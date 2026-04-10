from fastapi import status

def test_delete_topic_should_reorder_topics(client, user_with_topics):
    token = user_with_topics["access_token"]
    subject_id = user_with_topics["subject"]["id"]
    topics = user_with_topics["topics"]

    # Supongamos que borramos el topic con orden 2
    topic_to_delete = topics[1]  # sort_order = 2
    topic_id = topic_to_delete["id"]

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Obtener lista actualizada
    response = client.get(
        f"/subjects/{subject_id}/topics",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()["items"]

    # No debe existir el topic eliminado
    ids = [t["id"] for t in data]
    assert topic_id not in ids

    # Debe haber uno menos
    assert len(data) == len(topics) - 1

    # Los sort_order deben ser consecutivos (1,2,3,...)
    orders = [t["sort_order"] for t in data]
    assert orders == list(range(1, len(data) + 1))

def test_delete_topic_should_return_204(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_topic_should_return_404_if_not_exists(client, user_with_topics):
    token = user_with_topics["access_token"]
    subject_id = user_with_topics["subject"]["id"]

    response = client.delete(
        f"/subjects/{subject_id}/topics/9999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_topic_should_fail_if_other_user(
    client, user_with_topics, create_user, login_user
):
    # Crear segundo usuario
    create_user(email="otro@example.com")

    # Loguearlo
    other_token = login_user(
        email="otro@example.com",
        password="password123"
    )

    subject_id = user_with_topics["subject"]["id"]
    topic_id = user_with_topics["topics"][0]["id"]

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}",
        headers={"Authorization": f"Bearer {other_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND