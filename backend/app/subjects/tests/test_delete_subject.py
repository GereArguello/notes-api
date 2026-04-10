from fastapi import status
from sqlmodel import select
from app.topics.models import Topic
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



def test_delete_subject_should_delete_topics(session, client, user_with_topics):
    token = user_with_topics["access_token"]
    subject_id = user_with_topics["subject"]["id"]

    topics_before = session.exec(select(Topic)).all()
    assert len(topics_before) > 0

    response = client.delete(
        f"/subjects/{subject_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Intentar obtener topics
    response = client.get(
        f"/subjects/{subject_id}/topics",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    topics_after = session.exec(select(Topic)).all()
    assert len(topics_after) == 0