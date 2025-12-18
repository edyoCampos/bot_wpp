from datetime import datetime

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_db
from robbot.schemas.health import HealthOut
from robbot.services.health_service import HealthService

router = APIRouter()


@router.get("/health", response_model=HealthOut)
async def health_check(response: Response, db: Session = Depends(get_db)):
    """
    Endpoint de health check da API.
    Controller: apenas mapeia request -> chama service -> formata response.
    """
    service = HealthService(db)
    result = await service.get_health()
    overall_ok = all(
        component.get("ok") for component in result.components.values()
    )
    response.status_code = (
        status.HTTP_200_OK
        if overall_ok
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return result
