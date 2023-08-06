import pytest
from main import app
from models import Base, engine

from .api_client import TodoApiClient
from .constants import (
    DEFAULT_USER_NAME,
    DEFAULT_USER_PASSWORD,
    NEW_TODO_ITEM_IMPORTANT,
    NEW_TODO_ITEM_NOT_IMPORTANT,
    NEW_USER_NAME,
    NEW_USER_NAME_WITH_TODOS,
)


@pytest.fixture(scope="session", autouse=True)
def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def flask_app():
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(flask_app):
    return TodoApiClient(app.test_client())


@pytest.fixture(scope="session")
def default_user_client(flask_app) -> TodoApiClient:
    client = TodoApiClient(app.test_client())
    client.create_user(DEFAULT_USER_NAME, DEFAULT_USER_PASSWORD)
    client.auth(DEFAULT_USER_NAME, DEFAULT_USER_PASSWORD)
    return client


@pytest.fixture()
def new_user_client(client) -> TodoApiClient:
    client.create_user(NEW_USER_NAME, DEFAULT_USER_PASSWORD)
    client.auth(NEW_USER_NAME, DEFAULT_USER_PASSWORD)
    yield client
    client.delete_user()


@pytest.fixture()
def new_user_client_with_todos(client) -> TodoApiClient:
    client.create_user(NEW_USER_NAME_WITH_TODOS, DEFAULT_USER_PASSWORD)
    client.auth(NEW_USER_NAME_WITH_TODOS, DEFAULT_USER_PASSWORD)
    client.create_todo(NEW_TODO_ITEM_IMPORTANT, important=True)
    client.create_todo(NEW_TODO_ITEM_NOT_IMPORTANT, important=False)
    yield client
    client.delete_user()


@pytest.fixture()
def client_non_authorized(client) -> TodoApiClient:
    client.headers["token"] = "wrong_token"
    return client
