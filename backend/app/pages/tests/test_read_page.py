from fastapi import status

## TEST PARA LIST PAGE ## 

def test_list_pages_should_return_200(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]

    response = client.get(
        f"/subjects/{subject_id}/topics/{topic_id}/pages",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert "items" in body
    assert "total" in body
    assert body["total"] >= 1
    assert len(body["items"]) >= 1

def test_list_pages_should_return_empty_list(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.get(
        f"/subjects/{subject_id}/topics/{topic_id}/pages",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["items"] == []
    assert body["total"] == 0

def test_list_pages_should_return_sorted_by_order(
    client, user_login, create_subject, create_topic, create_page
):
    token = user_login["access_token"]

    subject = create_subject(token)
    topic = create_topic(token, subject["id"], name="Tema 1")

    # Crear varias páginas
    for i in range(1, 4):
        create_page(token, subject["id"], topic["id"], f"Página {i}")

    response = client.get(
        f"/subjects/{subject['id']}/topics/{topic['id']}/pages",
        headers={"Authorization": f"Bearer {token}"}
    )

    body = response.json()
    items = body["items"]

    assert len(items) == 3

    # Validar orden
    assert items[0]["sort_order"] == 1
    assert items[1]["sort_order"] == 2
    assert items[2]["sort_order"] == 3

def test_list_pages_should_fail_if_user_not_owner(
    client, create_user, login_user, create_subject, create_topic
):
    # Usuario 1
    user1 = create_user(email="user1@test.com")
    token1 = login_user(email=user1["email"], password=user1["raw_password"])

    subject = create_subject(token1)
    topic = create_topic(token1, subject["id"], "Tema 1")

    # Usuario 2
    user2 = create_user(email="user2@test.com")
    token2 = login_user(email=user2["email"], password=user2["raw_password"])

    response = client.get(
        f"/subjects/{subject['id']}/topics/{topic['id']}/pages",
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


## TEST PARA READ PAGE ##

def test_read_page_should_return_200(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.get(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["id"] == page_id
    assert body["topic_id"] == topic_id
    assert body["title"] is not None
    assert body["content"] is None
    assert body["created_at"] is not None
    assert body["last_viewed_at"] is not None

def test_read_page_should_return_404_if_page_not_exists(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.get(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_read_page_should_fail_if_page_not_in_topic(
    client, user_login, create_subject, create_topic, create_page
):
    token = user_login["access_token"]

    subject = create_subject(token)
    topic1 = create_topic(token, subject["id"], name="Topic 1")
    topic2 = create_topic(token, subject["id"], name="Topic 2")

    # Crear page en topic1
    page = create_page(token, subject["id"], topic1["id"], "Página 1")

    # Intentar acceder desde topic2
    response = client.get(
        f"/subjects/{subject['id']}/topics/{topic2['id']}/pages/{page['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_read_page_should_fail_if_user_not_owner(
    client, create_user, login_user, create_subject, create_topic, create_page
):
    # Usuario 1
    user1 = create_user(email="user1@test.com")
    token1 = login_user(email=user1["email"], password=user1["raw_password"])

    subject = create_subject(token1)
    topic = create_topic(token1, subject["id"], "Tema 1")
    page = create_page(token1, subject["id"], topic["id"], "Página 1")

    # Usuario 2
    user2 = create_user(email="user2@test.com")
    token2 = login_user(email=user2["email"], password=user2["raw_password"])

    response = client.get(
        f"/subjects/{subject['id']}/topics/{topic['id']}/pages/{page['id']}",
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND