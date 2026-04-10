from fastapi import Depends
from app.core.database import SessionDep
from app.topics.dependencies import get_user_topic
from app.subjects.models import Subject
from app.pages.services import get_page_or_404

def get_user_page(
    page_id: int,
    session: SessionDep,
    topic: Subject = Depends(get_user_topic)
):
    page = get_page_or_404(session, page_id, topic)

    return page