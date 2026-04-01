from fastapi import status


## TESTS PARA LISTS TOPICS ##

def test_list_topics_should_return_401_if_no_token(client, user_with_topic):
    subject_id = user_with_topic["subject"]["id"]

    response = client.get(f"/subjects/{subject_id}/topics")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_list_topics_should_return_404_if_other_user_subject(
    client, user_with_topic, create_user, login_user
):
    subject = user_with_topic["subject"]

    # otro usuario
    user = create_user(email="otro@test.com")
    token = login_user(user["email"],user["raw_password"])

    response = client.get(
        f"/subjects/{subject['id']}/topics",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_topics_should_return_404_if_subject_does_not_exists(client, user_with_topic):
    token = user_with_topic["access_token"]

    response = client.get(
        "/subjects/999/topics",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_topics_should_return_200(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]

    response = client.get(
        f"/subjects/{subject_id}/topics",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "size" in body

    assert len(body["items"]) == 1
    assert body["items"][0]["subject_id"] == subject_id


def test_list_topics_should_return_empty_list_if_no_topics(
    client, user_login, create_subject
):
    token = user_login["access_token"]
    subject = create_subject(token)

    response = client.get(
        f"/subjects/{subject['id']}/topics",
        headers={"Authorization": f"Bearer {token}"}
    )

    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body["items"] == []
    assert body["total"] == 0

def test_list_topics_should_paginate_results(
    client, user_with_topic, create_topic
):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]

    # crear varios topics
    for i in range(5):
        create_topic(token, subject_id, name=f"topic {i}")

    response = client.get(
        f"/subjects/{subject_id}/topics?page=1&size=3",
        headers={"Authorization": f"Bearer {token}"}
    )

    body = response.json()

    assert len(body["items"]) == 3

def test_list_topics_should_only_return_topics_from_subject(
    client, user_with_topic, create_topic, create_subject
):
    token = user_with_topic["access_token"]
    subject_1 = user_with_topic["subject"]

    subject_2 = create_subject(token, name="Materia 2")

    create_topic(token, subject_1["id"], name="topic 1")
    create_topic(token, subject_2["id"], name="topic 2")

    response = client.get(
        f"/subjects/{subject_1['id']}/topics",
        headers={"Authorization": f"Bearer {token}"}
    )

    body = response.json()

    for topic in body["items"]:
        assert topic["subject_id"] == subject_1["id"]

## TESTS PARA READ TOPIC ##

def test_read_topic_should_return_200(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.get(
        f"/subjects/{subject_id}/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["id"] == topic_id
    assert body["subject_id"] == subject_id

def test_read_topic_should_return_401_if_no_token(client, user_with_topic):
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.get(f"/subjects/{subject_id}/topics/{topic_id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_read_topic_should_return_404_if_topic_does_not_exist(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]

    response = client.get(
        f"/subjects/{subject_id}/topics/999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_read_topic_should_return_404_if_topic_not_in_subject(
    client, user_with_topic, create_topic, create_subject
):
    token = user_with_topic["access_token"]
    subject_1 = user_with_topic["subject"]

    subject_2 = create_subject(token, name="Materia 2")
    topic_2 = create_topic(token, subject_2["id"], name="otro topic")

    response = client.get(
        f"/subjects/{subject_1['id']}/topics/{topic_2['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_read_topic_should_return_404_if_other_user(
    client, user_with_topic, create_user, login_user
):
    subject = user_with_topic["subject"]
    topic = user_with_topic["topic"]

    user = create_user(email="otro@test.com")
    token = login_user(user["email"], user["raw_password"])

    response = client.get(
        f"/subjects/{subject['id']}/topics/{topic['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_read_topic_should_update_last_viewed_at(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.get(
        f"/subjects/{subject_id}/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body["last_viewed_at"] is not None