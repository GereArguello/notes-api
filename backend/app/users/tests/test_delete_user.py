from fastapi import status
from app.users.models import User

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