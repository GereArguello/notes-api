from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from typing import TYPE_CHECKING
from datetime import datetime
from app.utils import utc_now
from app.core.enums import DifficultyLevel

if TYPE_CHECKING:
    from app.users.models import User

class Subject(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("owner_id", "name"),
    )

    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", nullable=False, index=True)

    name: str = Field(max_length=50, nullable=False)
    description: str | None = Field(default=None, max_length=500)

    difficulty: DifficultyLevel = Field(nullable=False)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime | None = Field(default=None,
                                        sa_column_kwargs={"onupdate":
                                                          utc_now})
    last_viewed_at: datetime | None = Field(default=None)

    owner: "User" = Relationship(back_populates="subjects")

    @property
    def difficulty_label(self):
        return self.difficulty.label