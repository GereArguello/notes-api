from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from typing import TYPE_CHECKING

from app.page_tags.models import PageTagLink

if TYPE_CHECKING:
    from app.users.models import User
    from app.pages.models import Page


class Tag(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("owner_id", "name"),
    )

    id: int | None = Field(default=None, primary_key=True)

    owner_id: int = Field(
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )

    name: str = Field(max_length=30, nullable=False)

    owner: "User" = Relationship(back_populates="tags")

    pages: list["Page"] = Relationship(
        back_populates="tags",
        link_model=PageTagLink
    )

