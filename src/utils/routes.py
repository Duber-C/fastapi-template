from typing import Annotated, Any
from uuid import UUID
from sqlmodel import SQLModel, select

from fastapi import HTTPException, Query

from src.utils.database import SessionDep


class Selector:
    model: Any

    @classmethod
    def all(
        cls,
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ):
        items = session.exec(select(cls.model).offset(offset).limit(limit)).all()
        return items

    @classmethod
    def create(cls, item: Any, session: SessionDep):
        item = cls.model.model_validate(item)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @classmethod
    def get(cls, id: UUID, session: SessionDep):
        item = session.get(cls.model, id)
        if not item:
            raise HTTPException(status_code=404, detail="not found")
        return item

    @classmethod
    def update(cls, id: UUID, account: SQLModel, session: SessionDep):
        item = session.get(cls.model, id)
        if not item:
            raise HTTPException(status_code=404, detail="not found")

        item_data = account.model_dump(exclude_unset=True)
        item.sqlmodel_update(item_data)
        session.add(item)
        session.commit()
        session.refresh(item)

        return item

    @classmethod
    def delete(cls, id: UUID, session: SessionDep):
        item = session.get(cls.model, id)
        if not item:
            raise HTTPException(status_code=404, detail="not found")

        session.delete(item)
        session.commit()

        return {"ok": True}

