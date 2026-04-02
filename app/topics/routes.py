from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import select
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
from app.topics.schemas import TopicCreate, TopicRead, TopicUpdate, TopicReOrder
from app.topics.services import (existing_topic,
                                 get_topic_or_404,
                                 get_max_order_or_0,
                                 get_topics_to_reorder,
                                 shift_down,
                                 shift_up)

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

    max_order = get_max_order_or_0(session, subject_id)

    db_topic.sort_order = max_order + 1

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
    session: SessionDep,
    subject: Subject = Depends(get_user_subject),
):

    topic = get_topic_or_404(session, subject, topic_id)

    topic.last_viewed_at = utc_now()

    session.commit()
    session.refresh(topic)

    return topic

@router.patch("/subjects/{subject_id}/topics/{topic_id}", response_model=TopicRead, status_code=status.HTTP_200_OK)
def update_topic(
    topic_id: int,
    session: SessionDep,
    topic_data: TopicUpdate,
    subject: Subject = Depends(get_user_subject),
):

    topic = get_topic_or_404(session, subject, topic_id)

    update_data = topic_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar"
        )

    if "name" in update_data and topic.name == update_data["name"]:
        return topic
    
    topic.sqlmodel_update(update_data)

    try:
        session.add(topic)
        session.commit()
        session.refresh(topic)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un tema con este nombre"
        )
    return topic

@router.patch("/subjects/{subject_id}/topics/{topic_id}/re-order", response_model=TopicRead, status_code=status.HTTP_200_OK)
def re_order_topic(
    topic_id: int,
    order_data: TopicReOrder,
    session: SessionDep,
    subject: Subject = Depends(get_user_subject),
):
    topic = get_topic_or_404(session, subject, topic_id)

    new_order = order_data.model_dump(exclude_unset=True)

    if not new_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar"
        )

    new_sort_order = new_order["sort_order"]
    
    if topic.sort_order == new_sort_order:
        return topic

    last_topic = get_max_order_or_0(session, subject.id)

    if new_sort_order > last_topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de orden fuera de rango"
        )
    
    old_order = topic.sort_order

    topics = get_topics_to_reorder(session, subject, old_order, new_sort_order)

    try:
        topic.sort_order = -1
        session.add(topic)
        session.flush()

        if new_sort_order > old_order:
            shift_down(session, topics)
        else:
            shift_up(session, topics)

        topic.sort_order = new_sort_order
        session.add(topic)
        
        session.commit()
        session.refresh(topic)

        return topic
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto al reordenar los temas"
        )
    
@router.delete("/subjects/{subject_id}/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    topic_id: int,
    session: SessionDep,
    subject: Subject = Depends(get_user_subject),
):
    topic = get_topic_or_404(session, subject, topic_id)

    topics_to_update = session.exec(
        select(Topic)
        .where(
            Topic.subject_id == subject.id,
            Topic.sort_order > topic.sort_order
        )
    ).all()

    session.delete(topic)
    session.flush()

    shift_down(session, topics_to_update)    

    session.commit()

    return None

