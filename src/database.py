import logging
import os
from pathlib import Path
from typing import Generator

from sqlmodel import create_engine, Session, SQLModel


logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{Path(__file__).parent.parent}/database.db")

engine = create_engine(DATABASE_URL)


def create_db_and_tables() -> None:
    """Create the database and tables."""
    logger.info("Creating the database and tables")
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get a session for the database."""
    logger.info("Getting a session for the database")
    with Session(engine) as session:
        yield session
