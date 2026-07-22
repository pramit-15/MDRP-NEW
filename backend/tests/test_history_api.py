import pytest
from backend.app.factory import create_app
from backend.database import Base, init_db, get_session

@pytest.fixture(scope="module")
def app():
    # Ensure config has testing setup
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE_URL": "sqlite:///:memory:"
    })
    
    with app.app_context():
        init_db("sqlite:///:memory:")
        engine = get_session().get_bind()
        Base.metadata.create_all(engine)
        yield app
        Base.metadata.drop_all(engine)

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

def test_history_unauthorized(client):
    response = client.get("/api/v1/history")
    assert response.status_code == 401

# Note: mocking auth middleware to test the actual history endpoints requires
# overriding g.user or using a test token. We assume the auth tests cover auth.
