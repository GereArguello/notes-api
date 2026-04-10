from fastapi import status

def test_create_page_should_return_200(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.post(
        f"/subjects/{subject_id}/topics/{topic_id}/pages",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Página 1",
            }
    )

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()

    assert body["title"] == "Página 1"
    assert body["sort_order"] == 1
    assert body["created_at"] is not None
    assert body["updated_at"] is None
    assert body["topic_id"] == topic_id

def test_create_page_should_return_404_if_topic_does_not_exists(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]

    response = client.post(
        f"/subjects/{subject_id}/topics/999/pages",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Página 1",
            "content": "asdasdasd"
            }
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_page_should_return_404_if_subject_does_not_exists(client, user_with_topic):
    token = user_with_topic["access_token"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.post(
        f"/subjects/999/topics/{topic_id}/pages",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Página 1",
            "content": "asdasdasd"
            }
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_page_should_fail_if_topic_not_in_subject(client, user_login, create_subject, create_topic):
    token = user_login["access_token"]

    # Crear dos subjects
    subject1 = create_subject(token)
    subject2 = create_subject(token, name="Materia 2")

    # Crear un topic en el subject2
    topic = create_topic(token, subject2["id"], "Tema de ejemplo")

    # Intentar usar ese topic dentro de subject1 (incorrecto)
    response = client.post(
        f"/subjects/{subject1['id']}/topics/{topic['id']}/pages",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Página inválida",
            "content": "contenido"
        }
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_page_should_fail_if_user_not_owner(client, create_user, login_user, create_subject, create_topic):
    # Usuario 1
    user1 = create_user(email="user1@test.com")
    token1 = login_user(email=user1["email"], password=user1["raw_password"])

    subject = create_subject(token1)
    topic = create_topic(token1, subject["id"], name="Tema de ejemplo")

    # Usuario 2
    user2 = create_user(email="user2@test.com")
    token2 = login_user(email=user2["email"], password=user2["raw_password"])

    # Usuario 2 intenta crear página en recurso de user1
    response = client.post(
        f"/subjects/{subject['id']}/topics/{topic['id']}/pages",
        headers={"Authorization": f"Bearer {token2}"},
        json={
            "title": "No autorizado",
            "content": "contenido"
        }
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_page_should_increment_sort_order(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    # Crear múltiples páginas
    for i in range(1, 6):
        response = client.post(
            f"/subjects/{subject_id}/topics/{topic_id}/pages",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": f"Página {i}",
                "content": "contenido"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()

        assert body["sort_order"] == i