from sqlmodel import SQLModel, Field
from datetime import datetime

class TokenBlacklist(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    refresh_token: str
    expires_at: datetime