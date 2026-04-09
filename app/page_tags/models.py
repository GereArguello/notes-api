from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKey


class PageTagLink(SQLModel, table=True):
    page_id: int = Field(
        sa_column=Column(
            ForeignKey("page.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    tag_id: int = Field(
        sa_column=Column(
            ForeignKey("tag.id", ondelete="CASCADE"),
            primary_key=True
        )
    )