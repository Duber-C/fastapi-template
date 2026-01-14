from typing import Annotated, Type
from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


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

