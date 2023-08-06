import psycopg2
from errors import HttpError
from models import MODEL, MODEL_TYPE, Session
from sqlalchemy.exc import IntegrityError


def get_item_by_id(model: MODEL_TYPE, item_id: int, session: Session) -> MODEL:
    item = session.get(model, item_id)
    if item is None:
        raise HttpError(404, f"{model.__name__} not found")
    return item


def add_item(item: MODEL, session: Session) -> MODEL:
    try:
        session.add(item)
        session.commit()
    except IntegrityError as err:
        if isinstance(err.orig, psycopg2.errors.UniqueViolation):
            raise HttpError(409, f"{item.__class__.__name__} already exists")
        else:
            raise err
    return item


def create_item(model: MODEL_TYPE, payload: dict, session: Session) -> MODEL:
    item = model(**payload)
    item = add_item(item, session)
    return item


def delete_item(item: MODEL, session: Session):
    session.delete(item)
    session.commit()


def update_item(item: MODEL, payload: dict, session: Session) -> MODEL:
    for field, value in payload.items():
        setattr(item, field, value)
    add_item(item, session)
    return item


def update_item_by_id(
    model: MODEL_TYPE, item_id: int, payload: dict, session: Session
) -> MODEL:
    item = get_item_by_id(model, item_id, session)
    update_item(item, payload, session)
    return item
