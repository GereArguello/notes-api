from fastapi import Depends
from app.core.database import SessionDep
from app.subjects.dependencies import get_user_subject
from app.subjects.models import Subject
from app.topics.services import get_topic_or_404

def get_user_topic(
    topic_id: int,
    session: SessionDep,
    subject: Subject = Depends(get_user_subject)
):
    topic = get_topic_or_404(session, subject, topic_id)

    return topic