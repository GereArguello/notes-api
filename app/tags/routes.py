from fastapi import APIRouter, status, Depends
from sqlmodel import select
from app.core.database import SessionDep
from app.pages.dependencies import get_user_page
from app.pages.models import Page
from app.tags.schemas import TagCreate, TagRead
from app.tags.services import get_tag_or_create
from app.page_tags.models import PageTagLink
from app.page_tags.services import attach_tag_to_page



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
