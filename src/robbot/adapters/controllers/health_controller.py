from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_db
from robbot.schemas.health import HealthOut
from robbot.services.health_service import HealthService

router = APIRouter()


@router.get("/health", response_model=HealthOut, status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """
    Endpoint de health check da API.
    Controller: apenas mapeia request -> chama service -> formata response.
    """
    service = HealthService(db)
    result = service.get_health()
    return result
