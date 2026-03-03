"""Repository for managing revoked JWT tokens."""

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.revoked_token_model import RevokedTokenModel


class TokenRepository(BaseRepository[RevokedTokenModel]):
    """
    Repository to manage revoked tokens persistence.
    """

    def __init__(self, db: Session):
        super().__init__(db, RevokedTokenModel)

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
        q = self.db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token)
        exists_ = self.db.query(q.exists()).scalar()
        return bool(exists_)

    def get_by_token(self, token: str) -> RevokedTokenModel | None:
        """Retrieve a revoked token record by token string."""
        return self.db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()

