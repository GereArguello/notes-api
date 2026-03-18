from fastapi import status

def test_logout_success(user_login):
    client = user_login["client"]
    response = client.post(
        "/auth/logout",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_should_fail_if_refresh_token_is_invalid(user_login):
    client = user_login["client"]
    client.cookies.set("refresh_token", "fake_token")

    response = client.post("/auth/logout")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_logout_should_fail_with_previously_logout(user_login):
    client = user_login["client"]
    response1 = client.post(
        "/auth/logout",
    )
    assert response1.status_code == status.HTTP_204_NO_CONTENT

    response2 = client.post(
        "/auth/logout",
    )
    assert response2.status_code == status.HTTP_401_UNAUTHORIZED
    assert response2.json()["detail"] == "Token inválido"

def test_refresh_should_fail_after_logout(user_login):
    client = user_login["client"]
    # logout
    client.post("/auth/logout")

    # intentar refresh
    response = client.post(
        "/auth/refresh",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Token inválido"