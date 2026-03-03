from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_db
from robbot.schemas.health import HealthOut
from robbot.services.infrastructure.health_service import HealthService

router = APIRouter()


@router.get("/debug/messages")
def debug_messages(db: Session = Depends(get_db)):
    from robbot.infra.persistence.models.conversation_message_model import ConversationMessageModel

    msgs = db.query(ConversationMessageModel).all()
    return [{"id": m.id, "body": m.body, "created_at": str(m.created_at)} for m in msgs]


@router.get("", response_model=HealthOut)
async def health_check(response: Response, db: Session = Depends(get_db)):
    """
    Endpoint de health check da API.
    Controller: apenas mapeia request -> chama service -> formata response.
    """
    service = HealthService(db)
    result = await service.get_health()
    overall_ok = all(component.get("ok") for component in result.components.values())
    response.status_code = status.HTTP_200_OK if overall_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return result

