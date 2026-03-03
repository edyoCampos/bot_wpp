"""
Metrics Schemas

Pydantic schemas para validação e serialização de métricas.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# COMMON SCHEMAS
# =============================================================================


class PeriodSchema(BaseModel):
    """Período de análise"""

    start: date = Field(..., description="Data inicial")
    end: date = Field(..., description="Data final")


class BasePercentileSchema(BaseModel):
    """Schema base para métricas com percentis de tempo"""

    avg_hours: float = Field(..., ge=0, description="Média (horas)")
    median_hours: float = Field(..., ge=0, description="Mediana (horas)")
    p95_hours: float = Field(..., ge=0, description="95º percentil (horas)")
    min_hours: float = Field(..., ge=0, description="Mínimo (horas)")
    max_hours: float = Field(..., ge=0, description="Máximo (horas)")


# =============================================================================
# DASHBOARD SCHEMAS
# =============================================================================


class DashboardKPIsSchema(BaseModel):
    """KPIs principais do dashboard"""

    total_leads: int = Field(..., ge=0, description="Total de leads no período")
    converted_leads: int = Field(..., ge=0, description="Leads convertidos")
    conversion_rate: float = Field(..., ge=0, le=100, description="Taxa de conversão (%)")
    avg_response_time_seconds: float = Field(..., ge=0, description="Tempo médio de resposta (segundos)")
    total_conversations: int = Field(..., ge=0, description="Total de conversas")
    active_conversations: int = Field(..., ge=0, description="Conversas ativas")
    total_messages: int = Field(..., ge=0, description="Total de mensagens")
    avg_messages_per_conversation: float = Field(..., ge=0, description="Média de mensagens por conversa")


class DashboardSummaryResponse(BaseModel):
    """Response do dashboard summary"""

    period: PeriodSchema
    kpis: DashboardKPIsSchema

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period": {"start": "2024-12-01", "end": "2024-12-31"},
                "kpis": {
                    "total_leads": 150,
                    "converted_leads": 45,
                    "conversion_rate": 30.0,
                    "avg_response_time_seconds": 180.5,
                    "total_conversations": 200,
                    "active_conversations": 25,
                    "total_messages": 3500,
                    "avg_messages_per_conversation": 17.5,
                },
            }
        }
    )


# =============================================================================
# CONVERSION ANALYTICS SCHEMAS
# =============================================================================


class ConversionMetricsSchema(BaseModel):
    """Métricas de conversão"""

    total_leads: int = Field(..., ge=0)
    converted_leads: int = Field(..., ge=0)
    conversion_rate: float = Field(..., ge=0, le=100, description="Taxa de conversão (%)")


class ConversionSegmentSchema(ConversionMetricsSchema):
    """Segmento de conversão"""

    segment_name: str
    segment_id: str | None = None


class ConversionRateResponse(BaseModel):
    """Response da taxa de conversão"""

    period: PeriodSchema
    conversion: ConversionMetricsSchema | None = None
    segments: list[ConversionSegmentSchema] | None = None


class FunnelStageSchema(BaseModel):
    """Etapa do funil de conversão"""

    stage: str = Field(..., description="Identificador da etapa")
    name: str = Field(..., description="Nome legível da etapa")
    count: int = Field(..., ge=0, description="Quantidade nesta etapa")
    percentage: float = Field(..., ge=0, le=100, description="% do total inicial")
    drop_off: float = Field(..., ge=0, le=100, description="% de abandono da etapa anterior")


class ConversionFunnelResponse(BaseModel):
    """Response do funil de conversão"""

    period: PeriodSchema
    funnel: dict[str, list[FunnelStageSchema]] = Field(..., description="Stages do funil")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period": {"start": "2024-12-01", "end": "2024-12-31"},
                "funnel": {
                    "stages": [
                        {
                            "stage": "created",
                            "name": "Leads Criados",
                            "count": 150,
                            "percentage": 100.0,
                            "drop_off": 0.0,
                        },
                        {
                            "stage": "engaged",
                            "name": "Engajados (responderam)",
                            "count": 120,
                            "percentage": 80.0,
                            "drop_off": 20.0,
                        },
                    ]
                },
            }
        }
    )


class TimeToConversionStatsSchema(BasePercentileSchema):
    """Estatísticas de tempo até conversão"""

    pass


class TimeToConversionResponse(BaseModel):
    """Response do tempo até conversão"""

    period: PeriodSchema
    time_stats: TimeToConversionStatsSchema


# =============================================================================# CONVERSION REPORTS EXTENDED SCHEMAS ( - L2)
# =============================================================================


class TimeToConversionExtendedStatsSchema(BasePercentileSchema):
    """Estatísticas ESTENDIDAS de tempo até conversão (com p75, p90)"""

    p75_hours: float = Field(..., ge=0, description="75º percentil (horas)")
    p90_hours: float = Field(..., ge=0, description="90º percentil (horas)")


class TimeToConversionExtendedResponse(BaseModel):
    """Response estendido do tempo até conversão"""

    period: PeriodSchema
    time_stats: TimeToConversionExtendedStatsSchema


class ConversionBySourceSchema(BaseModel):
    """Conversão por origem/canal"""

    source: str = Field(..., description="Origem do lead (direct, group)")
    total_leads: int = Field(..., ge=0, description="Total de leads desta origem")
    converted_leads: int = Field(..., ge=0, description="Leads convertidos")
    conversion_rate: float = Field(..., ge=0, le=100, description="Taxa de conversão (%)")


class ConversionBySourceResponse(BaseModel):
    """Response de conversão por origem"""

    period: PeriodSchema
    sources: list[ConversionBySourceSchema]


class LostLeadsByMaturitySchema(BaseModel):
    """Leads perdidos por faixa de maturidade"""

    maturity_range: str = Field(..., description="Faixa de maturity score")
    count: int = Field(..., ge=0, description="Quantidade de leads perdidos")
    percentage: float = Field(..., ge=0, le=100, description="Percentual do total (%)")


class LostLeadsAnalysisSchema(BaseModel):
    """Análise de leads perdidos"""

    total_lost: int = Field(..., ge=0, description="Total de leads perdidos")
    lost_by_maturity_range: list[LostLeadsByMaturitySchema]
    avg_time_before_lost_hours: float = Field(..., ge=0, description="Tempo médio até perda (horas)")


class LostLeadsAnalysisResponse(BaseModel):
    """Response da análise de leads perdidos"""

    period: PeriodSchema
    lost_leads: LostLeadsAnalysisSchema


class ConversionTrendDataPointSchema(BaseModel):
    """Ponto de dados de tendência de conversão"""

    period: str = Field(..., description="Data do período (ISO 8601)")
    total_leads: int = Field(..., ge=0, description="Total de leads no período")
    converted_leads: int = Field(..., ge=0, description="Leads convertidos")
    conversion_rate: float = Field(..., ge=0, le=100, description="Taxa de conversão (%)")


class ConversionTrendResponse(BaseModel):
    """Response da tendência de conversão"""

    period: PeriodSchema
    granularity: str = Field(..., description="day, week ou month")
    trend: list[ConversionTrendDataPointSchema]


class ConversionReportExtendedSchema(BaseModel):
    """Relatório COMPLETO de conversão ( - L2)"""

    period: PeriodSchema
    time_to_conversion: TimeToConversionExtendedStatsSchema
    conversion_by_source: list[ConversionBySourceSchema]
    lost_leads: LostLeadsAnalysisSchema
    trend_daily: list[ConversionTrendDataPointSchema]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period": {"start": "2026-01-01", "end": "2026-01-31"},
                "time_to_conversion": {
                    "avg_hours": 48.5,
                    "median_hours": 36.0,
                    "p75_hours": 60.0,
                    "p90_hours": 96.0,
                    "p95_hours": 120.0,
                    "min_hours": 2.0,
                    "max_hours": 168.0,
                },
                "conversion_by_source": [
                    {"source": "direct", "total_leads": 120, "converted_leads": 45, "conversion_rate": 37.5},
                    {"source": "group", "total_leads": 30, "converted_leads": 5, "conversion_rate": 16.67},
                ],
                "lost_leads": {
                    "total_lost": 45,
                    "lost_by_maturity_range": [
                        {"maturity_range": "0-19 (muito baixo)", "count": 15, "percentage": 33.33}
                    ],
                    "avg_time_before_lost_hours": 36.5,
                },
                "trend_daily": [
                    {"period": "2026-01-01", "total_leads": 25, "converted_leads": 8, "conversion_rate": 32.0}
                ],
            }
        }
    )


# =============================================================================# PERFORMANCE ANALYTICS SCHEMAS
# =============================================================================


class ResponseTimeStatsSchema(BaseModel):
    """Estatísticas de tempo de resposta"""

    avg_seconds: float = Field(..., ge=0, description="Média (segundos)")
    median_seconds: float = Field(..., ge=0, description="Mediana (segundos)")
    p95_seconds: float = Field(..., ge=0, description="95º percentil (segundos)")
    p99_seconds: float = Field(..., ge=0, description="99º percentil (segundos)")
    total_responses: int = Field(..., ge=0, description="Total de respostas analisadas")


class ResponseTimeResponse(BaseModel):
    """Response do tempo de resposta"""

    period: PeriodSchema
    user_id: str | None = Field(None, description="UUID do usuário (null = global)")
    response_time: ResponseTimeStatsSchema


class MessageVolumeDataPointSchema(BaseModel):
    """Ponto de dados do volume de mensagens"""

    timestamp: str = Field(..., description="ISO 8601 timestamp")
    incoming: int = Field(..., ge=0, description="Mensagens recebidas")
    outgoing: int = Field(..., ge=0, description="Mensagens enviadas")
    total: int = Field(..., ge=0, description="Total de mensagens")


class MessageVolumeResponse(BaseModel):
    """Response do volume de mensagens"""

    period: PeriodSchema
    granularity: str = Field(..., description="hour, day, ou week")
    data_points: list[MessageVolumeDataPointSchema]


# =============================================================================
# BOT PERFORMANCE SCHEMAS
# =============================================================================


class BotAutonomyMetricsSchema(BaseModel):
    """Métricas de autonomia do bot"""

    total_conversations: int = Field(..., ge=0)
    bot_only: int = Field(..., ge=0, description="Conversas resolvidas sem humano")
    with_handoff: int = Field(..., ge=0, description="Conversas transferidas para humano")
    autonomy_rate: float = Field(..., ge=0, le=100, description="Taxa de autonomia (%)")


class BotAutonomyResponse(BaseModel):
    """Response da autonomia do bot"""

    period: PeriodSchema
    autonomy: BotAutonomyMetricsSchema


# =============================================================================
# CACHE MANAGEMENT SCHEMAS
# =============================================================================


class CacheStatsSchema(BaseModel):
    """Estatísticas do cache Redis"""

    keyspace_hits: int = Field(..., ge=0)
    keyspace_misses: int = Field(..., ge=0)
    hit_rate: float = Field(..., ge=0, le=100, description="Taxa de acerto do cache (%)")


# =============================================================================
# FORECAST SCHEMAS (FUTURE)
# =============================================================================


class ForecastDataPointSchema(BaseModel):
    """Ponto de previsão"""

    date: date
    predicted_volume: int = Field(..., ge=0)
    lower_bound: int = Field(..., ge=0)
    upper_bound: int = Field(..., ge=0)


class DemandForecastResponse(BaseModel):
    """Response da previsão de demanda"""

    forecast: list[ForecastDataPointSchema]
    status: str = Field(default="not_implemented")
    message: str | None = None


# =============================================================================
# PERFORMANCE REPORTS SCHEMAS ( - L1)
# =============================================================================


class BotResponseTimeStatsSchema(BaseModel):
    """Estatísticas de tempo de resposta do bot"""

    avg_ms: float = Field(..., ge=0, description="Média (ms)")
    median_ms: float = Field(..., ge=0, description="Mediana (ms)")
    p95_ms: float = Field(..., ge=0, description="95º percentil (ms)")
    p99_ms: float = Field(..., ge=0, description="99º percentil (ms)")
    min_ms: int = Field(..., ge=0, description="Mínimo (ms)")
    max_ms: int = Field(..., ge=0, description="Máximo (ms)")
    total_interactions: int = Field(..., ge=0, description="Total de interações LLM")


class BotResponseTimeResponse(BaseModel):
    """Response do tempo de resposta do bot"""

    period: PeriodSchema
    bot_response_time: BotResponseTimeStatsSchema


class HandoffRateStatsSchema(BaseModel):
    """Estatísticas de taxa de handoff"""

    total_conversations: int = Field(..., ge=0, description="Total de conversas")
    bot_resolved: int = Field(..., ge=0, description="Resolvidas pelo bot")
    handoff_required: int = Field(..., ge=0, description="Handoff para humano")
    handoff_rate: float = Field(..., ge=0, le=100, description="Taxa de handoff (%)")
    auto_resolution_rate: float = Field(..., ge=0, le=100, description="Taxa de resolução automática (%)")


class HandoffRateResponse(BaseModel):
    """Response da taxa de handoff"""

    period: PeriodSchema
    handoff_stats: HandoffRateStatsSchema


class PeakHourDataPointSchema(BaseModel):
    """Ponto de dados de horário de pico"""

    hour: int = Field(..., ge=0, le=23, description="Hora do dia (0-23)")
    message_count: int = Field(..., ge=0, description="Total de mensagens neste horário")
    conversation_count: int = Field(..., ge=0, description="Conversas ativas neste horário")


class PeakHoursResponse(BaseModel):
    """Response dos horários de pico"""

    period: PeriodSchema
    peak_hours: list[PeakHourDataPointSchema]


class ConversationStatusDistributionSchema(BaseModel):
    """Distribuição de conversas por status"""

    status: str = Field(..., description="Status da conversa")
    count: int = Field(..., ge=0, description="Quantidade")
    percentage: float = Field(..., ge=0, le=100, description="Percentual do total (%)")


class ConversationsByStatusResponse(BaseModel):
    """Response das conversas por status"""

    period: PeriodSchema
    status_distribution: list[ConversationStatusDistributionSchema]


class PerformanceReportSchema(BaseModel):
    """Relatório completo de performance de atendimento (L1)"""

    period: PeriodSchema
    bot_response_time: BotResponseTimeStatsSchema
    handoff_stats: HandoffRateStatsSchema
    peak_hours: list[PeakHourDataPointSchema]
    status_distribution: list[ConversationStatusDistributionSchema]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period": {"start": "2024-12-01", "end": "2024-12-31"},
                "bot_response_time": {
                    "avg_ms": 1500.5,
                    "median_ms": 1200.0,
                    "p95_ms": 3000.0,
                    "p99_ms": 5000.0,
                    "min_ms": 500,
                    "max_ms": 8000,
                    "total_interactions": 1250,
                },
                "handoff_stats": {
                    "total_conversations": 500,
                    "bot_resolved": 350,
                    "handoff_required": 150,
                    "handoff_rate": 30.0,
                    "auto_resolution_rate": 70.0,
                },
                "peak_hours": [
                    {"hour": 9, "message_count": 450, "conversation_count": 85},
                    {"hour": 14, "message_count": 520, "conversation_count": 95},
                ],
                "status_distribution": [
                    {"status": "ACTIVE_BOT", "count": 150, "percentage": 30.0},
                    {"status": "COMPLETED", "count": 200, "percentage": 40.0},
                ],
            }
        }
    )


# =====================================================================
# L3: Schemas de Análise de Conversas
# =====================================================================


class ActivityHeatmapDataPointSchema(BaseModel):
    """Ponto de dados do heatmap de atividade."""

    day_of_week: int = Field(..., ge=0, le=6, description="Dia da semana (0=domingo, 6=sábado)")
    hour: int = Field(..., ge=0, le=23, description="Hora do dia (0-23)")
    message_count: int = Field(..., ge=0, description="Quantidade de mensagens")

    model_config = ConfigDict(json_schema_extra={"example": {"day_of_week": 1, "hour": 14, "message_count": 85}})


class KeywordFrequencySchema(BaseModel):
    """Frequência de palavra-chave."""

    keyword: str = Field(..., min_length=1, description="Palavra-chave")
    count: int = Field(..., ge=1, description="Quantidade de ocorrências")

    model_config = ConfigDict(json_schema_extra={"example": {"keyword": "agendamento", "count": 250}})


class SentimentDistributionSchema(BaseModel):
    """Distribuição de sentimentos nas mensagens."""

    positive: int = Field(..., ge=0, description="Mensagens positivas")
    negative: int = Field(..., ge=0, description="Mensagens negativas")
    neutral: int = Field(..., ge=0, description="Mensagens neutras")
    total_messages: int = Field(..., ge=0, description="Total de mensagens analisadas")

    model_config = ConfigDict(
        json_schema_extra={"example": {"positive": 350, "negative": 80, "neutral": 570, "total_messages": 1000}}
    )


class TopicDistributionSchema(BaseModel):
    """Distribuição de topics discutidos."""

    topic: str = Field(..., min_length=1, description="Nome do topic")
    count: int = Field(..., ge=0, description="Quantidade de mensagens")
    percentage: float = Field(..., ge=0, le=100, description="Percentual do total")

    model_config = ConfigDict(json_schema_extra={"example": {"topic": "Agendamento", "count": 250, "percentage": 35.0}})


class ConversationAnalysisReportSchema(BaseModel):
    """Relatório agregado de análise de conversas."""

    period_start: str = Field(..., description="Início do período (ISO 8601)")
    period_end: str = Field(..., description="Fim do período (ISO 8601)")
    activity_heatmap: list[ActivityHeatmapDataPointSchema] = Field(..., description="Heatmap de atividade por dia/hora")
    top_keywords: list[KeywordFrequencySchema] = Field(..., description="Palavras-chave mais frequentes")
    sentiment_distribution: SentimentDistributionSchema = Field(..., description="Distribuição de sentimentos")
    topic_distribution: list[TopicDistributionSchema] = Field(..., description="Distribuição de topics")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period_start": "2026-01-01T00:00:00",
                "period_end": "2026-01-31T23:59:59",
                "activity_heatmap": [
                    {"day_of_week": 1, "hour": 9, "message_count": 120},
                    {"day_of_week": 1, "hour": 14, "message_count": 85},
                ],
                "top_keywords": [{"keyword": "agendamento", "count": 250}, {"keyword": "preço", "count": 180}],
                "sentiment_distribution": {"positive": 350, "negative": 80, "neutral": 570, "total_messages": 1000},
                "topic_distribution": [
                    {"topic": "Agendamento", "count": 250, "percentage": 35.0},
                    {"topic": "Preços", "count": 150, "percentage": 21.0},
                ],
            }
        }
    )


# =====================================================================
# L4: Schemas de Real-time Dashboard
# =====================================================================


class ActiveConversationSchema(BaseModel):
    """Conversa ativa no momento."""

    id: str = Field(..., description="ID da conversa")
    chat_id: str = Field(..., description="WhatsApp chat ID")
    status: str = Field(..., description="Status atual")
    last_message_at: str = Field(..., description="Timestamp da última mensagem")
    minutes_since_last_message: float = Field(..., description="Minutos desde última mensagem")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "uuid-123",
                "chat_id": "5511999999999@c.us",
                "status": "ACTIVE_BOT",
                "last_message_at": "2026-01-08T14:35:00",
                "minutes_since_last_message": 2.5,
            }
        }
    )


class QueueStatsSchema(BaseModel):
    """Estatísticas de uma fila RQ."""

    job_count: int = Field(..., ge=0, description="Quantidade de jobs na fila")
    worker_count: int = Field(..., ge=0, description="Quantidade de workers ativos")
    failed_count: int = Field(..., ge=0, description="Quantidade de jobs falhados")

    model_config = ConfigDict(json_schema_extra={"example": {"job_count": 25, "worker_count": 3, "failed_count": 2}})


class PerformanceAlertsSchema(BaseModel):
    """Alertas de performance."""

    high_latency_count: int = Field(..., ge=0, description="Jobs com latência alta")
    high_latency_avg_ms: float = Field(..., ge=0, description="Média de latência dos jobs lentos")
    error_rate: float = Field(..., ge=0, le=100, description="Taxa de erro em %")
    total_interactions_last_hour: int = Field(..., ge=0, description="Total de interações na última hora")
    failed_interactions: int = Field(..., ge=0, description="Interações falhadas")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "high_latency_count": 10,
                "high_latency_avg_ms": 6500.0,
                "error_rate": 7.5,
                "total_interactions_last_hour": 500,
                "failed_interactions": 38,
            }
        }
    )


class RealtimeSummarySchema(BaseModel):
    """Sumário de métricas em tempo real."""

    active_conversations: int = Field(..., ge=0, description="Conversas ativas (últimos 5min)")
    messages_per_minute: float = Field(..., ge=0, description="Taxa de mensagens por minuto")
    avg_response_time_ms: float = Field(..., ge=0, description="Tempo médio de resposta")
    bot_resolution_rate: float = Field(..., ge=0, le=100, description="Taxa de resolução do bot em %")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "active_conversations": 15,
                "messages_per_minute": 8.2,
                "avg_response_time_ms": 1500.0,
                "bot_resolution_rate": 85.0,
            }
        }
    )


class RealtimeDashboardSchema(BaseModel):
    """Dashboard completo em tempo real."""

    timestamp: str = Field(..., description="Timestamp da coleta (ISO 8601)")
    summary: RealtimeSummarySchema = Field(..., description="Sumário de métricas")
    active_conversations: list[ActiveConversationSchema] = Field(..., description="Conversas ativas")
    queue_stats: dict[str, QueueStatsSchema] = Field(..., description="Estatísticas das filas")
    performance_alerts: PerformanceAlertsSchema = Field(..., description="Alertas de performance")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestamp": "2026-01-08T14:35:00",
                "summary": {
                    "active_conversations": 15,
                    "messages_per_minute": 8.2,
                    "avg_response_time_ms": 1500.0,
                    "bot_resolution_rate": 85.0,
                },
                "active_conversations": [
                    {
                        "id": "uuid-123",
                        "chat_id": "5511999999999@c.us",
                        "status": "ACTIVE_BOT",
                        "last_message_at": "2026-01-08T14:35:00",
                        "minutes_since_last_message": 2.5,
                    }
                ],
                "queue_stats": {
                    "messages": {"job_count": 25, "worker_count": 3, "failed_count": 2},
                    "ai": {"job_count": 10, "worker_count": 2, "failed_count": 0},
                },
                "performance_alerts": {
                    "high_latency_count": 10,
                    "high_latency_avg_ms": 6500.0,
                    "error_rate": 7.5,
                    "total_interactions_last_hour": 500,
                    "failed_interactions": 38,
                },
            }
        }
    )
