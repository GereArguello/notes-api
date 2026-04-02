from fastapi import status, HTTPException
from sqlmodel import select
from sqlalchemy import func
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

def get_max_order_or_0(session: SessionDep, subject_id: int):
    max_order = session.exec(
        select(func.max(Topic.sort_order))
        .where(Topic.subject_id == subject_id)
    ).one()

    return max_order or 0

def get_topics_to_reorder(
    session: SessionDep,
    subject: Subject,
    old_order: int,
    new_order: int
) -> list[Topic]:

    if new_order > old_order:
        return session.exec(
            select(Topic).where(
                Topic.subject_id == subject.id,
                Topic.sort_order > old_order,
                Topic.sort_order <= new_order
            )
        ).all()

    return session.exec(
        select(Topic).where(
            Topic.subject_id == subject.id,
            Topic.sort_order >= new_order,
            Topic.sort_order < old_order
        )
    ).all()

def shift_down(session: SessionDep, topics: list[Topic]):
        for t in sorted(topics, key=lambda t: t.sort_order):
            t.sort_order -= 1
            session.add(t)
            session.flush()
        
    
def shift_up(session: SessionDep, topics: list[Topic]):       
        for t in sorted(topics, key=lambda t: t.sort_order, reverse=True):
            t.sort_order += 1
            session.add(t)
            session.flush()
        

