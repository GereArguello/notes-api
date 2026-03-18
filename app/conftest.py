from fastapi import status
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session
from app.core.database import get_session
from app.core.config import settings
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

@pytest.fixture(autouse=True)
def override_settings():
    settings.COOKIE_SECURE = False

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

@pytest.fixture(name="user_login")
def user_login(client, created_user):
    response = client.post(
        "/auth/login",
        data={
            "username": created_user["email"],
            "password": created_user["raw_password"]
        }
    )
    assert response.status_code == 200
    return {
        "client": client,
        "access_token": response.json()["access_token"]
    }