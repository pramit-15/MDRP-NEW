from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from backend.database.database import get_session, SessionLocal

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
