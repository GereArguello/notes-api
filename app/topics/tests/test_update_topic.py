from fastapi import status

def test_update_topic_should_return_200(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Topic actualizado"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["name"] == "Topic actualizado"
    assert body["updated_at"] is not None
    assert body["id"] == topic_id
    assert body["subject_id"] == subject_id

def test_update_topic_should_return_404_if_not_exists(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/9999",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Nuevo"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_topic_should_fail_if_other_user(client, user_with_topic, create_user, login_user):
    # topic del user 1
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    # user 2
    user2 = create_user(email="otro@test.com")
    token2 = login_user(user2["email"], user2["raw_password"])

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"name": "Hack"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_topic_should_return_409_if_name_exists(client, user_with_topic, create_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    # Crear otro topic con el nombre objetivo
    create_topic(token, subject_id, name="Duplicado")

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Duplicado"}
    )

    assert response.status_code == status.HTTP_409_CONFLICT

def test_update_topic_should_fail_if_empty_payload(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_update_topic_should_not_modify_if_same_name(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]
    topic_name = user_with_topic["topic"]["name"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": topic_name}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["name"] == topic_name