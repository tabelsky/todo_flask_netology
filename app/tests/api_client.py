import os
from typing import List, Literal, NamedTuple, Optional, Tuple

import requests
from flask.testing import FlaskClient

HTTP_METHOD = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
RESPONSE_TYPE = Optional[Literal["json", "text"]]


class HttpError(Exception):
    def __init__(self, status_code: int, description: str):
        self.status_code = status_code
        self.description = description

    def __str__(self):
        return f"{self.status_code=}\n{self.description=}"


class AbstractIdResponse(NamedTuple):
    id: int


class AbstractStatusResponse(NamedTuple):
    status: str


class TokenResponse(NamedTuple):
    token: str


class CreateUserResponse(AbstractIdResponse):
    pass


class GetUserResponse(NamedTuple):
    id: int
    name: str
    todos: List[int]


class UpdateUserResponse(AbstractIdResponse):
    pass


class DeleteUserResponse(AbstractStatusResponse):
    pass


class CreateTodoResponse(AbstractIdResponse):
    pass


class TodoItem(NamedTuple):
    id: int
    user_id: int
    name: str
    important: bool
    done: bool
    start_time: str
    finish_time: str


class GetTodoResponse(TodoItem):
    pass


GetTodoListResponse = Tuple[TodoItem]


class UpdateTodoResponse(AbstractIdResponse):
    pass


class DeleteTodoResponse(AbstractIdResponse):
    pass


class TodoApiClient:
    def __init__(self, test_client: FlaskClient):
        self.client = test_client
        self.headers = {}

    def _call(
        self,
        http_method: HTTP_METHOD,
        api_method: str,
        response_type: RESPONSE_TYPE = "json",
        json: dict = None,
        **kwargs,
    ) -> requests.Response | dict | str | list:
        # self.client.open()
        # self.client.get()
        headers = {**kwargs.pop("headers", {}), **self.headers}
        response = getattr(self.client, http_method.lower())(
            api_method, json=json, headers=headers, **kwargs
        )
        # response = self.session.request(
        #     http_method, f"{self.base_url}/{api_method}", json=json, **kwargs
        # )
        print(response.text, response.status_code)

        if response.status_code >= 400:
            raise HttpError(response.status_code, response.text)

        if response_type is not None:
            response = getattr(response, response_type)
            if callable(response):
                response = response()
        return response

    def login(self, name: str, password: str) -> TokenResponse:
        return TokenResponse(
            **self._call("POST", "/login", json={"name": name, "password": password})
        )

    def auth(self, name: str, password: str) -> None:
        token = self.login(name, password).token
        self.headers["Authorization"] = token

    def create_user(self, name: str, password: str) -> CreateUserResponse:
        return CreateUserResponse(
            **self._call("POST", "/user", json={"name": name, "password": password})
        )

    def get_user(self) -> GetUserResponse:
        return GetUserResponse(**self._call("GET", "/user"))

    def update_user(self, name: str = None, password: str = None) -> UpdateUserResponse:
        payload = {}
        if name is not None:
            payload["name"] = name
        if password is not None:
            payload["password"] = password
        return UpdateUserResponse(**self._call("PATCH", "/user", json=payload))

    def delete_user(self) -> DeleteUserResponse:
        return DeleteUserResponse(**self._call("DELETE", "/user"))

    def get_todos(self) -> GetTodoListResponse:
        return tuple(TodoItem(**todo_item) for todo_item in self._call("GET", "/todo"))

    def get_todo(self, todo_id: int) -> GetTodoResponse:
        return GetTodoResponse(**self._call("GET", f"/todo/{todo_id}"))

    def update_todo(
        self, todo_id: int, name: str = None, important: bool = None, done: bool = None
    ) -> UpdateTodoResponse:
        payload = {}
        if name is not None:
            payload["name"] = name
        if important is not None:
            payload["importance"] = important
        if done is not None:
            payload["done"] = done
        return UpdateTodoResponse(
            **self._call("PATCH", f"/todo/{todo_id}", json=payload)
        )

    def create_todo(self, name: str, important: bool = False) -> CreateTodoResponse:
        return CreateTodoResponse(
            **self._call("POST", "/todo", json={"name": name, "important": important})
        )
