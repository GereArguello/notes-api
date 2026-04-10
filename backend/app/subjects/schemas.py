from sqlmodel import SQLModel, Field
from app.core.enums import DifficultyLevel
from datetime import datetime

class SubjectCreate(SQLModel):
    name: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default= None, max_length=500)
    difficulty: DifficultyLevel

class SubjectRead(SQLModel):
    id: int
    owner_id: int
    name: str
    description: str | None
    difficulty: DifficultyLevel
    difficulty_label: str
    created_at: datetime
    updated_at: datetime | None
    last_viewed_at: datetime | None

class SubjectUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    difficulty: DifficultyLevel | None = None