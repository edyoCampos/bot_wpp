"""Database session management."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from robbot.infra.db.base import SessionLocal


@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    """
    Get synchronous database session with context manager.
    
    Yields:
        SQLAlchemy Session
        
    Example:
        with get_sync_session() as session:
            # Use session
            session.query(Model).all()
            session.commit()
    """
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session for FastAPI dependency injection.
    
    Yields:
        SQLAlchemy Session
        
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
