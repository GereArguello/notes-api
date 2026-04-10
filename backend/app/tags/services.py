from sqlmodel import select
from app.core.database import SessionDep
from app.tags.models import Tag

def get_tag_or_create(session: SessionDep, user_id: int, tag_name: str):
    tag = session.exec(
        select(Tag).where(
            Tag.owner_id == user_id,
            Tag.name == tag_name
        )
    ).first()

    if tag:
        return tag
    
    tag = Tag(owner_id=user_id, name=tag_name)
    session.add(tag)
    session.flush()
    
    return tag