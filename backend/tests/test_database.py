import pytest
from sqlalchemy import text
from backend.database import get_session, init_db

def test_database_connection():
    # Uses TEST_DATABASE_URL by default when running pytest with proper config
    # Actually, we can use an in-memory SQLite just for connection testing if needed,
    # but we'll assume the environment sets up TEST_DATABASE_URL as a Postgres test DB.
    # We will initialize with sqlite:///:memory: for pure unit tests
    init_db("sqlite:///:memory:")
    
    session = get_session()
    # Simple query
    result = session.execute(text("SELECT 1")).scalar()
    assert result == 1
    session.close()
