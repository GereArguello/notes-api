from sqlmodel import SQLModel, Field
from datetime import datetime

class TopicCreate(SQLModel):
    name: str = Field(min_length=1, max_length=200)

class TopicRead(SQLModel):
    id: int
    subject_id: int

    name: str
    sort_order: int

    created_at: datetime
    updated_at: datetime | None
    last_viewed_at: datetime | None