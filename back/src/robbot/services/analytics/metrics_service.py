"""
Metrics Service

Service de alto nível para cálculo e cache de métricas.
Implementa caching inteligente no Redis com TTL configurável via settings.

Refatorado .1:
- TTL baseado em settings (não hardcoded)
- Validação de params em cache_key
- Cache em métodos agregadores
- Dependency injection para QueueManager
"""

import json
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from redis import Redis

from robbot.infra.persistence.repositories.analytics_repository import AnalyticsRepository
from robbot.config.settings import get_settings
from robbot.infra.redis.queue import RQQueueManager

logger = logging.getLogger(__name__)
settings = get_settings()


class MetricsService:
    """
    Service para cálculo e cache de métricas de negócio.

    Estratégia de cache:
    - Real-time data: settings.ANALYTICS_CACHE_TTL_REALTIME (30s)
    - Metrics: settings.ANALYTICS_CACHE_TTL_METRICS (15min)
    - Historical data: settings.ANALYTICS_CACHE_TTL_HISTORICAL (1h)
    - Reports: settings.ANALYTICS_CACHE_TTL_REPORTS (30min)

    Cache key pattern: metrics:{metric_name}:{period}:{user_id}:{hash_params}
    """

    def __init__(
        self,
        analytics_repo: AnalyticsRepository,
        redis_client: Redis,
        queue_manager: RQQueueManager | None = None,
    ):
        self.analytics = analytics_repo
        self.redis = redis_client
        self.queue_manager = queue_manager  # Injected dependency

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    def _generate_cache_key(
        self,
        metric_name: str,
        start_date: datetime,
        end_date: datetime,
        user_id: UUID | None = None,
        **kwargs,
    ) -> str:
        """
        Gera chave de cache consistente.

        IMPORTANTE: Todos os params que afetam o resultado DEVEM estar em kwargs.
        Exemplo: se method tem param 'limit', DEVE passar limit=value.

        Args:
            metric_name: Nome da métrica
            start_date: Data inicial
            end_date: Data final
            user_id: ID do usuário (opcional)
            **kwargs: Params extras que afetam resultado (limit, granularity, etc)

        Returns:
            Cache key string
        """
        period = f"{start_date.date()}_{end_date.date()}"
        user_part = f"user_{user_id}" if user_id else "global"

        # Hash dos parâmetros extras (sorted para consistência)
        if kwargs:
            # Ordenar e serializar params para garantir consistência
            params_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            return f"metrics:{metric_name}:{period}:{user_part}:{params_str}"

        return f"metrics:{metric_name}:{period}:{user_part}"

    async def _get_cached_or_compute(
        self,
        cache_key: str,
        ttl: int,
        compute_fn,
        *args,
        **kwargs,
    ) -> Any:
        """
        Pattern: Cache-aside

        1. Tenta buscar no cache
        2. Se cache miss, computa e salva
        3. Retorna resultado
        """
        import inspect

        try:
            # Tentar buscar do cache
            cached = self.redis.get(cache_key)
            if cached:
                logger.debug("Cache HIT: %s", cache_key)
                return json.loads(cached)

            logger.debug("Cache MISS: %s", cache_key)
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.warning("[WARNING] Redis error on GET %s: %s", cache_key, e)
            # Continua sem cache se Redis falhar

        # Computar métrica (suporta sync e async)
        if inspect.iscoroutinefunction(compute_fn):
            result = await compute_fn(*args, **kwargs)
        else:
            result = compute_fn(*args, **kwargs)

        # Salvar no cache
        try:
            self.redis.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str),  # default=str para datetime
            )
            logger.debug("Cache SET: %s (TTL=%ss)", cache_key, ttl)
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.warning("[WARNING] Redis error on SET %s: %s", cache_key, e)

        return result

    def _invalidate_cache_pattern(self, pattern: str):
        """Invalida todas as chaves que batem com o pattern"""
        try:
            # Scan para evitar KEYS (blocking)
            keys_to_delete = []
            for key in self.redis.scan_iter(match=pattern):
                keys_to_delete.append(key)

            if keys_to_delete:
                self.redis.delete(*keys_to_delete)
                logger.info("[INFO] Invalidated %s cache keys matching %s", len(keys_to_delete), pattern)
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Failed to invalidate cache pattern %s: %s", pattern, e)

    # =============================================================================
    # DASHBOARD METRICS
    # =============================================================================

    async def get_dashboard_summary(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Resumo executivo do dashboard.

        Cache: 5 minutos (dados em tempo real)

        Returns:
            {
                "period": {"start": "2024-12-01", "end": "2024-12-31"},
                "kpis": {
                    "total_leads": 150,
                    "converted_leads": 45,
                    "conversion_rate": 30.0,
                    "avg_response_time_seconds": 180.5,
                    "total_conversations": 200,
                    "active_conversations": 25,
                    "total_messages": 3500,
                    "avg_messages_per_conversation": 17.5
                }
            }
        """
        cache_key = self._generate_cache_key(
            "dashboard_summary",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_REALTIME,
            self.analytics.get_dashboard_summary,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "kpis": result,
        }

    # =============================================================================
    # CONVERSION ANALYTICS
    # =============================================================================

    async def get_conversion_rate(
        self,
        start_date: datetime,
        end_date: datetime,
        segment_by: str | None = None,
    ) -> dict[str, Any]:
        """
        Taxa de conversão global ou segmentada.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "conversion": {
                    "total_leads": 150,
                    "converted_leads": 45,
                    "conversion_rate": 30.0
                },
                "segments": [...]  # se segmentado
            }
        """
        cache_key = self._generate_cache_key(
            "conversion_rate",
            start_date,
            end_date,
            segment_by=segment_by,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_conversion_rate,
            start_date,
            end_date,
            segment_by,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "conversion": result if not segment_by else None,
            "segments": result.get("segments") if segment_by else None,
        }

    async def get_conversion_funnel(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Análise de funil de conversão com drop-off.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "funnel": {
                    "stages": [
                        {
                            "stage": "created",
                            "name": "Leads Criados",
                            "count": 150,
                            "percentage": 100.0,
                            "drop_off": 0.0
                        },
                        ...
                    ]
                }
            }
        """
        cache_key = self._generate_cache_key(
            "conversion_funnel",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_conversion_funnel,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "funnel": result,
        }

    async def get_time_to_conversion(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Estatísticas de tempo até conversão.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "time_stats": {
                    "avg_hours": 48.5,
                    "median_hours": 36.0,
                    "min_hours": 2.0,
                    "max_hours": 168.0,
                    "p95_hours": 120.0
                }
            }
        """
        cache_key = self._generate_cache_key(
            "time_to_conversion",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_time_to_conversion,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "time_stats": result,
        }

    # =============================================================================
    # PERFORMANCE ANALYTICS
    # =============================================================================

    async def get_human_response_time_stats(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Estatísticas de tempo de resposta.

        Cache: 5 minutos (dados operacionais)

        Returns:
            {
                "period": {...},
                "user_id": "uuid" | null,
                "response_time": {
                    "avg_seconds": 180.5,
                    "median_seconds": 120.0,
                    "p95_seconds": 600.0,
                    "p99_seconds": 1200.0,
                    "total_responses": 350
                }
            }
        """
        cache_key = self._generate_cache_key(
            "response_time_stats",
            start_date,
            end_date,
            user_id=user_id,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_REALTIME,
            self.analytics.get_human_response_time_stats,
            start_date,
            end_date,
            user_id,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "user_id": str(user_id) if user_id else None,
            "response_time": result,
        }

    async def get_message_volume(
        self,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "day",
    ) -> dict[str, Any]:
        """
        Volume de mensagens ao longo do tempo.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "granularity": "day",
                "data_points": [
                    {
                        "timestamp": "2024-12-18T00:00:00",
                        "incoming": 150,
                        "outgoing": 180,
                        "total": 330
                    },
                    ...
                ]
            }
        """
        cache_key = self._generate_cache_key(
            "message_volume",
            start_date,
            end_date,
            granularity=granularity,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_message_volume,
            start_date,
            end_date,
            granularity,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "granularity": granularity,
            "data_points": result,
        }

    # =============================================================================
    # BOT PERFORMANCE
    # =============================================================================

    async def get_bot_autonomy_rate(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Taxa de autonomia do bot.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "autonomy": {
                    "total_conversations": 200,
                    "bot_only": 120,
                    "with_handoff": 80,
                    "autonomy_rate": 60.0
                }
            }
        """
        cache_key = self._generate_cache_key(
            "bot_autonomy_rate",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_bot_autonomy_rate,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "autonomy": result,
        }

    # =============================================================================    # PERFORMANCE REPORTS ( - L1)
    # =============================================================================

    async def get_bot_response_time(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Estatísticas de tempo de resposta do bot via LLM latency.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "bot_response_time": {
                    "avg_ms": 1500.5,
                    "median_ms": 1200.0,
                    "p95_ms": 3000.0,
                    "p99_ms": 5000.0,
                    "min_ms": 500,
                    "max_ms": 8000,
                    "total_interactions": 1250
                }
            }
        """
        cache_key = self._generate_cache_key(
            "bot_response_time",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_bot_llm_latency_stats,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "bot_response_time": result,
        }

    async def get_handoff_rate(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Taxa de resolução automática vs handoff.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "handoff_stats": {
                    "total_conversations": 500,
                    "bot_resolved": 350,
                    "handoff_required": 150,
                    "handoff_rate": 30.0,
                    "auto_resolution_rate": 70.0
                }
            }
        """
        cache_key = self._generate_cache_key(
            "handoff_rate",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_handoff_rate_stats,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "handoff_stats": result,
        }

    async def get_peak_hours(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Horários de pico de atendimento.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "peak_hours": [
                    {"hour": 9, "message_count": 450, "conversation_count": 85},
                    ...
                ]
            }
        """
        cache_key = self._generate_cache_key(
            "peak_hours",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_peak_hours_stats,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "peak_hours": result,
        }

    async def get_conversations_by_status(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Distribuição de conversas por status.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "status_distribution": [
                    {"status": "ACTIVE_BOT", "count": 150, "percentage": 30.0},
                    ...
                ]
            }
        """
        cache_key = self._generate_cache_key(
            "conversations_by_status",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_conversations_by_status,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "status_distribution": result,
        }

    async def get_performance_report(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Relatório completo de performance de atendimento (L1).

        Combina todas as métricas de performance em um único response.

        Cache: 30 minutos (resultado agregado final)

        Returns:
            {
                "period": {...},
                "bot_response_time": {...},
                "handoff_stats": {...},
                "peak_hours": [...],
                "status_distribution": [...]
            }
        """
        # Cachear resultado agregado (não apenas componentes)
        cache_key = self._generate_cache_key(
            "performance_report",
            start_date,
            end_date,
        )

        async def _compute():
            bot_response = await self.get_bot_response_time(start_date, end_date)
            handoff = await self.get_handoff_rate(start_date, end_date)
            peak = await self.get_peak_hours(start_date, end_date)
            status_dist = await self.get_conversations_by_status(start_date, end_date)

            return {
                "period": {
                    "start": start_date.date().isoformat(),
                    "end": end_date.date().isoformat(),
                },
                "bot_response_time": bot_response["bot_response_time"],
                "handoff_stats": handoff["handoff_stats"],
                "peak_hours": peak["peak_hours"],
                "status_distribution": status_dist["status_distribution"],
            }

        return await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_REPORTS,
            _compute,
        )

    # =============================================================================
    # CONVERSION REPORTS EXTENDED ( - L2)
    # =============================================================================

    async def get_time_to_conversion_extended(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Estatísticas ESTENDIDAS de tempo até conversão (p75, p90).

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "time_stats": {
                    "avg_hours": 48.5,
                    "median_hours": 36.0,
                    "p75_hours": 60.0,
                    "p90_hours": 96.0,
                    "p95_hours": 120.0,
                    "min_hours": 2.0,
                    "max_hours": 168.0
                }
            }
        """
        cache_key = self._generate_cache_key(
            "time_to_conversion_extended",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_time_to_conversion_extended,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "time_stats": result,
        }

    async def get_conversion_by_source(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Taxa de conversão por origem/canal.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "sources": [
                    {
                        "source": "direct",
                        "total_leads": 120,
                        "converted_leads": 45,
                        "conversion_rate": 37.5
                    },
                    ...
                ]
            }
        """
        cache_key = self._generate_cache_key(
            "conversion_by_source",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_conversion_by_source,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "sources": result,
        }

    async def get_lost_leads_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Análise de leads perdidos.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "lost_leads": {
                    "total_lost": 45,
                    "lost_by_maturity_range": [...],
                    "avg_time_before_lost_hours": 36.5
                }
            }
        """
        cache_key = self._generate_cache_key(
            "lost_leads_analysis",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_lost_leads_analysis,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "lost_leads": result,
        }

    async def get_conversion_trend(
        self,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "day",
    ) -> dict[str, Any]:
        """
        Tendência temporal de conversão.

        Cache: 15 minutos

        Returns:
            {
                "period": {...},
                "granularity": "day",
                "trend": [
                    {
                        "period": "2026-01-01",
                        "total_leads": 25,
                        "converted_leads": 8,
                        "conversion_rate": 32.0
                    },
                    ...
                ]
            }
        """
        cache_key = self._generate_cache_key(
            "conversion_trend",
            start_date,
            end_date,
            granularity=granularity,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_conversion_trend,
            start_date,
            end_date,
            granularity,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "granularity": granularity,
            "trend": result,
        }

    async def get_conversion_report_extended(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Relatório COMPLETO de conversão ( - L2).

        Combina todas as métricas de conversão estendidas.

        Cache: 30 minutos (resultado agregado final)

        Returns:
            {
                "period": {...},
                "time_to_conversion": {...},
                "conversion_by_source": [...],
                "lost_leads": {...},
                "trend_daily": [...]
            }
        """
        # Cachear resultado agregado
        cache_key = self._generate_cache_key(
            "conversion_report_extended",
            start_date,
            end_date,
        )

        async def _compute():
            time_conv = await self.get_time_to_conversion_extended(start_date, end_date)
            by_source = await self.get_conversion_by_source(start_date, end_date)
            lost = await self.get_lost_leads_analysis(start_date, end_date)
            trend = await self.get_conversion_trend(start_date, end_date, granularity="day")

            return {
                "period": {
                    "start": start_date.date().isoformat(),
                    "end": end_date.date().isoformat(),
                },
                "time_to_conversion": time_conv["time_stats"],
                "conversion_by_source": by_source["sources"],
                "lost_leads": lost["lost_leads"],
                "trend_daily": trend["trend"],
            }

        return await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_REPORTS,
            _compute,
        )

    # =============================================================================
    # L3: CONVERSATION ANALYSIS METHODS
    # =============================================================================

    async def get_activity_heatmap(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Heatmap de atividade: mensagens por dia da semana e hora.

        Cache: 15 minutos (CACHE_TTL_METRICS)

        Returns:
            {
                "period": {...},
                "heatmap": [
                    {"day_of_week": 0, "hour": 9, "message_count": 150},
                    ...
                ]
            }
        """
        cache_key = self._generate_cache_key(
            "activity_heatmap",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_message_frequency_by_hour,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "heatmap": result,
        }

    async def get_keyword_frequency(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Palavras-chave mais frequentes nas mensagens INBOUND.

        Cache: 15 minutos (CACHE_TTL_METRICS)

        Returns:
            {
                "period": {...},
                "keywords": [
                    {"keyword": "agendamento", "count": 250},
                    ...
                ]
            }
        """
        cache_key = self._generate_cache_key(
            "keyword_frequency",
            start_date,
            end_date,
            limit=limit,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_keyword_frequency,
            start_date,
            end_date,
            limit,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "keywords": result,
        }

    async def get_sentiment_distribution(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Distribuição de sentimento nas mensagens INBOUND.

        Cache: 15 minutos (CACHE_TTL_METRICS)

        Returns:
            {
                "period": {...},
                "sentiment": {
                    "positive": 350,
                    "negative": 80,
                    "neutral": 570,
                    "total_messages": 1000
                }
            }
        """
        cache_key = self._generate_cache_key(
            "sentiment_distribution",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_message_sentiment_distribution,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "sentiment": result,
        }

    async def get_topic_distribution(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Topics mais discutidos nas mensagens INBOUND.

        Cache: 15 minutos (CACHE_TTL_METRICS)

        Returns:
            {
                "period": {...},
                "topics": [
                    {"topic": "Agendamento", "count": 250, "percentage": 35.0},
                    ...
                ]
            }
        """
        cache_key = self._generate_cache_key(
            "topic_distribution",
            start_date,
            end_date,
        )

        result = await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_METRICS,
            self.analytics.get_conversation_topics,
            start_date,
            end_date,
        )

        return {
            "period": {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            },
            "topics": result,
        }

    async def get_conversation_analysis_report(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Relatório COMPLETO de análise de conversas ( - L3).

        Combina todas as métricas de análise textual.

        Cache: 30 minutos (resultado agregado final)

        Returns:
            {
                "period": {...},
                "activity_heatmap": [...],
                "top_keywords": [...],
                "sentiment_distribution": {...},
                "topic_distribution": [...]
            }
        """
        # Cachear resultado agregado
        cache_key = self._generate_cache_key(
            "conversation_analysis_report",
            start_date,
            end_date,
        )

        async def _compute():
            heatmap = await self.get_activity_heatmap(start_date, end_date)
            keywords = await self.get_keyword_frequency(start_date, end_date, limit=50)
            sentiment = await self.get_sentiment_distribution(start_date, end_date)
            topics = await self.get_topic_distribution(start_date, end_date)

            return {
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "activity_heatmap": heatmap["heatmap"],
                "top_keywords": keywords["keywords"],
                "sentiment_distribution": sentiment["sentiment"],
                "topic_distribution": topics["topics"],
            }

        return await self._get_cached_or_compute(
            cache_key,
            settings.ANALYTICS_CACHE_TTL_REPORTS,
            _compute,
        )

    # =============================================================================
    # L4: REAL-TIME DASHBOARD METHODS
    # =============================================================================

    async def get_realtime_dashboard(self) -> dict[str, Any]:
        """
        Dashboard completo em tempo real.

        Cache: 30 segundos (CACHE_TTL_REALTIME = 30)

        Returns:
            {
                "timestamp": "2026-01-08T14:35:00",
                "summary": {...},
                "active_conversations": [...],
                "queue_stats": {...},
                "performance_alerts": {...}
            }
        """
        from datetime import datetime

        from robbot.infra.redis.queue import get_queue_manager

        cache_key = "metrics:realtime_dashboard"

        async def _compute():
            # 1. Sumário em tempo real
            summary = self.analytics.get_realtime_summary()

            # 2. Conversas ativas
            active_conversations = self.analytics.get_active_conversations()

            # 3. Estatísticas das filas via QueueManager
            queue_manager = get_queue_manager()
            queue_stats = queue_manager.get_queue_stats()

            # 4. Alertas de performance
            performance_alerts = self.analytics.get_performance_alerts(
                latency_threshold_ms=5000,
                error_rate_threshold=5.0,
            )

            return {
                "timestamp": datetime.now().isoformat(),
                "summary": summary,
                "active_conversations": active_conversations,
                "queue_stats": queue_stats,
                "performance_alerts": performance_alerts,
            }

        # Cache de 30 segundos (near-real-time)
        cache_ttl_realtime = 30
        return await self._get_cached_or_compute(
            cache_key,
            cache_ttl_realtime,
            _compute,
        )

    def get_active_conversations_live(self) -> dict[str, Any]:
        """
        Conversas ativas sem cache (para WebSocket).

        Returns:
            {
                "timestamp": "2026-01-08T14:35:00",
                "active_conversations": [...]
            }
        """
        from datetime import datetime

        return {
            "timestamp": datetime.now().isoformat(),
            "active_conversations": self.analytics.get_active_conversations(),
        }

    # =============================================================================    # CACHE MANAGEMENT
    # =============================================================================

    def invalidate_all_metrics(self):
        """Invalida todo o cache de métricas (usar com cautela)"""
        self._invalidate_cache_pattern("metrics:*")

    def invalidate_metric(self, metric_name: str):
        """Invalida cache de uma métrica específica"""
        self._invalidate_cache_pattern(f"metrics:{metric_name}:*")

    def get_cache_stats(self) -> dict[str, Any]:
        """Estatísticas do cache Redis"""
        try:
            info = self.redis.info("stats")
            return {
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0)
                    / (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1))
                    * 100,
                    2,
                ),
            }
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Failed to get cache stats: %s", e)
            return {}

