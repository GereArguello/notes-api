from fastapi import status

def test_create_topic_should_return_201(client, user_with_subject):
    token = user_with_subject["access_token"]
    subject_id = user_with_subject["subject"]["id"]

    data = {
        "name": "topic nuevo"
    }

    response = client.post(
        f"/subjects/{subject_id}/topics",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )

    body = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert body["name"] == data["name"]
    assert body["subject_id"] == subject_id

def test_create_topic_should_return_404_if_subject_does_not_exist(client, user_with_subject):
    token = user_with_subject["access_token"]

    data = {
        "name": "topic nuevo"
    }

    response = client.post(
        f"/subjects/999/topics",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_topic_should_return_404_if_subject_belongs_to_other_user(
    client, user_login, create_subject
):
    # Usuario A crea subject
    subject = create_subject(user_login["access_token"])

    # Usuario B
    other_user = client.post("/users/", json={
        "first_name": "Juan",
        "last_name": "Perez",
        "email": "otro@example.com",
        "password": "12345678",
        "password2": "12345678"
    }).json()

    login_other = client.post("/auth/login", data={
        "username": "otro@example.com",
        "password": "12345678"
    }).json()

    token = login_other["access_token"]

    response = client.post(
        f"/subjects/{subject['id']}/topics",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "topic"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_topic_should_fail_if_name_already_exists(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]

    data = {
        "name": user_with_topic["topic"]["name"]
    }

    response = client.post(
        f"/subjects/{subject_id}/topics",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Ya existe un tema con este nombre"

def test_create_topic_should_return_422_if_name_is_missing(client, user_with_subject):
    token = user_with_subject["access_token"]
    subject_id = user_with_subject["subject"]["id"]

    response = client.post(
        f"/subjects/{subject_id}/topics",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_create_topic_should_assign_incremental_sort_order(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]

    response = client.post(
        f"/subjects/{subject_id}/topics",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "otro topic"}
    )

    body = response.json()

    assert body["sort_order"] == 2