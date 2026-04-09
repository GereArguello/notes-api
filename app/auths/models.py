from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, ForeignKey
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.users.models import User

class RefreshToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )

    token: str
    expires_at: datetime
    revoked_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )

    user: "User" = Relationship(back_populates="refresh_tokens")