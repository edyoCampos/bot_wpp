"""
Dashboard Controller - MVP KISS

Apenas 3 endpoints essenciais para dashboard básico.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from robbot.repositories.analytics.analytics_repository import AnalyticsRepository
from robbot.services.analytics.metrics_service import MetricsService
from robbot.schemas.metrics_schemas import (
    DashboardSummaryResponse,
    ConversionFunnelResponse,
    BotAutonomyResponse,
)
from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.infra.redis.client import get_redis_client
from robbot.infra.db.models.user_model import UserModel
from robbot.domain.enums import Role

router = APIRouter(prefix="/metrics", tags=["Metrics"])


def get_metrics_service(db_session: Session = Depends(get_db)) -> MetricsService:
    """Injeta MetricsService"""
    return MetricsService(AnalyticsRepository(db_session), get_redis_client())


def check_admin(current_user: UserModel = Depends(get_current_user)):
    """Apenas admin"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas admin")
    return current_user


def parse_dates(
    start_date: Optional[str], end_date: Optional[str], period: str
) -> tuple[datetime, datetime]:
    """Parse datas"""
    if start_date and end_date:
        return (
            datetime.fromisoformat(start_date).replace(hour=0, minute=0),
            datetime.fromisoformat(end_date).replace(hour=23, minute=59),
        )
    
    end = datetime.now().replace(hour=23, minute=59, second=59)
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
    return end - timedelta(days=days), end


@router.get("/dashboard", response_model=DashboardSummaryResponse)
def dashboard(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """KPIs: conversão, mensagens, tempo resposta. Cache 5min."""
    start, end = parse_dates(start_date, end_date, period)
    return svc.get_dashboard_summary(start, end)


@router.get("/conversion-funnel", response_model=ConversionFunnelResponse)
def funnel(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Funil 5 etapas + drop-off. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return svc.get_conversion_funnel(start, end)


@router.get("/bot-autonomy", response_model=BotAutonomyResponse)
def bot_autonomy(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(check_admin),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Taxa autonomia bot. Admin only. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return svc.get_bot_autonomy_rate(start, end)
