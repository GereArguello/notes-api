from sqlmodel import SQLModel, Field

class TagCreate(SQLModel):
    name: str = Field(min_length=1, max_length=30)

class TagRead(SQLModel):
    id: int
    owner_id: int
    name: str