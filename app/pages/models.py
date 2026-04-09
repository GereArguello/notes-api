from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint, Column, ForeignKey, TEXT
from typing import TYPE_CHECKING

from datetime import datetime
from app.utils import utc_now

from app.page_tags.models import PageTagLink

if TYPE_CHECKING:
    from app.topics.models import Topic
    from app.tags.models import Tag


class Page(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("topic_id", "title"),
        UniqueConstraint("topic_id", "sort_order")
    )
    id: int | None = Field(default=None, primary_key=True)

    topic_id: int = Field(
        sa_column=Column(
            ForeignKey("topic.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )

    title: str = Field(max_length=200, nullable=False)
    content: str | None = Field(
        default=None,
        sa_column=Column(TEXT, nullable=True)
    )

    sort_order: int = Field(ge=1, nullable=False)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime | None = Field(default=None,
                                 sa_column_kwargs={"onupdate": utc_now})
    
    last_viewed_at: datetime | None = Field(default=None)

    topic: "Topic" = Relationship(back_populates="pages")

    tags: list["Tag"] = Relationship(
        back_populates="pages",
        link_model=PageTagLink,
        passive_deletes=True
    )
