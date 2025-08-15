from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from core.config import settings

engine = create_engine(settings.db_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
