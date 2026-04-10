from fastapi import status
from sqlmodel import select
from app.pages.models import Page

def test_delete_page_should_return_204(client, user_with_page):
    token = user_with_page["access_token"]
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_page_should_return_404_if_not_exists(client, user_with_topic):
    token = user_with_topic["access_token"]
    subject_id = user_with_topic["subject"]["id"]
    topic_id = user_with_topic["topic"]["id"]

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/9999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_page_should_reorder_remaining_pages(client, session, user_with_pages):
    token = user_with_pages["access_token"]
    subject_id = user_with_pages["subject_id"]
    topic_id = user_with_pages["topic_id"]
    pages = user_with_pages["pages"]

    # Eliminamos una página intermedia y verificamos reorder completo
    page_to_delete = pages[1]  # (sort_order=2)

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_to_delete['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Volvemos a traer las páginas
    remaining_pages = session.exec(
        select(Page)
        .where(Page.topic_id == topic_id)
        .order_by(Page.sort_order)
    ).all()

    assert len(remaining_pages) == 4

    # Verificamos que quedaron ordenadas 1,2 (no 1,3)
    for i, page in enumerate(remaining_pages, start=1):
        assert page.sort_order == i

def test_delete_last_page_should_not_affect_others(client, session, user_with_pages):
    token = user_with_pages["access_token"]
    subject_id = user_with_pages["subject_id"]
    topic_id = user_with_pages["topic_id"]
    pages = user_with_pages["pages"]

    last_page = pages[-1]

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{last_page['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    remaining_pages = session.exec(
        select(Page)
        .where(Page.topic_id == topic_id)
        .order_by(Page.sort_order)
    ).all()

    # No debería haber cambios en orden
    for i, page in enumerate(remaining_pages, start=1):
        assert page.sort_order == i

def test_delete_page_should_not_allow_other_user(client, user_with_page, create_user, login_user):
    other_user = create_user(email="ejemplo@ejemplo.com")
    token = login_user(other_user["email"], other_user["raw_password"])
    subject_id = user_with_page["subject"]["id"]
    topic_id = user_with_page["topic"]["id"]
    page_id = user_with_page["page"]["id"]

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND