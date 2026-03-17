from fastapi import status
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session
from app.core.database import get_session
from app.main import app

sqlite_url = "sqlite:///:memory:"

engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="created_user")
def created_user(client):
    password = "password123"

    payload = {
        "first_name": "Pedro",
        "last_name": "Sanchez",
        "email": "Pedro@gmail.com",
        "password": password,
        "password2": password
    }

    response = client.post("/users", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    data["raw_password"] = password
    return data