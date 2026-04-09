from sqlmodel import SQLModel, Field, Column, Relationship
from typing import TYPE_CHECKING
from sqlalchemy import String
from datetime import date, datetime
from app.utils import utc_now

if TYPE_CHECKING:
    from app.auths.models import RefreshToken
    from app.subjects.models import Subject
    from app.tags.models import Tag

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    first_name: str = Field(sa_column=Column(String(50), nullable=False))
    last_name: str = Field(sa_column=Column(String(50), nullable=False))

    email: str = Field(
        sa_column=Column(String(255), index=True, unique=True, nullable=False)
    )

    password_hash: str = Field(nullable=False)

    birth_date: date | None = None

    created_at: datetime = Field(default_factory=utc_now)

    updated_at: datetime | None = Field(default=None,
    sa_column_kwargs={"onupdate": utc_now})

    deleted_at: datetime | None = None

    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="user",
        passive_deletes=True
    )

    subjects: list["Subject"] = Relationship(
        back_populates="owner",
        passive_deletes=True
    )
    tags: list["Tag"] = Relationship(
        back_populates="owner",
        passive_deletes=True
    )