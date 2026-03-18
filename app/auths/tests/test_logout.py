from fastapi import status

def test_logout_success(client, user_login):
    refresh_token = user_login["refresh_token"]

    response = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_should_fail_if_uses_access_token(client, user_login):
    access_token = user_login["access_token"]

    response = client.post(
        "/auth/logout",
        json={"refresh_token": access_token}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Token inválido"

def test_logout_should_fail_with_previously_logout(client, user_login):
    refresh_token = user_login["refresh_token"]

    response1 = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token}
    )
    assert response1.status_code == status.HTTP_204_NO_CONTENT

    response2 = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token}
    )
    assert response2.status_code == status.HTTP_401_UNAUTHORIZED
    assert response2.json()["detail"] == "Token revocado"

def test_refresh_should_fail_after_logout(client, user_login):
    refresh_token = user_login["refresh_token"]

    # logout
    client.post("/auth/logout", json={"refresh_token": refresh_token})

    # intentar refresh
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Token revocado"