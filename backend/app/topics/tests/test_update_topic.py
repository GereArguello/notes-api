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


## TESTS PARA REORDENAR TEMAS

def test_reorder_topic_move_down(client, user_with_topics):
    token = user_with_topics["access_token"]
    subject_id = user_with_topics["subject"]["id"]
    topics = user_with_topics["topics"]


    topic_to_move = topics[1] #Sort_order = 2

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_to_move['id']}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": 8}
    )

    assert response.status_code == status.HTTP_200_OK

    # Volver a pedir la lista
    response = client.get(
        f"/subjects/{subject_id}/topics",
        headers={"Authorization": f"Bearer {token}"}
    )

    items = response.json()["items"]

    orders = [t["sort_order"] for t in items]

    assert orders == [i+1 for i in range(10)]  # siempre consistente
    assert any(t["id"] == topic_to_move["id"] and t["sort_order"] == 8 for t in items)

def test_reorder_topic_move_up(client, user_with_topics):
    token = user_with_topics["access_token"]
    subject_id = user_with_topics["subject"]["id"]
    topics = user_with_topics["topics"]


    topic_to_move = topics[7] #Sort_order = 8

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic_to_move['id']}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": 2}
    )

    assert response.status_code == status.HTTP_200_OK

    # Volver a pedir la lista
    response = client.get(
        f"/subjects/{subject_id}/topics",
        headers={"Authorization": f"Bearer {token}"}
    )

    items = response.json()["items"]

    orders = [t["sort_order"] for t in items]

    assert orders == [i+1 for i in range(10)]  # siempre consistente
    assert any(t["id"] == topic_to_move["id"] and t["sort_order"] == 2 for t in items)

def test_reorder_topic_same_position(client, user_with_topics):
    token = user_with_topics["access_token"]
    subject_id = user_with_topics["subject"]["id"]
    topics = user_with_topics["topics"]

    topic = topics[3]  

    response = client.patch(
        f"/subjects/{subject_id}/topics/{topic['id']}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": topic["sort_order"]}
    )

    assert response.status_code == status.HTTP_200_OK
    
def test_reorder_topic_out_of_range_should_return_400(client, user_with_topics):
    token = user_with_topics["access_token"]
    subject_id = user_with_topics["subject"]["id"]
    topics = user_with_topics["topics"]

    topic = topics[0]  # cualquier topic válido

    # Caso 1: menor que 1
    response_low = client.patch(
        f"/subjects/{subject_id}/topics/{topic['id']}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": 0}
    )

    assert response_low.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # Caso 2: mayor al máximo
    response_high = client.patch(
        f"/subjects/{subject_id}/topics/{topic['id']}/re-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"sort_order": len(topics) + 1}
    )

    assert response_high.status_code == status.HTTP_400_BAD_REQUEST
    assert response_high.json()["detail"] == "Número de orden fuera de rango"