from datetime import datetime
from typing import Dict

from sqlalchemy.orm import Session

from robbot.adapters.repositories.health_repository import HealthRepository
from robbot.services.alert_service import AlertService
from robbot.schemas.health import HealthOut
from robbot.config.settings import settings


class HealthService:
    """
    Serviço responsável por verificar saúde da API e seus componentes (ex.: DB).
    """

    def __init__(self, db: Session):
        self.db = db
        self.health_repo = HealthRepository(db)
        self.alert_service = AlertService(db)

    def get_health(self) -> HealthOut:
        """
        Checa integrações essenciais (DB) e retorna um resumo.
        Se houver falha crítica e alerts estiver configurado, persiste alerta.
        """
        now = datetime.utcnow()
        db_ok = False
        db_error: str | None = None
        redis_ok = False
        redis_error: str | None = None
        try:
            db_ok = self.health_repo.ping()
        except Exception as exc:  # pragma: no cover - integration moment
            db_ok = False
            db_error = str(exc)

        try:
            redis_ok = self.health_repo.check_redis_connection()
        except Exception as exc:  # pragma: no cover - integration moment
            redis_ok = False
            redis_error = str(exc)

        status_str = "ok" if db_ok and redis_ok else "unhealthy"

        # Se crítico (DB down) e alerts ativados, persistir alerta básico
        if not db_ok and getattr(settings, "SMTP_SENDER", None) is not None:
            # Persistir alerta para análise posterior
            try:
                self.alert_service.create_alert(
                    level="critical",
                    message="Database unreachable in health check",
                    metadata={"error": db_error},
                )
            except Exception:
                # Não propagar erro de persistência de alerta no health check
                pass

        return HealthOut(
            status=status_str,
            components={
                "database": {"ok": db_ok, "error": db_error},
                "redis": {"ok": redis_ok, "error": redis_error},
            },
            timestamp=now,
        )
