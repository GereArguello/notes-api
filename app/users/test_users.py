from fastapi import status
from app.users.models import User

def test_should_fail_if_passwords_dont_match(client):
    data = {
        "first_name": "Pedro",
        "last_name": "Sanchez",
        "email": "test@example.com",
        "password": "12345678",
        "password2": "87654321"
    }

    response = client.post("/users/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"] == "Las contraseñas no coinciden"

def test_should_fail_if_email_already_exists(client, create_user):
    user = create_user("test@example.com")
    data = {
        "first_name": "Pepe",
        "last_name": "Sanchez",
        "email": user["email"],
        "password": "12345678",
        "password2": "12345678"
    }


    response = client.post("/users/", json=data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "El email ya está registrado"

def test_should_create_user_successfully(client):
    data = {
        "first_name": "Pepe",
        "last_name": "Sanchez",
        "email": "newuser@example.com",
        "password": "12345678",
        "password2": "12345678"
    }

    response = client.post("/users/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()

    assert body["email"] == data["email"]
    assert body["first_name"] == data["first_name"]

    # Muy importante: asegurarse que NO devuelve el password
    assert "password" not in body
    assert "password_hash" not in body
    assert "id" in body

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

def test_deactivate_user_success(client, user_login):
    token = user_login["access_token"]

    response = client.patch(
        "/users/me/deactivate",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_deactivate_user_sets_deleted_at(client, user_login):
    token = user_login["access_token"]

    # Desactivar usuario
    client.patch(
        "/users/me/deactivate",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Intentar acceder a /me -> debería fallar
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_delete_user_success(client, user_login):
    token = user_login["access_token"]

    response = client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_deleted_user_cannot_access_protected_routes(client, user_login):
    token = user_login["access_token"]

    # eliminar usuario
    client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    # intentar acceder a /me
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_delete_user_removes_from_db(client, user_login, session):
    token = user_login["access_token"]

    # obtener id antes
    me = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    ).json()

    user_id = me["id"]

    # eliminar
    client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    # verificar en DB
    user = session.get(User, user_id)

    assert user is None