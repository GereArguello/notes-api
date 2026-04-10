from fastapi import status

## TESTS PARA UPDATE PAGE ## 

def test_update_page_should_return_200(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Página 2"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["title"] != user_with_page["page"]["title"]
    assert body["updated_at"] is not None

def test_update_page_should_return_404_if_not_exists(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/9999",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Nueva página"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_page_should_return_404_if_page_is_not_user(client, user_with_page, create_user, login_user):
    other_user = create_user(email="ejemplo@ejemplo.com")
    token = login_user(other_user["email"], other_user["raw_password"])

    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Hack intento"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_page_should_not_change_if_same_data(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]
    original_title = user_with_page["page"]["title"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": original_title}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["title"] == original_title

def test_update_page_multiple_fields(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Nuevo título",
            "content": "Nuevo contenido"
        }
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["title"] == "Nuevo título"
    assert body["content"] == "Nuevo contenido"


## TESTS PARA RE-ORDER PAGE ##

def test_reorder_page_move_down_should_return_200(client, user_with_pages):
    token = user_with_pages["access_token"]
    subject_id = user_with_pages["subject_id"]
    topic_id = user_with_pages["topic_id"]

    page_1 = user_with_pages["pages"][0]  # sort_order = 1

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_1['id']}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": 3}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["sort_order"] == 3

def test_reorder_page_move_up_should_return_200(client, user_with_pages):
    token = user_with_pages["access_token"]
    subject_id = user_with_pages["subject_id"]
    topic_id = user_with_pages["topic_id"]

    page_3 = user_with_pages["pages"][2]  # sort_order = 3

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_3['id']}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": 1}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["sort_order"] == 1

def test_reorder_page_same_position_should_return_200(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page = user_with_page["page"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page['id']}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": page["sort_order"]}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["sort_order"] == page["sort_order"]

def test_reorder_page_out_of_range_should_return_400(client, user_with_pages):
    token = user_with_pages["access_token"]
    subject_id = user_with_pages["subject_id"]
    topic_id = user_with_pages["topic_id"]

    page = user_with_pages["pages"][0]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page['id']}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": 999}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_reorder_page_should_return_404_if_not_user(client, user_with_page, create_user, login_user):
    other_user = create_user(email="ejemplo@ejemplo.com")
    token = login_user(other_user["email"], other_user["raw_password"])

    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": 1}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_reorder_page_should_shift_other_pages(client, user_with_pages):
    token = user_with_pages["access_token"]
    subject_id = user_with_pages["subject_id"]
    topic_id = user_with_pages["topic_id"]

    page_1 = user_with_pages["pages"][0]  # order 1

    client.patch(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_1['id']}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": 3}
    )

    response = client.get(
        f"/subjects/{subject_id}/topics/{topic_id}/pages",
        headers={"Authorization": f"Bearer {token}"}
    )

    items = response.json()["items"]

    orders = [p["sort_order"] for p in items]

    assert sorted(orders) == list(range(1, len(items) + 1))