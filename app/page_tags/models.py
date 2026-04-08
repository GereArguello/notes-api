from sqlmodel import SQLModel, Field


class PageTagLink(SQLModel, table=True):
    page_id: int = Field(foreign_key="page.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)