from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from robbot.config.settings import settings

# Engine configured to use DATABASE_URL (Postgres). For local/dev use docker-compose Postgres service.
# Do NOT call Base.metadata.create_all() in production; use Alembic migrations instead.
engine = create_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
