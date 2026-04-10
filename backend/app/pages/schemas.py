from sqlmodel import SQLModel, Field
from sqlalchemy import Column, TEXT
from datetime import datetime

class PageCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    content: str | None = Field(
        default=None,
        sa_column=Column(TEXT, nullable=True)
    )

class PageRead(SQLModel):
    id: int
    topic_id: int

    title: str
    content: str | None
    sort_order: int

    created_at: datetime
    updated_at: datetime | None
    last_viewed_at: datetime | None

class PageUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None

class PageReOrder(SQLModel):
    sort_order : int | None = Field(ge=1, default=None)