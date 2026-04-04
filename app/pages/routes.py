from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page as PageResponse

from app.core.database import SessionDep
from app.core.pagination import PagePagination
from app.topics.models import Topic
from app.pages.schemas import PageRead, PageCreate, PageUpdate, PageReOrder
from app.pages.models import Page
from app.topics.dependencies import get_user_topic
from app.pages.dependencies import get_user_page
from app.pages.services import get_max_order_or_0, get_pages_to_reorder
from app.utils import utc_now, shift_items


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
    session: SessionDep,
    page: Page = Depends(get_user_page),
):

    now = utc_now()

    page.last_viewed_at = now
    page.topic.last_viewed_at = now
    page.topic.subject.last_viewed_at = now

    session.commit()
    session.refresh(page)

    return page

@router.patch(
    "/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
    response_model=PageRead,
    status_code=status.HTTP_200_OK
)
def update_page(
    page_data: PageUpdate,
    session: SessionDep,
    page: Page = Depends(get_user_page)
):
    update_data = page_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar"
        )
    
    if all(getattr(page, k) == v for k, v in update_data.items()):
        return page
    
    page.sqlmodel_update(update_data)

    try:
        session.add(page)
        session.commit()
        session.refresh(page)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una página con este título"
        )
    return page

@router.patch(
    "/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/re-order",
    response_model=PageRead,
    status_code=status.HTTP_200_OK
)
def re_order_page(
    session: SessionDep,
    order_data: PageReOrder,
    page: Page = Depends(get_user_page)
):
    data = order_data.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar"
        )

    new_sort_order = data["sort_order"]

    if page.sort_order == new_sort_order:
        return page
    
    last_order = get_max_order_or_0(session, page.topic_id)

    if new_sort_order > last_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de orden fuera de rango"
        )
    
    old_order = page.sort_order

    pages = get_pages_to_reorder(session, page.topic_id, old_order, new_sort_order)

    try:
        page.sort_order = -1
        session.add(page)
        session.flush()

        if new_sort_order > old_order:
            shift_items(session, pages, move_up=True)
        else:
            shift_items(session, pages, move_up=False)

        page.sort_order = new_sort_order
        session.add(page)
        
        session.commit()
        session.refresh(page)

        return page
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto al reordenar las páginas"
        )

@router.delete(
    "/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_page(
    session: SessionDep,
    page: Page = Depends(get_user_page)
): 
    pages_to_update = (session.exec(
        select(Page)
        .where(
            Page.topic_id == page.topic_id,
            Page.sort_order > page.sort_order)
        )
    ).all()

    session.delete(page)
    session.flush()

    shift_items(session, pages_to_update, move_up=True)

    session.commit()

    return None