from fastapi import status
from sqlmodel import select
from datetime import timedelta
from app.core.security import create_access_token, create_refresh_token
from app.users.models import User

#----- TESTS PARA TOKEN DE ACCESO -----#
def test_should_fail_if_token_is_missing(client):
    response = client.get(
        "/users/me"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_should_return_401_if_token_is_malformed(client):
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer asd1234"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_token_allows_access_to_protected_endpoint(client, user_login):
    token = user_login["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

def test_should_return_401_if_token_expired(client, created_user, session):
    customer_email = created_user["email"]
    user = session.exec(select(User).where(User.email == customer_email)).first()

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=-1)
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    body = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert body["detail"] == "Token inválido o expirado"

#----- TESTS PARA TOKEN DE REFRESCO -----#
    
def test_refresh_returns_new_tokens(client, user_login):
    refresh_token = user_login["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"

def test_refresh_fails_if_token_expired(client, created_user, session):
    user = session.exec(
        select(User).where(User.email == created_user["email"])
    ).first()

    expired_token = create_refresh_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(minutes=-1)
    )

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": expired_token}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_refresh_fails_if_token_is_not_refresh(client, user_login):
    access_token = user_login["access_token"]

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": access_token}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_refresh_token_cannot_be_reused(client, user_login):
    refresh_token = user_login["refresh_token"]

    # primer uso (válido)
    response1 = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response1.status_code == status.HTTP_200_OK

    # segundo uso (debería fallar)
    response2 = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response2.status_code == status.HTTP_401_UNAUTHORIZED