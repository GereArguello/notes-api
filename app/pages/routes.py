from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page as PageResponse

from app.core.database import SessionDep
from app.core.pagination import PagePagination
from app.topics.models import Topic
from app.pages.schemas import PageRead, PageCreate
from app.pages.models import Page
from app.pages.dependecies import get_user_topic
from app.pages.services import get_max_order_or_0, get_page_or_404
from app.utils import utc_now


router = APIRouter(tags=["pages"])


@router.post(
    "/subjects/{subject_id}/topics/{topic_id}/pages",
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

@router.get(
        "/subjects/{subject_id}/topics/{topic_id}/pages",
        response_model=PageResponse[PageRead],
        status_code=status.HTTP_200_OK)
def list_pages(
    session: SessionDep,
    topic: Topic = Depends(get_user_topic),
    params: PagePagination = Depends()
):
    qs = (
        select(Page)
        .where(Page.topic_id == topic.id)
        .order_by(Page.sort_order)
    )

    return paginate(session, qs, params)

@router.get(
        "/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
        response_model=PageRead,
        status_code=status.HTTP_200_OK
)
def read_page(
    page_id: int,
    session: SessionDep,
    topic: Topic = Depends(get_user_topic),
):
    page = get_page_or_404(session, page_id, topic)

    now = utc_now()

    page.last_viewed_at = now
    page.topic.last_viewed_at = now
    page.topic.subject.last_viewed_at = now

    session.commit()
    session.refresh(page)

    return page