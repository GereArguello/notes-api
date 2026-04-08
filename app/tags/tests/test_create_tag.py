from fastapi import status
from sqlmodel import select
from app.page_tags.models import PageTagLink

def test_create_tag_should_create_tag_and_associate_to_page(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.post(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "pyTHon"}
    )

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()

    assert body["name"] == "python"

    assert body["id"] is not None

def test_create_tag_should_reuse_existing_tag(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.post(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "pyTHon"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    tag_1 = response.json()

    response_2 = client.post(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "pyTHon"}
    )

    assert response_2.status_code == status.HTTP_201_CREATED
    tag_2 = response_2.json()

    # mismo tag_id (no duplicado)
    assert tag_1["id"] == tag_2["id"]

    # opcional pero claro
    assert tag_2["name"] == "python"

def test_create_tag_should_not_duplicate_page_tag_link(
    client, session, user_with_page
):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    # primer llamado
    client.post(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "python"}
    )

    # segundo llamado
    client.post(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "python"}
    )

    # verificamos DB directamente
    links = session.exec(
        select(PageTagLink).where(PageTagLink.page_id == page_id)
    ).all()

    assert len(links) == 1


def test_create_tag_should_return_404_if_page_not_exists(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]

    response = client.post(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/999/tags",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "python"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_tag_should_return_404_if_page_not_belongs_to_user(client, user_with_page, create_user, login_user):
    user = create_user(email="ejemplo@ejemplo.com")
    token = login_user(user["email"], user["raw_password"])

    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.post(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "pyTHon"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_tag_should_return_422_if_name_missing(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.post(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    