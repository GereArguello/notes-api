from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page

from app.core.database import SessionDep
from app.core.pagination import TopicPagination
from app.auths.dependencies import get_current_user
from app.users.models import User
from app.subjects.models import Subject
from app.subjects.dependencies import get_user_subject
from app.topics.models import Topic
from app.topics.schemas import TopicCreate, TopicRead
from app.topics.services import existing_topic

from app.utils import utc_now

router = APIRouter(tags=["topics"])


@router.post("/subjects/{subject_id}/topics", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
def create_topic(
    subject_id: int,
    topic: TopicCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    subject = session.get(Subject, subject_id)

    if not subject or subject.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La materia no existe"
        )

    # Validación previa
    topic_exists = existing_topic(session, topic, subject_id)

    if topic_exists:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un tema con este nombre"
        )
    
    db_topic = Topic(**topic.model_dump(), subject_id=subject_id)

    max_order = session.exec(
        select(func.max(Topic.sort_order))
        .where(Topic.subject_id == subject_id)
    ).one()

    db_topic.sort_order = (max_order or 0) + 1
    print(db_topic)
    try:
        session.add(db_topic)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear el tema"
        )
    session.refresh(db_topic)

    return db_topic

@router.get("/subjects/{subject_id}/topics", response_model=Page[TopicRead], status_code=status.HTTP_200_OK)
def list_topics(
    subject_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    params: TopicPagination = Depends()
):
    subject = session.get(Subject, subject_id)

    if not subject or subject.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="La materia no existe")
    
    qs = (
        select(Topic)
        .where(Topic.subject_id == subject_id)
        .order_by(Topic.sort_order)
    )

    return paginate(session, qs, params)

@router.get("/subjects/{subject_id}/topics/{topic_id}", response_model=TopicRead, status_code=status.HTTP_200_OK)
def read_topic(
    topic_id: int,
    subject: Subject = Depends(get_user_subject),
    session: SessionDep = Depends(),
):

    topic = session.exec(
        select(Topic)
        .where(Topic.id == topic_id,
               Topic.subject_id == subject.id)
    ).first()

    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="El tema no existe")
    
    topic.last_viewed_at = utc_now()

    session.commit()
    session.refresh(topic)

    return topic