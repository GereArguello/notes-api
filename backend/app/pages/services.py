from fastapi import status, HTTPException
from sqlmodel import select
from sqlalchemy import func

from app.core.database import SessionDep
from app.pages.models import Page
from app.topics.models import Topic

def get_max_order_or_0(session: SessionDep, topic_id: int):
    max_order = session.exec(
        select(func.max(Page.sort_order))
        .where(Page.topic_id == topic_id)
    ).one()

    return max_order or 0

def get_page_or_404(session: SessionDep, page_id: int, topic: Topic):
    page = session.exec(
        select(Page)
        .where(Page.id == page_id, Page.topic_id == topic.id)
    ).first()

    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Página no encontrada"
        )
    return page

def get_pages_to_reorder(
    session: SessionDep,
    topic_id: int,
    old_order: int,
    new_order: int
) -> list[Page]:

    if new_order > old_order:
        return session.exec(
            select(Page).where(
                Page.topic_id == topic_id,
                Page.sort_order > old_order,
                Page.sort_order <= new_order
            )
        ).all()

    return session.exec(
        select(Page).where(
            Page.topic_id == topic_id,
            Page.sort_order >= new_order,
            Page.sort_order < old_order
        )
    ).all()
