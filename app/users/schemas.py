from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime

class UserCreate(SQLModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: str
    password: str = Field(min_length=8, max_length=128)
    password2: str = Field(min_length=8, max_length=128)
    birth_date: Optional[date] = None

class UserRead(SQLModel):
    id: int
    first_name: str
    last_name: str
    email: str
    birth_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserUpdate(SQLModel):
    first_name: Optional[str] = Field(min_length=1, max_length=50)
    last_name: Optional[str] = Field(min_length=1, max_length=50)
    birth_date: Optional[date]

    model_config = {
        "extra": "forbid"
    }

class UserUpdatePassword(SQLModel):
    current_password : str
    new_password: str = Field(min_length=8, max_length=128)
    new_password2: str = Field(min_length=8, max_length=128)