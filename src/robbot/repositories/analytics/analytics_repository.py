"""
Analytics Repository

Repositório especializado em queries agregadas e análises complexas.
Otimizado para performance com CTEs e window functions.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import func, and_, or_, case, cast, Integer, Float, extract, text
from sqlalchemy.orm import Session, aliased

from robbot.infra.db.models.conversation_model import ConversationModel
from robbot.infra.db.models.conversation_message_model import ConversationMessageModel
from robbot.infra.db.models.lead_model import LeadModel
from robbot.infra.db.models.user_model import UserModel
from robbot.domain.enums import LeadStatus, ConversationStatus


class AnalyticsRepository:
    """Repository para queries analíticas e agregações complexas"""

    def __init__(self, db_session: Session):
        self.db = db_session

    # =============================================================================
    # CONVERSION ANALYTICS
    # =============================================================================

    def get_conversion_rate(
        self,
        start_date: datetime,
        end_date: datetime,
        segment_by: Optional[str] = None,
    ) -> Dict[str, Any]:
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
            func.count(
                case((LeadModel.status == LeadStatus.CONVERTED, LeadModel.id))
            ).label("converted_leads"),
        ).filter(
            LeadModel.created_at >= start_date,
            LeadModel.created_at <= end_date,
            LeadModel.deleted_at.is_(None),
        )

        if segment_by:
            if segment_by == "assigned_to":
                query = query.join(UserModel, LeadModel.assigned_to_user_id == UserModel.id)
                query = query.add_columns(
                    UserModel.full_name.label("segment_name"),
                    UserModel.id.label("segment_id"),
                )
                query = query.group_by(UserModel.id, UserModel.full_name)
            # Adicionar outros segments futuramente
        
        result = query.all()

        if not segment_by:
            row = result[0] if result else (0, 0)
            total = row.total_leads or 0
            converted = row.converted_leads or 0
            rate = (converted / total * 100) if total > 0 else 0.0

            return {
                "total_leads": total,
                "converted_leads": converted,
                "conversion_rate": round(rate, 2),
            }
        else:
            segments = []
            for row in result:
                total = row.total_leads or 0
                converted = row.converted_leads or 0
                rate = (converted / total * 100) if total > 0 else 0.0
                
                segments.append({
                    "segment_name": row.segment_name,
                    "segment_id": str(row.segment_id),
                    "total_leads": total,
                    "converted_leads": converted,
                    "conversion_rate": round(rate, 2),
                })

            return {"segments": segments}

    def get_conversion_funnel(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
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
        # CTE para calcular cada etapa
        query = text("""
            WITH funnel AS (
                SELECT
                    COUNT(DISTINCT l.id) as total_created,
                    COUNT(DISTINCT CASE WHEN cm.id IS NOT NULL THEN l.id END) as total_engaged,
                    COUNT(DISTINCT CASE WHEN l.maturity_score >= 60 THEN l.id END) as total_qualified,
                    COUNT(DISTINCT CASE WHEN c.handoff_at IS NOT NULL THEN l.id END) as total_handoff,
                    COUNT(DISTINCT CASE WHEN l.status = 'CONVERTED' THEN l.id END) as total_converted
                FROM leads l
                LEFT JOIN conversations c ON l.id = c.lead_id
                LEFT JOIN conversation_messages cm ON c.id = cm.conversation_id 
                    AND cm.direction = 'INCOMING'
                WHERE l.created_at >= :start_date
                    AND l.created_at <= :end_date
                    AND l.deleted_at IS NULL
            )
            SELECT * FROM funnel
        """)

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date}
        )
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
                "drop_off": round((total_created - (row.total_engaged or 0)) / total_created * 100, 2) if total_created > 0 else 0,
            },
            {
                "stage": "qualified",
                "name": "Qualificados (score >= 60)",
                "count": row.total_qualified or 0,
                "percentage": round((row.total_qualified or 0) / total_created * 100, 2) if total_created > 0 else 0,
                "drop_off": round(((row.total_engaged or 0) - (row.total_qualified or 0)) / (row.total_engaged or 0) * 100, 2) if row.total_engaged else 0,
            },
            {
                "stage": "handoff",
                "name": "Transferidos para humano",
                "count": row.total_handoff or 0,
                "percentage": round((row.total_handoff or 0) / total_created * 100, 2) if total_created > 0 else 0,
                "drop_off": round(((row.total_qualified or 0) - (row.total_handoff or 0)) / (row.total_qualified or 0) * 100, 2) if row.total_qualified else 0,
            },
            {
                "stage": "converted",
                "name": "Convertidos (agendaram)",
                "count": row.total_converted or 0,
                "percentage": round((row.total_converted or 0) / total_created * 100, 2) if total_created > 0 else 0,
                "drop_off": round(((row.total_handoff or 0) - (row.total_converted or 0)) / (row.total_handoff or 0) * 100, 2) if row.total_handoff else 0,
            },
        ]

        return {"stages": stages}

    def get_time_to_conversion(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, float]:
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

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date}
        )
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

    # =============================================================================
    # PERFORMANCE ANALYTICS
    # =============================================================================

    def get_response_time_stats(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
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
        # Query complexa com window function para achar primeira resposta após mensagem do lead
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
                    AND m_out.direction = 'OUTGOING'
                    AND m_out.created_at > m_in.created_at
                WHERE m_in.direction = 'INCOMING'
                    AND c.handoff_at IS NOT NULL
                    AND m_in.created_at >= :start_date
                    AND m_in.created_at <= :end_date
                    AND (:user_id::uuid IS NULL OR c.handoff_to = :user_id::uuid)
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
                "user_id": str(user_id) if user_id else None
            }
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
    ) -> List[Dict[str, Any]]:
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

        query = text(f"""
            SELECT
                date_trunc(:granularity, created_at) as timestamp,
                COUNT(*) FILTER (WHERE direction = 'INCOMING') as incoming,
                COUNT(*) FILTER (WHERE direction = 'OUTGOING') as outgoing,
                COUNT(*) as total
            FROM conversation_messages
            WHERE created_at >= :start_date
                AND created_at <= :end_date
            GROUP BY timestamp
            ORDER BY timestamp
        """)

        result = self.db.execute(
            query,
            {
                "granularity": trunc,
                "start_date": start_date,
                "end_date": end_date
            }
        )
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

    # =============================================================================
    # DASHBOARD SUMMARY
    # =============================================================================

    def get_dashboard_summary(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
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
        # Query agregada otimizada
        query = text("""
            SELECT
                COUNT(DISTINCT l.id) as total_leads,
                COUNT(DISTINCT CASE WHEN l.status = 'CONVERTED' THEN l.id END) as converted_leads,
                COUNT(DISTINCT c.id) as total_conversations,
                COUNT(DISTINCT CASE WHEN c.status IN ('ACTIVE', 'WAITING') THEN c.id END) as active_conversations,
                COUNT(m.id) as total_messages,
                AVG(msg_count.message_count) as avg_messages_per_conversation
            FROM leads l
            LEFT JOIN conversations c ON l.id = c.lead_id
            LEFT JOIN conversation_messages m ON c.id = m.conversation_id
            LEFT JOIN (
                SELECT conversation_id, COUNT(*) as message_count
                FROM conversation_messages
                GROUP BY conversation_id
            ) msg_count ON c.id = msg_count.conversation_id
            WHERE l.created_at >= :start_date
                AND l.created_at <= :end_date
                AND l.deleted_at IS NULL
        """)

        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date}
        )
        row = result.fetchone()

        if not row:
            return {}

        total_leads = row.total_leads or 0
        converted_leads = row.converted_leads or 0
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0.0

        # Buscar tempo de resposta separadamente (query complexa)
        response_time_stats = self.get_response_time_stats(start_date, end_date)

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

    # =============================================================================
    # BOT PERFORMANCE
    # =============================================================================

    def get_bot_autonomy_rate(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
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
            func.count(
                case((ConversationModel.handoff_at.is_(None), ConversationModel.id))
            ).label("bot_only"),
            func.count(
                case((ConversationModel.handoff_at.isnot(None), ConversationModel.id))
            ).label("with_handoff"),
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
