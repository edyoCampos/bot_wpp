from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from robbot.adapters.repositories.alert_repository import AlertRepository
from robbot.infra.db.models.alert_model import AlertModel


class AlertService:
    """
    Serviço para criação/consulta de alerts persistidos.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = AlertRepository(db)

    def create_alert(self, level: str, message: str, metadata: Dict[str, Any] | None = None) -> AlertModel:
        """
        Persiste um alerta no banco. Retorna a entidade criada.
        """
        metadata = metadata or {}
        alert = self.repo.create(level=level, message=message, metadata=metadata)
        return alert