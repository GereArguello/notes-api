from sqlmodel import select
from app.core.database import SessionDep
from app.page_tags.models import PageTagLink

def attach_tag_to_page(session: SessionDep, page_id: int, tag_id: int):
    existing_link = session.exec(
        select(PageTagLink).where(
            PageTagLink.page_id == page_id,
            PageTagLink.tag_id == tag_id
        )
    ).first()

    if not existing_link:
        session.add(PageTagLink(page_id=page_id, tag_id=tag_id))