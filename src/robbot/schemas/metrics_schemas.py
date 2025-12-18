"""
Metrics Schemas

Pydantic schemas para validação e serialização de métricas.
"""

from datetime import datetime, date
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# COMMON SCHEMAS
# =============================================================================

class PeriodSchema(BaseModel):
    """Período de análise"""
    start: date = Field(..., description="Data inicial")
    end: date = Field(..., description="Data final")


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

    class Config:
        json_schema_extra = {
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
                    "avg_messages_per_conversation": 17.5
                }
            }
        }


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
    segment_id: Optional[str] = None


class ConversionRateResponse(BaseModel):
    """Response da taxa de conversão"""
    period: PeriodSchema
    conversion: Optional[ConversionMetricsSchema] = None
    segments: Optional[List[ConversionSegmentSchema]] = None


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
    funnel: Dict[str, List[FunnelStageSchema]] = Field(..., description="Stages do funil")

    class Config:
        json_schema_extra = {
            "example": {
                "period": {"start": "2024-12-01", "end": "2024-12-31"},
                "funnel": {
                    "stages": [
                        {
                            "stage": "created",
                            "name": "Leads Criados",
                            "count": 150,
                            "percentage": 100.0,
                            "drop_off": 0.0
                        },
                        {
                            "stage": "engaged",
                            "name": "Engajados (responderam)",
                            "count": 120,
                            "percentage": 80.0,
                            "drop_off": 20.0
                        }
                    ]
                }
            }
        }


class TimeToConversionStatsSchema(BaseModel):
    """Estatísticas de tempo até conversão"""
    avg_hours: float = Field(..., ge=0, description="Média (horas)")
    median_hours: float = Field(..., ge=0, description="Mediana (horas)")
    min_hours: float = Field(..., ge=0, description="Mínimo (horas)")
    max_hours: float = Field(..., ge=0, description="Máximo (horas)")
    p95_hours: float = Field(..., ge=0, description="95º percentil (horas)")


class TimeToConversionResponse(BaseModel):
    """Response do tempo até conversão"""
    period: PeriodSchema
    time_stats: TimeToConversionStatsSchema


# =============================================================================
# PERFORMANCE ANALYTICS SCHEMAS
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
    user_id: Optional[str] = Field(None, description="UUID do usuário (null = global)")
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
    data_points: List[MessageVolumeDataPointSchema]


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
    forecast: List[ForecastDataPointSchema]
    status: str = Field(default="not_implemented")
    message: Optional[str] = None
