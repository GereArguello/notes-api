from sqlmodel import SQLModel, Field
from datetime import datetime

class RefreshToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    token: str
    expires_at: datetime
    revoked: bool = False