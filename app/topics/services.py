from fastapi import status, HTTPException
from sqlmodel import select
from app.topics.models import Topic
from app.subjects.models import Subject
from app.core.database import SessionDep

def existing_topic(session: SessionDep, topic: Topic, subject_id: int):
    return session.exec(
        select(Topic).where(
            Topic.subject_id == subject_id,
            Topic.name == topic.name
        )
    ).first()

def get_topic_or_404(session: SessionDep, subject: Subject, topic_id: int):
    topic = session.exec(
        select(Topic)
        .where(
            Topic.id == topic_id,
            Topic.subject_id == subject.id
        )
    ).first()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El tema no existe"
        )

    return topic

