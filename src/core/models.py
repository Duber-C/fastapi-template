from datetime import datetime, UTC
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class BaseDBModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    created: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    modified: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
