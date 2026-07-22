from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.app.config import Config

engine = None
SessionLocal = None

def init_db(database_url: str = None):
    global engine, SessionLocal
    url = database_url or Config.DATABASE_URL
    
    # Pool size and max_overflow are good for production.
    if url.startswith("sqlite"):
        engine = create_engine(url)
    else:
        engine = create_engine(url, pool_size=5, max_overflow=10)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    SessionLocal = scoped_session(session_factory)

def get_engine():
    return engine

def get_session():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    return SessionLocal()
