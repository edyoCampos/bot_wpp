"""
Metrics controller for legacy test endpoints.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.analytics_repository import AnalyticsRepository
from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.infra.redis.client import get_redis_client
from robbot.infra.redis.queue import get_queue_manager
from robbot.services.analytics.metrics_service import MetricsService

router = APIRouter()


def get_metrics_service(db_session: Session = Depends(get_db)) -> MetricsService:
    return MetricsService(
        analytics_repo=AnalyticsRepository(db_session),
        redis_client=get_redis_client(),
        queue_manager=get_queue_manager(),
    )


def _parse_dates(start_date: str | None, end_date: str | None) -> tuple[datetime, datetime, str]:
    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0)
            end = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format") from exc
        if start > end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date range: start_date must be <= end_date",
            )
        return start, end, f"{start.date().isoformat()}_{end.date().isoformat()}"

    start = datetime(1970, 1, 1)
    end = datetime.now().replace(hour=23, minute=59, second=59)
    return start, end, "all_time"


@router.get("/overview")
async def get_metrics_overview(
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _current_user=Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Legacy overview metrics endpoint used by API tests."""
    start, end, period = _parse_dates(start_date, end_date)
    summary = await svc.get_dashboard_summary(start, end)
    kpis = summary.get("kpis", {})

    return {
        "period": period,
        "total_conversations": kpis.get("total_conversations", 0),
        "conversion_rate": kpis.get("conversion_rate", 0.0),
        "total_leads": kpis.get("total_leads", 0),
        "converted_leads": kpis.get("converted_leads", 0),
    }


@router.get("/campaigns")
def get_campaign_metrics(
    _current_user=Depends(get_current_user),
):
    """Legacy campaigns metrics endpoint used by API tests."""
    return []

