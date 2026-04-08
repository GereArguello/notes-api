from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import select
from app.core.database import SessionDep
from app.auths.dependencies import get_current_user
from app.users.models import User
from app.pages.dependencies import get_user_page
from app.pages.models import Page
from app.tags.schemas import TagCreate, TagRead
from app.tags.models import Tag
from app.tags.services import get_tag_or_create
from app.page_tags.services import attach_tag_to_page
from app.page_tags.models import PageTagLink



router = APIRouter(tags=["tags"])

@router.post("/pages/{page_id}/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    data: TagCreate,
    session: SessionDep,
    page: Page = Depends(get_user_page)
):
    tag_name = data.name.strip().lower()
    user_id = page.topic.subject.owner_id

    tag = get_tag_or_create(session, user_id, tag_name)

    attach_tag_to_page(session, page.id, tag.id)

    session.commit()

    return tag

@router.get("/tags", response_model=list[TagRead])
def list_tags(
    session: SessionDep,
    search: str | None = None,
    current_user: User = Depends(get_current_user),
):
    query = select(Tag).where(Tag.owner_id == current_user.id)

    if search:
        query = query.where(Tag.name.contains(search.lower()))

    query = query.order_by(Tag.name)

    return session.exec(query).all()

@router.delete("/pages/{page_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_page_tag(
    tag_id: int,
    session: SessionDep,
    page: Page = Depends(get_user_page),
):
    link = session.exec(
        select(PageTagLink).where(
            PageTagLink.page_id == page.id,
            PageTagLink.tag_id == tag_id
        )
    ).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El tag no está asociado a esta página"
        )
    
    session.delete(link)
    session.commit()