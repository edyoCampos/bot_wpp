"""Repository for persisting alert records to the database."""

from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from robbot.infra.db.models.alert_model import AlertModel


class AlertRepository:
    """
    Persistência de alerts no banco.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        level: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AlertModel:
        """
        Cria e persiste um AlertModel.
        """
        obj = AlertModel(
            level=level,
            message=message,
            metadata_json=metadata or {},
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, alert_id: int) -> Optional[AlertModel]:
        """Retrieve an alert by ID."""
        return self.db.get(AlertModel, alert_id)
