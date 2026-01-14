from typing import Annotated, Type
from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session

from src.settings import settings

engine = create_engine(settings.database_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def update_or_create(model: Type[SQLModel], item: dict):
    instance = model.model_validate(item)

    pks = model.__table__.primary_key.columns
    pk_values = [getattr(instance, i.name) for i in pks]

    with Session(engine) as session:
        db_item = None
        if pk_values:
            db_item = session.get(model, pk_values)

        if db_item:
            db_item.sqlmodel_update(instance)
        else:
            db_item = instance

        session.add(db_item)
        session.commit()
