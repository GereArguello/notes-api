from fastapi import status
from app.core.enums import DifficultyLevel

def test_update_subject_should_return_200(client, user_login, create_subject):
    token = user_login["access_token"]
    subject = create_subject(token)

    subj_id = subject["id"]

    data = {
            "name": "Materia 200",
            "description": "blablabla",
            "difficulty": DifficultyLevel.VERY_HARD
    }

    response = client.patch(f"/subjects/{subj_id}",
                            headers={"Authorization": f"Bearer {token}"},
                            json=data)
    assert response.status_code == status.HTTP_200_OK

def test_update_subject_should_modify_fields(client, user_login, create_subject):
    token = user_login["access_token"]
    subject = create_subject(token)

    data = {
        "name": "Nueva materia",
        "description": "Nueva descripción",
        "difficulty": DifficultyLevel.HARD
    }

    response = client.patch(
        f"/subjects/{subject['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )

    body = response.json()

    assert body["name"] == data["name"]
    assert body["description"] == data["description"]
    assert body["difficulty"] == data["difficulty"]

def test_update_subject_partial_update(client, user_login, create_subject):
    token = user_login["access_token"]
    subject = create_subject(token)

    data = {
        "name": "Solo nombre"
    }

    response = client.patch(
        f"/subjects/{subject['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )

    body = response.json()

    assert body["name"] == "Solo nombre"
    assert body["description"] == subject["description"]  # no cambia

def test_update_subject_should_fail_if_other_user_subject(
    client, user_login, create_subject
):
    token_user1 = user_login["access_token"]
    subject = create_subject(token_user1)

    # Crear segundo usuario
    user_data = {
        "first_name": "Juan",
        "last_name": "Perez",
        "email": "otro@example.com",
        "password": "12345678",
        "password2": "12345678"
    }

    client.post("/users/", json=user_data)

    # Login segundo usuario
    login_response = client.post("/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })

    token_user2 = login_response.json()["access_token"]

    response = client.patch(
        f"/subjects/{subject['id']}",
        headers={"Authorization": f"Bearer {token_user2}"},
        json={"name": "Hack"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_subject_should_return_409_if_name_exists(
    client, user_login, create_subject
):
    token = user_login["access_token"]

    subject1 = create_subject(token, name="Materia 1")
    subject2 = create_subject(token, name="Materia 2")

    response = client.patch(
        f"/subjects/{subject2['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Materia 1"}
    )

    assert response.status_code == status.HTTP_409_CONFLICT