from sqlmodel import select
from sqlalchemy import func

from app.core.database import SessionDep
from app.pages.models import Page

def get_max_order_or_0(session: SessionDep, topic_id: int):
    max_order = session.exec(
        select(func.max(Page.sort_order))
        .where(Page.topic_id == topic_id)
    ).one()

    return max_order or 0