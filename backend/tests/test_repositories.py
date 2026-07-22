import pytest
from backend.database import init_db, get_session, Base
from backend.repositories import UserRepository, PredictionRepository
from sqlalchemy import create_engine

@pytest.fixture(scope="module")
def db_session():
    # Use SQLite for repository tests to keep them fast and independent
    init_db("sqlite:///:memory:")
    engine = get_session().get_bind()
    Base.metadata.create_all(engine)
    session = get_session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_user_repository_create(db_session):
    repo = UserRepository(db_session)
    user = repo.get_or_create("clerk_123")
    assert user is not None
    assert user.clerk_id == "clerk_123"

def test_prediction_repository_save(db_session):
    user_repo = UserRepository(db_session)
    user = user_repo.get_or_create("clerk_123")
    
    pred_repo = PredictionRepository(db_session)
    
    results = {
        "heart": 20.0,
        "diabetes": 10.0,
        "kidney": 5.0,
        "health_condition": {"Healthy": 80.0},
        "scores_detail": {},
        "clinical_scores": {},
        "used_defaults": []
    }
    inputs = {"age": 45}
    
    pred = pred_repo.save_prediction(user.id, results, inputs)
    assert pred.id is not None
    assert pred.heart_risk == 20.0
    
    history, total = pred_repo.get_history_by_user(user.id)
    assert total == 1
    assert len(history) == 1
    assert history[0].id == pred.id
