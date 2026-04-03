from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionDep
from app.topics.models import Topic
from app.pages.schemas import PageRead, PageCreate
from app.pages.models import Page
from app.pages.dependecies import get_user_topic
from app.pages.services import get_max_order_or_0


router = APIRouter(tags=["pages"])


@router.post(
    "/subject/{subject_id}/topics/{topic_id}/pages",
    response_model=PageRead, status_code=status.HTTP_201_CREATED
)
def create_page(
    page_data: PageCreate,
    session: SessionDep,
    topic: Topic = Depends(get_user_topic),
):   
    db_page = Page(**page_data.model_dump(), topic_id=topic.id)

    max_order = get_max_order_or_0(session, topic.id)

    db_page.sort_order = max_order + 1

    try:
        session.add(db_page)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una página con este nombre"
        )
    
    session.refresh(db_page)

    return db_page
