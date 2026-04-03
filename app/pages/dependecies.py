from fastapi import Depends, status, HTTPException
from sqlmodel import select
from app.core.database import SessionDep
from app.subjects.dependencies import get_user_subject
from app.subjects.models import Subject
from app.topics.models import Topic

def get_user_topic(
    topic_id: int,
    session: SessionDep,
    subject: Subject = Depends(get_user_subject)
):
    topic = session.exec(
        select(Topic).where(
            Topic.id == topic_id,
            Topic.subject_id == subject.id
        )
    ).first()

    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= "El tema no existe")

    return topic