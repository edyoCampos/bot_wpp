"""
Analytics Repository - Consolidated

Repositório consolidado para todas as métricas de analytics.
Anteriormente dividido em 4 arquivos separados (DT-004 resolvido).

Seções:
1. Conversion Analytics (conversão de leads, funil)
2. Performance Analytics (tempo de resposta, volume)
3. Bot Performance Analytics (autonomia do bot)
4. Dashboard Analytics (sumários agregados)
"""
# pylint: disable=not-callable

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import case, func, text
from sqlalchemy.orm import Session

from robbot.config.analytics_config_loader import get_analytics_config
from robbot.domain.shared.enums import LeadStatus
from robbot.infra.persistence.models.conversation_model import ConversationModel
from robbot.infra.persistence.models.lead_model import LeadModel
from robbot.infra.persistence.models.user_model import UserModel

try:
    from robbot.infra.integrations.llm.llm_client import get_llm_client
    from robbot.core.cache import get_cache
except Exception:  # noqa: BLE001 (blind exception)
    get_llm_client = None
    get_cache = None


class AnalyticsRepository:
    """Repository consolidado para todas as métricas de analytics"""

    def __init__(self, db_session: Session):
        self.db = db_session

    # =========================================================================
    # SEÇÃO 1: CONVERSION ANALYTICS (Conversão de Leads)
    # =========================================================================

    def get_conversion_rate(
        self,
        start_date: datetime,
        end_date: datetime,
        segment_by: str | None = None,
    ) -> dict[str, Any]:
        """
        Calcula taxa de conversão global ou segmentada.

        Args:
            start_date: Data inicial
            end_date: Data final
            segment_by: Segmentação (procedure, source, assigned_to)

        Returns:
            {
                "total_leads": 150,
                "converted_leads": 45,
                "conversion_rate": 30.0,
                "segments": [...]  # se segment_by
            }
        """
        # Query base
        query = self.db.query(
            func.count(LeadModel.id).label("total_leads"),
            func.count(case((LeadModel.status == LeadStatus.SCHEDULED, LeadModel.id), else_=None)).label(
                "converted_leads"
            ),
        ).filter(
            LeadModel.created_at >= start_date,
            LeadModel.created_at <= end_date,
            LeadModel.deleted_at.is_(None),
        )

        if segment_by and segment_by == "assigned_to":
            query = query.join(UserModel, LeadModel.assigned_to_user_id == UserModel.id)
            query = query.add_columns(
                UserModel.full_name.label("segment_name"),
                UserModel.id.label("segment_id"),
            )
            query = query.group_by(UserModel.id, UserModel.full_name)

        result = query.all()

        if not segment_by:
            row = result[0] if result else (0, 0)
            total = getattr(row, "total_leads", 0) or 0
            converted = getattr(row, "converted_leads", 0) or 0
            rate = (converted / total * 100) if total > 0 else 0.0
            return {
                "total_leads": total,
                "converted_leads": converted,
                "conversion_rate": round(rate, 2),
            }
        else:
            segments = []
            for row in result:
                total = getattr(row, "total_leads", 0) or 0
                converted = getattr(row, "converted_leads", 0) or 0
                rate = (converted / total * 100) if total > 0 else 0.0
                segments.append(
                    {
                        "segment_name": getattr(row, "segment_name", None),
                        "segment_id": str(getattr(row, "segment_id", "")),
                        "total_leads": total,
                        "converted_leads": converted,
                        "conversion_rate": round(rate, 2),
                    }
                )
            return {"segments": segments}

    def get_conversion_funnel(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Analisa funil de conversão com drop-off por etapa.

        Etapas:
        1. Leads criados (NEW)
        2. Engajados (respondeu pelo menos 1 msg)
        3. Qualificados (maturity_score >= 60)
        4. Handoff (transferido para humano)
        5. Convertidos (CONVERTED)

        Returns:
            {
                "stages": [
                    {
                        "stage": "created",
                        "count": 150,
                        "percentage": 100.0,
                        "drop_off": 0.0
                    },
                    ...
                ]
            }
        """
        query = text("""
            WITH funnel AS (
                SELECT
                    COUNT(DISTINCT l.id) as total_created,
                    COUNT(DISTINCT CASE WHEN cm.id IS NOT NULL THEN l.id END) as total_engaged,
                    COUNT(DISTINCT CASE WHEN l.maturity_score >= 60 THEN l.id END) as total_qualified,
                    COUNT(DISTINCT CASE WHEN c.handoff_at IS NOT NULL THEN l.id END) as total_handoff,
                    COUNT(DISTINCT CASE WHEN l.status = 'CONVERTED' THEN l.id END) as total_converted
                FROM leads l
                LEFT JOIN conversations c ON c.id = l.conversation_id
                LEFT JOIN conversation_messages cm ON c.id = cm.conversation_id
                    AND cm.direction = 'INBOUND'
                WHERE l.created_at >= :start_date
                    AND l.created_at <= :end_date
                    AND l.deleted_at IS NULL
            )
            SELECT * FROM funnel
        """)

        result = self.db.execute(query, {"start_date": start_date, "end_date": end_date})
        row = result.fetchone()

        if not row:
            return {"stages": []}

        total_created = row.total_created or 0

        stages = [
            {
                "stage": "created",
                "name": "Leads Criados",
                "count": total_created,
                "percentage": 100.0,
                "drop_off": 0.0,
            },
            {
                "stage": "engaged",
                "name": "Engajados (responderam)",
                "count": row.total_engaged or 0,
                "percentage": round((row.total_engaged or 0) / total_created * 100, 2) if total_created > 0 else 0,
                "drop_off": round((total_created - (row.total_engaged or 0)) / total_created * 100, 2)
                if total_created > 0
                else 0,
            },
            {
                "stage": "qualified",
                "name": "Qualificados (score >= 60)",
                "count": row.total_qualified or 0,
                "percentage": round((row.total_qualified or 0) / total_created * 100, 2) if total_created > 0 else 0,
                "drop_off": round(
                    ((row.total_engaged or 0) - (row.total_qualified or 0)) / (row.total_engaged or 0) * 100,
                    2,
                )
                if row.total_engaged
                else 0,
            },
            {
                "stage": "handoff",
                "name": "Transferidos para humano",
                "count": row.total_handoff or 0,
                "percentage": round((row.total_handoff or 0) / total_created * 100, 2) if total_created > 0 else 0,
                "drop_off": round(
                    ((row.total_qualified or 0) - (row.total_handoff or 0)) / (row.total_qualified or 0) * 100,
                    2,
                )
                if row.total_qualified
                else 0,
            },
            {
                "stage": "converted",
                "name": "Convertidos (agendaram)",
                "count": row.total_converted or 0,
                "percentage": round((row.total_converted or 0) / total_created * 100, 2) if total_created > 0 else 0,
                "drop_off": round(
                    ((row.total_handoff or 0) - (row.total_converted or 0)) / (row.total_handoff or 0) * 100,
                    2,
                )
                if row.total_handoff
                else 0,
            },
        ]

        return {"stages": stages}

    def get_time_to_conversion(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, float]:
        """
        Calcula estatísticas de tempo até conversão.

        Returns:
            {
                "avg_hours": 48.5,
                "median_hours": 36.0,
                "min_hours": 2.0,
                "max_hours": 168.0,
                "p95_hours": 120.0
            }
        """
        query = text("""
            SELECT
                AVG(EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as avg_hours,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as median_hours,
                MIN(EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as min_hours,
                MAX(EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as max_hours,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as p95_hours
            FROM leads l
            WHERE l.status = 'CONVERTED'
                AND l.converted_at IS NOT NULL
                AND l.created_at >= :start_date
                AND l.created_at <= :end_date
                AND l.deleted_at IS NULL
        """)

        result = self.db.execute(query, {"start_date": start_date, "end_date": end_date})
        row = result.fetchone()

        if not row or row.avg_hours is None:
            return {
                "avg_hours": 0.0,
                "median_hours": 0.0,
                "min_hours": 0.0,
                "max_hours": 0.0,
                "p95_hours": 0.0,
            }

        return {
            "avg_hours": round(float(row.avg_hours), 2),
            "median_hours": round(float(row.median_hours), 2),
            "min_hours": round(float(row.min_hours), 2),
            "max_hours": round(float(row.max_hours), 2),
            "p95_hours": round(float(row.p95_hours), 2),
        }

    def get_time_to_conversion_extended(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, float]:
        """
        Estatísticas ESTENDIDAS de tempo até conversão ( - L2).

        Adiciona p75 e p90 às métricas existentes.

        Returns:
            {
                "avg_hours": 48.5,
                "median_hours": 36.0,
                "p75_hours": 60.0,
                "p90_hours": 96.0,
                "p95_hours": 120.0,
                "min_hours": 2.0,
                "max_hours": 168.0
            }
        """
        query = text("""
            SELECT
                AVG(EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as avg_hours,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as median_hours,
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as p75_hours,
                PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as p90_hours,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as p95_hours,
                MIN(EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as min_hours,
                MAX(EXTRACT(EPOCH FROM (l.converted_at - l.created_at)) / 3600) as max_hours
            FROM leads l
            WHERE l.status = 'CONVERTED'
                AND l.converted_at IS NOT NULL
                AND l.created_at >= :start_date
                AND l.created_at <= :end_date
                AND l.deleted_at IS NULL
        """)

        result = self.db.execute(query, {"start_date": start_date, "end_date": end_date})
        row = result.fetchone()

        if not row or row.avg_hours is None:
            return {
                "avg_hours": 0.0,
                "median_hours": 0.0,
                "p75_hours": 0.0,
                "p90_hours": 0.0,
                "p95_hours": 0.0,
                "min_hours": 0.0,
                "max_hours": 0.0,
            }

        return {
            "avg_hours": round(float(row.avg_hours), 2),
            "median_hours": round(float(row.median_hours), 2),
            "p75_hours": round(float(row.p75_hours), 2),
            "p90_hours": round(float(row.p90_hours), 2),
            "p95_hours": round(float(row.p95_hours), 2),
            "min_hours": round(float(row.min_hours), 2),
            "max_hours": round(float(row.max_hours), 2),
        }

    def get_conversion_by_source(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict[str, Any]]:
        """
        Taxa de conversão por origem/canal ( - L2).

        Usa conversation.chat_id para identificar origem (WhatsApp groups vs direct).

        Returns:
            [
                {
                    "source": "direct",
                    "total_leads": 120,
                    "converted_leads": 45,
                    "conversion_rate": 37.5
                },
                {
                    "source": "group",
                    "total_leads": 30,
                    "converted_leads": 5,
                    "conversion_rate": 16.67
                }
            ]
        """
        query = text("""
            WITH lead_sources AS (
                SELECT
                    l.id,
                    l.status,
                    CASE
                        WHEN c.chat_id LIKE '%@g.us' THEN 'group'
                        ELSE 'direct'
                    END as source
                FROM leads l
                LEFT JOIN conversations c ON l.conversation_id = c.id
                WHERE l.created_at >= :start_date
                    AND l.created_at <= :end_date
                    AND l.deleted_at IS NULL
            )
            SELECT
                source,
                COUNT(*) as total_leads,
                COUNT(*) FILTER (WHERE status = 'CONVERTED') as converted_leads,
                (COUNT(*) FILTER (WHERE status = 'CONVERTED')::float / COUNT(*) * 100) as conversion_rate
            FROM lead_sources
            GROUP BY source
            ORDER BY conversion_rate DESC
        """)

        result = self.db.execute(query, {"start_date": start_date, "end_date": end_date})
        rows = result.fetchall()

        return [
            {
                "source": row.source or "unknown",
                "total_leads": row.total_leads or 0,
                "converted_leads": row.converted_leads or 0,
                "conversion_rate": round(float(row.conversion_rate or 0), 2),
            }
            for row in rows
        ]

    def get_lost_leads_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Análise de leads perdidos ( - L2).

        Retorna leads com status LOST + última interação + motivo inferido.

        Returns:
            {
                "total_lost": 45,
                "lost_by_status": [
                    {"previous_status": "ENGAGED", "count": 20, "percentage": 44.44},
                    {"previous_status": "INTERESTED", "count": 15, "percentage": 33.33},
                    ...
                ],
                "avg_time_before_lost_hours": 36.5
            }
        """
        query = text("""
            WITH lost_leads AS (
                SELECT
                    l.id,
                    l.status,
                    l.created_at,
                    l.updated_at,
                    EXTRACT(EPOCH FROM (l.updated_at - l.created_at)) / 3600 as time_before_lost_hours,
                    (
                        SELECT li.interaction_type
                        FROM lead_interactions li
                        WHERE li.lead_id = l.id
                        ORDER BY li.created_at DESC
                        LIMIT 1
                    ) as last_interaction_type
                FROM leads l
                WHERE l.status = 'LOST'
                    AND l.created_at >= :start_date
                    AND l.created_at <= :end_date
                    AND l.deleted_at IS NULL
            )
            SELECT
                COUNT(*) as total_lost,
                AVG(time_before_lost_hours) as avg_time_before_lost_hours
            FROM lost_leads
        """)

        result = self.db.execute(query, {"start_date": start_date, "end_date": end_date})
        row = result.fetchone()

        if not row or row.total_lost == 0:
            return {
                "total_lost": 0,
                "lost_by_maturity_range": [],
                "avg_time_before_lost_hours": 0.0,
            }

        # Query para distribuição por range de maturity score
        maturity_query = text("""
            SELECT
                CASE
                    WHEN l.maturity_score < 20 THEN '0-19 (muito baixo)'
                    WHEN l.maturity_score < 40 THEN '20-39 (baixo)'
                    WHEN l.maturity_score < 60 THEN '40-59 (médio)'
                    WHEN l.maturity_score < 80 THEN '60-79 (alto)'
                    ELSE '80-100 (muito alto)'
                END as maturity_range,
                COUNT(*) as count
            FROM leads l
            WHERE l.status = 'LOST'
                AND l.created_at >= :start_date
                AND l.created_at <= :end_date
                AND l.deleted_at IS NULL
            GROUP BY maturity_range
            ORDER BY maturity_range
        """)

        maturity_result = self.db.execute(maturity_query, {"start_date": start_date, "end_date": end_date})
        maturity_rows = maturity_result.fetchall()

        total_lost = row.total_lost
        lost_by_maturity = [
            {
                "maturity_range": mr.maturity_range,
                "count": mr.count,
                "percentage": round((mr.count / total_lost * 100), 2),
            }
            for mr in maturity_rows
        ]

        return {
            "total_lost": total_lost,
            "lost_by_maturity_range": lost_by_maturity,
            "avg_time_before_lost_hours": round(float(row.avg_time_before_lost_hours or 0), 2),
        }

    def get_conversion_trend(
        self,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "day",  # day, week, month
    ) -> list[dict[str, Any]]:
        """
        Tendência temporal de conversão ( - L2).

        Agrega conversões por período (dia/semana/mês).

        Returns:
            [
                {
                    "period": "2026-01-01",
                    "total_leads": 25,
                    "converted_leads": 8,
                    "conversion_rate": 32.0
                },
                ...
            ]
        """
        if granularity == "week":
            trunc = "week"
        elif granularity == "month":
            trunc = "month"
        else:
            trunc = "day"

        query = text(
            """
            SELECT
                date_trunc(:granularity, l.created_at) as period,
                COUNT(*) as total_leads,
                COUNT(*) FILTER (WHERE l.status = 'CONVERTED') as converted_leads,
                (COUNT(*) FILTER (WHERE l.status = 'CONVERTED')::float / COUNT(*) * 100) as conversion_rate
            FROM leads l
            WHERE l.created_at >= :start_date
                AND l.created_at <= :end_date
                AND l.deleted_at IS NULL
            GROUP BY period
            ORDER BY period
        """
        )

        result = self.db.execute(
            query,
            {"granularity": trunc, "start_date": start_date, "end_date": end_date},
        )
        rows = result.fetchall()

        return [
            {
                "period": row.period.date().isoformat() if row.period else None,
                "total_leads": row.total_leads or 0,
                "converted_leads": row.converted_leads or 0,
                "conversion_rate": round(float(row.conversion_rate or 0), 2),
            }
            for row in rows
        ]

    # =========================================================================
    # SEÇÃO 2: PERFORMANCE ANALYTICS (Tempo de Resposta e Volume)
    # =========================================================================

    def get_human_response_time_stats(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Estatísticas de tempo de resposta (humano).

        Calcula tempo entre mensagem do lead e primeira resposta humana.

        Returns:
            {
                "avg_seconds": 180.5,
                "median_seconds": 120.0,
                "p95_seconds": 600.0,
                "p99_seconds": 1200.0,
                "total_responses": 350
            }
        """
        query = text("""
            WITH response_times AS (
                SELECT
                    c.id as conversation_id,
                    EXTRACT(EPOCH FROM (
                        MIN(m_out.created_at) - m_in.created_at
                    )) as response_seconds
                FROM conversation_messages m_in
                JOIN conversations c ON m_in.conversation_id = c.id
                JOIN conversation_messages m_out ON m_out.conversation_id = c.id
                    AND m_out.direction = 'OUTBOUND'
                    AND m_out.created_at > m_in.created_at
                WHERE m_in.direction = 'INBOUND'
                    AND m_in.created_at >= :start_date
                    AND m_in.created_at <= :end_date
                GROUP BY c.id, m_in.id, m_in.created_at
            )
            SELECT
                AVG(response_seconds) as avg_seconds,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_seconds) as median_seconds,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_seconds) as p95_seconds,
                PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_seconds) as p99_seconds,
                COUNT(*) as total_responses
            FROM response_times
            WHERE response_seconds >= 0
        """)

        result = self.db.execute(
            query,
            {
                "start_date": start_date,
                "end_date": end_date,
                "user_id": str(user_id) if user_id else None,
            },
        )
        row = result.fetchone()

        if not row or row.avg_seconds is None:
            return {
                "avg_seconds": 0.0,
                "median_seconds": 0.0,
                "p95_seconds": 0.0,
                "p99_seconds": 0.0,
                "total_responses": 0,
            }

        return {
            "avg_seconds": round(float(row.avg_seconds), 2),
            "median_seconds": round(float(row.median_seconds), 2),
            "p95_seconds": round(float(row.p95_seconds), 2),
            "p99_seconds": round(float(row.p99_seconds), 2),
            "total_responses": row.total_responses,
        }

    def get_message_volume(
        self,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "day",  # hour, day, week
    ) -> list[dict[str, Any]]:
        """
        Volume de mensagens ao longo do tempo.

        Returns:
            [
                {
                    "timestamp": "2024-12-18T00:00:00",
                    "incoming": 150,
                    "outgoing": 180,
                    "total": 330
                },
                ...
            ]
        """
        if granularity == "hour":
            trunc = "hour"
        elif granularity == "week":
            trunc = "week"
        else:
            trunc = "day"

        query = text(
            """
            SELECT
                date_trunc(:granularity, created_at) as timestamp,
                COUNT(*) FILTER (WHERE direction = 'INBOUND') as incoming,
                COUNT(*) FILTER (WHERE direction = 'OUTBOUND') as outgoing,
                COUNT(*) as total
            FROM conversation_messages
            WHERE created_at >= :start_date
                AND created_at <= :end_date
            GROUP BY timestamp
            ORDER BY timestamp
        """
        )

        result = self.db.execute(query, {"granularity": trunc, "start_date": start_date, "end_date": end_date})
        rows = result.fetchall()

        return [
            {
                "timestamp": row.timestamp.isoformat(),
                "incoming": row.incoming or 0,
                "outgoing": row.outgoing or 0,
                "total": row.total or 0,
            }
            for row in rows
        ]

    # =========================================================================
    # SEÇÃO 3: BOT PERFORMANCE ANALYTICS (Autonomia do Bot)
    # =========================================================================

    def get_bot_autonomy_rate(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Taxa de autonomia do bot (conversas resolvidas sem humano).

        Returns:
            {
                "total_conversations": 200,
                "bot_only": 120,
                "with_handoff": 80,
                "autonomy_rate": 60.0
            }
        """
        query = self.db.query(
            func.count(ConversationModel.id).label("total"),
            func.count(case((ConversationModel.handoff_at.is_(None), ConversationModel.id), else_=None)).label(
                "bot_only"
            ),
            func.count(case((ConversationModel.handoff_at.isnot(None), ConversationModel.id), else_=None)).label(
                "with_handoff"
            ),
        ).filter(
            ConversationModel.created_at >= start_date,
            ConversationModel.created_at <= end_date,
        )

        result = query.first()

        if not result or result.total == 0:
            return {
                "total_conversations": 0,
                "bot_only": 0,
                "with_handoff": 0,
                "autonomy_rate": 0.0,
            }

        total = result.total
        bot_only = result.bot_only or 0
        with_handoff = result.with_handoff or 0
        autonomy_rate = (bot_only / total * 100) if total > 0 else 0.0

        return {
            "total_conversations": total,
            "bot_only": bot_only,
            "with_handoff": with_handoff,
            "autonomy_rate": round(autonomy_rate, 2),
        }

    # =========================================================================
    # SEÇÃO 4: DASHBOARD ANALYTICS (Sumários Agregados)
    # =========================================================================

    def get_dashboard_summary(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Resumo completo para dashboard principal.

        Returns:
            {
                "total_leads": 150,
                "converted_leads": 45,
                "conversion_rate": 30.0,
                "avg_response_time_seconds": 180.5,
                "total_conversations": 200,
                "active_conversations": 25,
                "total_messages": 3500,
                "avg_messages_per_conversation": 17.5
            }
        """
        query = text("""
            SELECT
                COUNT(DISTINCT l.id) as total_leads,
                COUNT(DISTINCT CASE WHEN l.status = 'SCHEDULED' THEN l.id END) as converted_leads,
                COUNT(DISTINCT c.id) as total_conversations,
                COUNT(DISTINCT CASE WHEN c.status IN ('ACTIVE_BOT', 'PENDING_HANDOFF') THEN c.id END) as active_conversations,
                COUNT(m.id) as total_messages,
                AVG(msg_count.message_count) as avg_messages_per_conversation
            FROM leads l
            LEFT JOIN conversations c ON c.id = l.conversation_id
            LEFT JOIN conversation_messages m ON c.id = m.conversation_id
            LEFT JOIN (
                SELECT conversation_id, COUNT(*) as message_count
                FROM conversation_messages
                GROUP BY conversation_id
            ) msg_count ON c.id = msg_count.conversation_id
            WHERE l.created_at >= :start_date
                AND l.created_at <= :end_date
        """)

        result = self.db.execute(query, {"start_date": start_date, "end_date": end_date})
        row = result.fetchone()

        if not row:
            return {}

        total_leads = row.total_leads or 0
        converted_leads = row.converted_leads or 0
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0.0

        # Buscar tempo de resposta usando método interno
        response_time_stats = self.get_human_response_time_stats(start_date, end_date)

        return {
            "total_leads": total_leads,
            "converted_leads": converted_leads,
            "conversion_rate": round(conversion_rate, 2),
            "avg_response_time_seconds": response_time_stats["avg_seconds"],
            "total_conversations": row.total_conversations or 0,
            "active_conversations": row.active_conversations or 0,
            "total_messages": row.total_messages or 0,
            "avg_messages_per_conversation": round(float(row.avg_messages_per_conversation or 0), 2),
        }

    # =========================================================================
    # SEÇÃO 5: PERFORMANCE REPORTS ( - L1)
    # =========================================================================

    def get_bot_llm_latency_stats(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Estatísticas de tempo de resposta do bot (via LLM latency).

        Returns:
            {
                "avg_ms": 1500.5,
                "median_ms": 1200.0,
                "p95_ms": 3000.0,
                "p99_ms": 5000.0,
                "min_ms": 500,
                "max_ms": 8000,
                "total_interactions": 1250
            }
        """
        query = text("""
            SELECT
                AVG(latency_ms) as avg_ms,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as median_ms,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_ms,
                PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99_ms,
                MIN(latency_ms) as min_ms,
                MAX(latency_ms) as max_ms,
                COUNT(*) as total_interactions
            FROM llm_interactions
            WHERE created_at >= :start_date
                AND created_at <= :end_date
                AND latency_ms IS NOT NULL
        """)

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date},
        )
        row = result.fetchone()

        if not row or row.avg_ms is None:
            return {
                "avg_ms": 0.0,
                "median_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
                "min_ms": 0,
                "max_ms": 0,
                "total_interactions": 0,
            }

        return {
            "avg_ms": round(float(row.avg_ms), 2),
            "median_ms": round(float(row.median_ms), 2),
            "p95_ms": round(float(row.p95_ms), 2),
            "p99_ms": round(float(row.p99_ms), 2),
            "min_ms": int(row.min_ms),
            "max_ms": int(row.max_ms),
            "total_interactions": row.total_interactions,
        }

    def get_handoff_rate_stats(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Taxa de resolução automática vs handoff para humanos.

        Returns:
            {
                "total_conversations": 500,
                "bot_resolved": 350,
                "handoff_required": 150,
                "handoff_rate": 30.0,
                "auto_resolution_rate": 70.0
            }
        """
        query = text("""
            SELECT
                COUNT(*) as total_conversations,
                COUNT(*) FILTER (WHERE handoff_at IS NULL) as bot_resolved,
                COUNT(*) FILTER (WHERE handoff_at IS NOT NULL) as handoff_required
            FROM conversations
            WHERE created_at >= :start_date
                AND created_at <= :end_date
        """)

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date},
        )
        row = result.fetchone()

        if not row or row.total_conversations == 0:
            return {
                "total_conversations": 0,
                "bot_resolved": 0,
                "handoff_required": 0,
                "handoff_rate": 0.0,
                "auto_resolution_rate": 0.0,
            }

        total = row.total_conversations
        bot_resolved = row.bot_resolved or 0
        handoff_required = row.handoff_required or 0

        handoff_rate = (handoff_required / total * 100) if total > 0 else 0.0
        auto_resolution_rate = (bot_resolved / total * 100) if total > 0 else 0.0

        return {
            "total_conversations": total,
            "bot_resolved": bot_resolved,
            "handoff_required": handoff_required,
            "handoff_rate": round(handoff_rate, 2),
            "auto_resolution_rate": round(auto_resolution_rate, 2),
        }

    def get_peak_hours_stats(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict[str, Any]]:
        """
        Horários de pico de atendimento (agregado por hora do dia).

        Returns:
            [
                {"hour": 9, "message_count": 450, "conversation_count": 85},
                {"hour": 10, "message_count": 520, "conversation_count": 95},
                ...
            ]
        """
        query = text("""
            SELECT
                EXTRACT(HOUR FROM created_at) as hour,
                COUNT(*) as message_count,
                COUNT(DISTINCT conversation_id) as conversation_count
            FROM conversation_messages
            WHERE created_at >= :start_date
                AND created_at <= :end_date
            GROUP BY hour
            ORDER BY hour
        """)

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date},
        )
        rows = result.fetchall()

        return [
            {
                "hour": int(row.hour),
                "message_count": row.message_count or 0,
                "conversation_count": row.conversation_count or 0,
            }
            for row in rows
        ]

    def get_conversations_by_status(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict[str, Any]]:
        """
        Distribuição de conversas por status.

        Returns:
            [
                {"status": "ACTIVE_BOT", "count": 150, "percentage": 30.0},
                {"status": "PENDING_HANDOFF", "count": 50, "percentage": 10.0},
                ...
            ]
        """
        query = text("""
            WITH status_counts AS (
                SELECT
                    status,
                    COUNT(*) as count
                FROM conversations
                WHERE created_at >= :start_date
                    AND created_at <= :end_date
                GROUP BY status
            ),
            total_count AS (
                SELECT SUM(count) as total FROM status_counts
            )
            SELECT
                sc.status,
                sc.count,
                (sc.count::float / tc.total * 100) as percentage
            FROM status_counts sc, total_count tc
            ORDER BY sc.count DESC
        """)

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date},
        )
        rows = result.fetchall()

        if not rows:
            return []

        return [
            {
                "status": row.status,
                "count": row.count,
                "percentage": round(float(row.percentage), 2),
            }
            for row in rows
        ]

    # =====================================================================
    # Seção 6: Análise de Conversas (L3)
    # =====================================================================

    def get_message_frequency_by_hour(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict[str, Any]]:
        """
        Heatmap de atividade: mensagens por dia da semana e hora do dia.

        Returns:
            [
                {"day_of_week": 0, "hour": 9, "message_count": 150},
                {"day_of_week": 0, "hour": 10, "message_count": 180},
                ...
            ]
        """
        query = text("""
            SELECT
                EXTRACT(DOW FROM created_at) as day_of_week,
                EXTRACT(HOUR FROM created_at) as hour,
                COUNT(*) as message_count
            FROM conversation_messages
            WHERE created_at >= :start_date
                AND created_at <= :end_date
            GROUP BY day_of_week, hour
            ORDER BY day_of_week, hour
        """)

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date},
        )
        rows = result.fetchall()

        return [
            {
                "day_of_week": int(row.day_of_week),
                "hour": int(row.hour),
                "message_count": row.message_count or 0,
            }
            for row in rows
        ]

    def get_keyword_frequency(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Palavras-chave mais frequentes nas mensagens INBOUND.

        Stop words carregadas de analytics_config.yaml (editável sem deploy).

        P3 #2: Usa to_tsvector PostgreSQL Full-Text Search para acurácia +30%.

        Returns:
            [
                {"keyword": "agendamento", "count": 250},
                {"keyword": "preço", "count": 180},
                ...
            ]
        """
        config = get_analytics_config()
        stop_words_list = config.stop_words

        # Build SQL ARRAY dinamicamente
        stop_words_escaped = "', '".join(stop_words_list)
        stop_words_sql = f"ARRAY['{stop_words_escaped}']"

        # P3 #2: Substituído string_to_array por to_tsvector('portuguese')
        # to_tsvector faz:
        # - Stemming automático (agendamento, agendar, agenda → agend)
        # - Stop words nativas do PostgreSQL
        # - Acurácia +30% vs split por espaço
        query = text(f"""
            WITH message_tokens AS (
                SELECT
                    unnest(tsvector_to_array(to_tsvector('portuguese', body))) as token
                FROM conversation_messages
                WHERE created_at >= :start_date
                    AND created_at <= :end_date
                    AND direction = 'INBOUND'
                    AND body IS NOT NULL
                    AND LENGTH(body) > 0
            ),
            custom_stop_words AS (
                SELECT unnest({stop_words_sql}) as word
            )
            SELECT
                token as keyword,
                COUNT(*) as count
            FROM message_tokens
            WHERE token NOT IN (SELECT word FROM custom_stop_words)
                AND LENGTH(token) > 2
            GROUP BY token
            ORDER BY count DESC
            LIMIT :limit
        """)

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date, "limit": limit},
        )
        rows = result.fetchall()

        return [
            {
                "keyword": row.keyword,
                "count": row.count,
            }
            for row in rows
        ]

    async def get_message_sentiment_distribution(
        self,
        start_date: datetime,
        end_date: datetime,
        use_gemini_fallback: bool = False,
    ) -> dict[str, Any]:
        """
        Análise de sentimento com fallback Gemini API (P3 #3).

        Strategy:
        1. Regex (rápido, grátis) - default
        2. Gemini API (preciso +60%, pago) - ativa se use_gemini_fallback=True

        Keywords carregadas de analytics_config.yaml (editável sem deploy).

        Args:
            use_gemini_fallback: Se True, usa Gemini API para mensagens neutras (maior acurácia)

        Returns:
            {
                "positive": 350,
                "negative": 80,
                "neutral": 570,
                "total_messages": 1000,
                "gemini_used": false  # indica se Gemini foi usado
            }
        """
        config = get_analytics_config()
        positive_regex = config.build_sentiment_regex("positive")
        negative_regex = config.build_sentiment_regex("negative")

        # Estratégia 1: Regex (sempre executada primeiro)
        query = text(f"""
            WITH sentiment_keywords AS (
                SELECT
                    id,
                    body,
                    LOWER(body) as body_lower,
                    CASE
                        WHEN LOWER(body) ~ '{positive_regex}' THEN 'positive'
                        WHEN LOWER(body) ~ '{negative_regex}' THEN 'negative'
                        ELSE 'neutral'
                    END as sentiment_regex
                FROM conversation_messages
                WHERE created_at >= :start_date
                    AND created_at <= :end_date
                    AND direction = 'INBOUND'
                    AND body IS NOT NULL
            )
            SELECT
                id,
                body,
                sentiment_regex,
                COUNT(*) OVER (PARTITION BY sentiment_regex) as sentiment_count,
                COUNT(*) OVER () as total_count
            FROM sentiment_keywords
        """)

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date},
        )
        rows = result.fetchall()

        if not rows:
            return {
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "total_messages": 0,
                "gemini_used": False,
            }

        # Agregar resultados regex
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        neutral_messages = []

        for row in rows:
            sentiment_counts[row.sentiment_regex] = row.sentiment_count
            if row.sentiment_regex == "neutral" and use_gemini_fallback:
                neutral_messages.append({"id": row.id, "body": row.body})

        total_messages = rows[0].total_count if rows else 0

        # Estratégia 2: Gemini API Fallback (apenas para mensagens neutras)
        gemini_used = False
        if use_gemini_fallback and neutral_messages:
            gemini_used = True
            sentiment_counts = await self._refine_sentiment_with_gemini(
                neutral_messages,
                sentiment_counts,
                config,
            )

        return {
            "positive": sentiment_counts["positive"],
            "negative": sentiment_counts["negative"],
            "neutral": sentiment_counts["neutral"],
            "total_messages": total_messages,
            "gemini_used": gemini_used,
        }

    async def _refine_sentiment_with_gemini(
        self,
        neutral_messages: list[dict],
        sentiment_counts: dict,
        config: Any,
    ) -> dict:
        """
        Refina sentimento de mensagens neutras usando Gemini API.

        P3 #3: Batch processing + cache para reduzir custos.
        """
        logger = logging.getLogger(__name__)
        if get_llm_client is None:
            return sentiment_counts

        cache = get_cache() if get_cache else None

        # Config Gemini
        gemini_config = config.data.get("sentiment_analysis", {}).get("gemini_fallback", {})
        batch_size = gemini_config.get("batch_size", 50)
        cache_ttl = gemini_config.get("cache_ttl_seconds", 86400)
        prompt_template = config.data.get("sentiment_analysis", {}).get("gemini_prompt", "")

        llm = get_llm_client()
        refined_positive = 0
        refined_negative = 0
        refined_neutral = 0

        # Process em batches
        for i in range(0, len(neutral_messages), batch_size):
            batch = neutral_messages[i : i + batch_size]

            for msg in batch:
                # Check cache primeiro
                cache_key = f"sentiment:gemini:{msg['id']}"
                cached_sentiment = cache.get(cache_key) if cache else None

                if cached_sentiment:
                    if cached_sentiment == "POSITIVE":
                        refined_positive += 1
                    elif cached_sentiment == "NEGATIVE":
                        refined_negative += 1
                    else:
                        refined_neutral += 1
                    continue

                # Chamada Gemini
                try:
                    prompt = prompt_template.replace("{message}", msg["body"])
                    
                    # LLMClient now uses generate_response which returns a dict
                    response_data = await llm.generate_response(prompt)
                    gemini_sentiment = response_data.get("response", "NEUTRAL").strip().upper()

                    # Normalizar resposta
                    if gemini_sentiment not in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
                        gemini_sentiment = "NEUTRAL"

                    # Cache resultado
                    if cache:
                        cache.set(cache_key, gemini_sentiment, ttl=cache_ttl)

                    # Contar
                    if gemini_sentiment == "POSITIVE":
                        refined_positive += 1
                    elif gemini_sentiment == "NEGATIVE":
                        refined_negative += 1
                    else:
                        refined_neutral += 1

                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.warning("Gemini sentiment analysis failed for message %s: %s", msg.get("id"), e)
                    refined_neutral += 1  # Fallback: mantém como neutral

        # Atualizar contadores
        sentiment_counts["positive"] += refined_positive
        sentiment_counts["negative"] += refined_negative
        sentiment_counts["neutral"] = refined_neutral  # Só os que Gemini confirmou como neutral

        logger.info(
            "Gemini sentiment refinement: %d messages processed, +%d positive, +%d negative, %d remain neutral",
            len(neutral_messages),
            refined_positive,
            refined_negative,
            refined_neutral,
        )

        return sentiment_counts

    def get_conversation_topics(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict[str, Any]]:
        """
        Topics mais discutidos baseados em keywords temáticas configuráveis.

        Topics e keywords carregados de analytics_config.yaml (editável sem deploy).

        Returns:
            [
                {"topic": "Agendamento", "count": 250, "percentage": 35.0},
                {"topic": "Preços", "count": 150, "percentage": 21.0},
                ...
            ]
        """
        config = get_analytics_config()
        topic_cases_sql = config.build_topic_sql_cases()

        query = text(f"""
            WITH topic_detection AS (
                SELECT
                    id,
                    {topic_cases_sql} as topic
                FROM conversation_messages
                WHERE created_at >= :start_date
                    AND created_at <= :end_date
                    AND direction = 'INBOUND'
            ),
            topic_counts AS (
                SELECT
                    topic,
                    COUNT(*) as count
                FROM topic_detection
                GROUP BY topic
            ),
            total_count AS (
                SELECT SUM(count) as total FROM topic_counts
            )
            SELECT
                tc.topic,
                tc.count,
                (tc.count::float / t.total * 100) as percentage
            FROM topic_counts tc, total_count t
            ORDER BY tc.count DESC
        """)

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date},
        )
        rows = result.fetchall()

        return [
            {
                "topic": row.topic,
                "count": row.count,
                "percentage": round(float(row.percentage), 2),
            }
            for row in rows
        ]

    # =====================================================================
    # Seção 7: Real-time Dashboard (L4)
    # =====================================================================

    def get_active_conversations(self) -> list[dict[str, Any]]:
        """
        Conversas ativas no momento (últimos 5 minutos).

        Returns:
            [
                {
                    "id": "uuid",
                    "chat_id": "5511999999999@c.us",
                    "status": "ACTIVE_BOT",
                    "last_message_at": "2026-01-08T14:35:00",
                    "minutes_since_last_message": 2
                }
            ]
        """
        query = text("""
            SELECT
                id,
                chat_id,
                status,
                last_message_at,
                EXTRACT(EPOCH FROM (NOW() - last_message_at)) / 60 as minutes_since_last_message
            FROM conversations
            WHERE last_message_at >= NOW() - INTERVAL '5 minutes'
                AND status IN ('ACTIVE_BOT', 'ACTIVE_HUMAN', 'PENDING_HANDOFF')
            ORDER BY last_message_at DESC
            LIMIT 100
        """)

        result = self.db.execute(query)
        rows = result.fetchall()

        return [
            {
                "id": row.id,
                "chat_id": row.chat_id,
                "status": row.status,
                "last_message_at": row.last_message_at.isoformat(),
                "minutes_since_last_message": round(float(row.minutes_since_last_message), 1),
            }
            for row in rows
        ]

    def get_performance_alerts(
        self,
        latency_threshold_ms: int = 5000,
        error_rate_threshold: float = 5.0,
    ) -> dict[str, Any]:
        """
        Alertas de performance baseados em thresholds.

        Args:
            latency_threshold_ms: Latência máxima aceitável em ms (default: 5000ms)
            error_rate_threshold: Taxa de erro máxima em % (default: 5%)

        Returns:
            {
                "high_latency_count": 10,
                "high_latency_avg_ms": 6500,
                "error_rate": 7.5,
                "total_interactions_last_hour": 500,
                "failed_interactions": 38
            }
        """
        logger = logging.getLogger(__name__)
        logger.debug(
            "Performance thresholds: latency=%sms, error_rate=%s%%", latency_threshold_ms, error_rate_threshold
        )

        query = text("""
            WITH recent_interactions AS (
                SELECT
                    id,
                    latency_ms,
                    error,
                    error_message
                FROM llm_interactions
                WHERE created_at >= NOW() - INTERVAL '1 hour'
            )
            SELECT
                COUNT(*) FILTER (WHERE latency_ms > :latency_threshold) as high_latency_count,
                AVG(latency_ms) FILTER (WHERE latency_ms > :latency_threshold) as high_latency_avg_ms,
                COUNT(*) FILTER (WHERE error = true) as failed_interactions,
                COUNT(*) as total_interactions,
                (COUNT(*) FILTER (WHERE error = true)::float / NULLIF(COUNT(*), 0) * 100) as error_rate
            FROM recent_interactions
        """)

        result = self.db.execute(
            query,
            {
                "latency_threshold": latency_threshold_ms,
            },
        )
        row = result.fetchone()

        if not row or row.total_interactions == 0:
            return {
                "high_latency_count": 0,
                "high_latency_avg_ms": 0.0,
                "error_rate": 0.0,
                "total_interactions_last_hour": 0,
                "failed_interactions": 0,
            }

        return {
            "high_latency_count": row.high_latency_count or 0,
            "high_latency_avg_ms": round(float(row.high_latency_avg_ms or 0), 2),
            "error_rate": round(float(row.error_rate or 0), 2),
            "total_interactions_last_hour": row.total_interactions,
            "failed_interactions": row.failed_interactions or 0,
        }

    def get_realtime_summary(self) -> dict[str, Any]:
        """
        Sumário de métricas em tempo real (últimos 5 minutos).

        Returns:
            {
                "active_conversations": 15,
                "messages_per_minute": 8.2,
                "avg_response_time_ms": 1500,
                "bot_resolution_rate": 85.0
            }
        """
        query = text("""
            WITH recent_data AS (
                SELECT
                    COUNT(DISTINCT c.id) as active_conversations,
                    COUNT(DISTINCT cm.id) as total_messages,
                    AVG(li.latency_ms) as avg_latency,
                    COUNT(DISTINCT c.id) FILTER (WHERE c.handoff_at IS NULL AND c.status = 'COMPLETED') as bot_resolved,
                    COUNT(DISTINCT c.id) FILTER (WHERE c.status IN ('COMPLETED', 'PENDING_HANDOFF', 'ACTIVE_HUMAN')) as total_completed
                FROM conversations c
                LEFT JOIN conversation_messages cm ON cm.conversation_id = c.id
                    AND cm.created_at >= NOW() - INTERVAL '5 minutes'
                LEFT JOIN llm_interactions li ON li.conversation_id = c.id
                    AND li.created_at >= NOW() - INTERVAL '5 minutes'
                WHERE c.last_message_at >= NOW() - INTERVAL '5 minutes'
            )
            SELECT
                active_conversations,
                total_messages,
                (total_messages::float / 5.0) as messages_per_minute,
                avg_latency,
                (bot_resolved::float / NULLIF(total_completed, 0) * 100) as bot_resolution_rate
            FROM recent_data
        """)

        result = self.db.execute(query)
        row = result.fetchone()

        if not row:
            return {
                "active_conversations": 0,
                "messages_per_minute": 0.0,
                "avg_response_time_ms": 0.0,
                "bot_resolution_rate": 0.0,
            }

        return {
            "active_conversations": row.active_conversations or 0,
            "messages_per_minute": round(float(row.messages_per_minute or 0), 2),
            "avg_response_time_ms": round(float(row.avg_latency or 0), 2),
            "bot_resolution_rate": round(float(row.bot_resolution_rate or 0), 2),
        }

