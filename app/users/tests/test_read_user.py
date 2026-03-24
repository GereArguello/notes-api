from fastapi import status

def test_read_me_success(client, user_login):
    token = user_login["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert "email" in body
    assert "id" in body

def test_read_me_without_token_should_fail(client):
    response = client.get("/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_read_me_with_invalid_token_should_fail(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer token_invalido"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED