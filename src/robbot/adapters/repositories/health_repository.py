from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class HealthRepository:
    """
    Repositório responsável por checar conectividade com o banco.
    Encapsula a query SQL simples usada para health check.
    """

    def __init__(self, db: Session):
        self.db = db

    def ping(self) -> bool:
        """
        Executa uma consulta simples para checar conectividade com o DB.
        Retorna True se o DB responder corretamente.
        """
        # Usamos texto SQL simples compatível com Postgres
        result = self.db.execute(text("SELECT 1")).scalar_one_or_none()
        return result == 1
