"""Repository for managing revoked JWT tokens."""

from typing import Optional

from sqlalchemy.orm import Session

from robbot.infra.db.models.revoked_token_model import RevokedTokenModel


class TokenRepository:
    """
    Repository to manage revoked tokens persistence.
    """

    def __init__(self, db: Session):
        self.db = db

    def revoke(self, token: str) -> RevokedTokenModel:
        """
        Persist a revoked token.
        """
        obj = RevokedTokenModel(token=token)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def is_revoked(self, token: str) -> bool:
        """
        Check whether the token was revoked.
        """
        q = self.db.query(RevokedTokenModel).filter(
            RevokedTokenModel.token == token)
        exists_ = self.db.query(q.exists()).scalar()
        return bool(exists_)

    def get_by_token(self, token: str) -> Optional[RevokedTokenModel]:
        """Retrieve a revoked token record by token string."""
        return (
            self.db.query(RevokedTokenModel)
            .filter(RevokedTokenModel.token == token)
            .first()
        )
