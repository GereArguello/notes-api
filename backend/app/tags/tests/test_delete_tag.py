from fastapi import status
from sqlmodel import select
from app.page_tags.models import PageTagLink
from app.tags.models import Tag

def test_delete_page_tag_should_return_204(session, client, user_with_tag):
    token = user_with_tag["access_token"]
    subject_id = user_with_tag["subject_id"]
    topic_id = user_with_tag["topic_id"]
    page_id = user_with_tag["page_id"]
    tag_id = user_with_tag["tag"]["id"]

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags/{tag_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # validar DB: ya no existe la relación
    link = session.exec(
        select(PageTagLink).where(
            PageTagLink.page_id == page_id,
            PageTagLink.tag_id == tag_id
        )
    ).first()

    assert link is None

def test_delete_page_tag_should_not_delete_tag(client, session, user_with_tag):
    token = user_with_tag["access_token"]
    subject_id = user_with_tag["subject_id"]
    topic_id = user_with_tag["topic_id"]
    page_id = user_with_tag["page_id"]
    tag_id = user_with_tag["tag"]["id"]

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags/{tag_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    #  el tag sigue existiendo
    tag = session.get(Tag, tag_id)
    assert tag is not None

def test_delete_page_tag_should_return_404_if_not_linked(client, user_with_tag):
    token = user_with_tag["access_token"]
    subject_id = user_with_tag["subject_id"]
    topic_id = user_with_tag["topic_id"]
    page_id = user_with_tag["page_id"]

    response = client.delete(
        f"/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags/999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND