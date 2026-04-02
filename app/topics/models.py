from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint, Column, ForeignKey
from typing import TYPE_CHECKING
from datetime import datetime
from app.utils import utc_now

if TYPE_CHECKING:
    from app.subjects.models import Subject

class Topic(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("subject_id", "name"),
        UniqueConstraint("subject_id", "sort_order"),
    )

    id: int | None = Field(default=None, primary_key=True)
    
    subject_id: int = Field(
        sa_column=Column(
            ForeignKey("subject.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )

    name: str = Field(max_length=200, nullable=False)
    sort_order: int = Field(ge=1, nullable=False)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime | None = Field(default=None,
                                 sa_column_kwargs={"onupdate": utc_now})
    
    last_viewed_at: datetime | None = Field(default=None)

    subject: "Subject" = Relationship(back_populates="topics")

