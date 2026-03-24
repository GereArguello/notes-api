from fastapi import status

def test_update_user_success(client, user_login):
    token = user_login["access_token"]

    data = {
        "first_name": "NuevoNombre"
    }

    #  Obtener estado inicial
    before = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    ).json()

    # Update
    response = client.patch(
        "/users/me",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["first_name"] == "NuevoNombre"
    assert body["last_name"] == before["last_name"]

def test_update_user_without_data_should_fail(client, user_login):
    token = user_login["access_token"]

    response = client.patch(
        "/users/me",
        json={}, 
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No se enviaron datos para actualizar"

def test_update_password_success(client, user_login):
    token = user_login["access_token"]

    data = {
        "current_password": "password123",
        "new_password": "password1234",
        "new_password2": "password1234"
    }

    response = client.patch(
        "/users/me/password",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Contraseña actualizada correctamente"

def test_update_password_should_fail_if_passwords_dont_match(client, user_login):
    token = user_login["access_token"]

    data = {
        "current_password": "password123",
        "new_password": "87654321",
        "new_password2": "00000000"
    }

    response = client.patch(
        "/users/me/password",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"] == "Las contraseñas no coinciden"

def test_update_password_should_fail_if_current_password_is_wrong(client, user_login):
    token = user_login["access_token"]

    data = {
        "current_password": "wrongpassword",
        "new_password": "87654321",
        "new_password2": "87654321"
    }

    response = client.patch(
        "/users/me/password",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Contraseña actual incorrecta"

def test_update_password_should_fail_if_new_password_is_same(client, user_login):
    token = user_login["access_token"]

    data = {
        "current_password": "password123",
        "new_password": "password123",
        "new_password2": "password123"
    }

    response = client.patch(
        "/users/me/password",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "La nueva contraseña no puede ser igual a la actual"

def test_update_password_should_revoke_all_refresh_tokens(client, user_login):
    access_token = user_login["access_token"]

    # Cambiar contraseña
    response = client.patch(
        "/users/me/password",
        json={
            "current_password": "password123",
            "new_password": "87654321",
            "new_password2": "87654321"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    # Intentar usar refresh token viejo -> debe fallar
    response_refresh = client.post(
        "/auth/refresh",
    )

    assert response_refresh.status_code == status.HTTP_401_UNAUTHORIZED