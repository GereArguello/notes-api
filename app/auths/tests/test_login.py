from fastapi import status

def test_user_can_login(client, created_user):
    response = client.post(
        "/auth/login",
        data = {
            "username": created_user["email"],
            "password": created_user["raw_password"]
        }
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

def test_login_should_fail_if_credentials_are_invalid(client, created_user):
    response = client.post(
        "/auth/login",
        data={
            "username": created_user["email"],
            "password": "wrong password"
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Usuario o contraseña incorrectos"

def test_login_should_fail_if_payload_is_invalid(client):
    response = client.post(
        "/auth/login",
        data={
            "password": "wrong password"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT