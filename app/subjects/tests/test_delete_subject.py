from fastapi import status

def test_delete_subject_should_return_204(client, user_login, create_subject):
    token = user_login["access_token"]
    subject = create_subject(token)

    subj_id = subject["id"]

    response = client.delete(
        f"/subjects/{subj_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_subject_should_return_404_if_not_exists(client, user_login, create_subject):
    token = user_login["access_token"]
    create_subject(token)

    response = client.delete(
        f"/subjects/999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_subject_should_return_404_if_other_user_subject(
    client, user_login, create_subject
):
    subject = create_subject(user_login["access_token"])

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

    response = client.delete(
        f"/subjects/{subject['id']}",
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND