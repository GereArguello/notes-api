from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime
from datetime import datetime

class RefreshToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    token: str
    expires_at: datetime
    revoked_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )