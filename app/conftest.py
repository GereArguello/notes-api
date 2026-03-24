from fastapi import status
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session
from app.core.database import get_session
from app.core.config import settings
from app.core.enums import DifficultyLevel
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


#Fixtures desacoplados: retornan funciones para luego poder variar con los datos

@pytest.fixture
def create_user(client):
    def _create_user(email: str):
        password = "password123"

        payload = {
            "first_name": "Pedro",
            "last_name": "Sanchez",
            "email": email,
            "password": password,
            "password2": password
        }

        response = client.post("/users", json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        data["raw_password"] = password
        return data

    return _create_user

@pytest.fixture
def login_user(client):
    def _login_user(email: str, password: str):
        response = client.post(
            "/auth/login",
            data={
                "username": email,
                "password": password
            }
        )
        assert response.status_code == status.HTTP_200_OK

        return response.json()["access_token"]

    return _login_user

# Para tests simples
@pytest.fixture(name="user_login")
def user_login(create_user, login_user):
    user = create_user("test@gmail.com")
    token = login_user(user["email"], user["raw_password"])

    return {
        "access_token": token,
        "user": user
    }

@pytest.fixture
def create_subject(client):
    def _create_subject(token, name="Materia 1", data=None):
        if not data:
            data = {
                "name": name,
                "description": "Materia de ejemplo",
                "difficulty": DifficultyLevel.MEDIUM,
            }

        response = client.post(
            "/subjects",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )

        assert response.status_code == status.HTTP_201_CREATED
        return response.json()

    return _create_subject