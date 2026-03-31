from sqlmodel import select
from app.topics.models import Topic
from app.core.database import SessionDep

def existing_topic(session: SessionDep, topic: Topic, subject_id: int):
    return session.exec(
        select(Topic).where(
            Topic.subject_id == subject_id,
            Topic.name == topic.name
        )
    ).first()
