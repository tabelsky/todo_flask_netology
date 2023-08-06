from auth import check_owner, check_password, check_token, hash_password
from crud import add_item, create_item, delete_item, get_item_by_id, update_item
from errors import HttpError
from flask import jsonify, request
from flask.views import MethodView
from models import Todo, Token, User
from schema import CreateTodo, CreateUser, Login, PatchUser, UpdateTodo
from sqlalchemy import func
from sqlalchemy.orm import Session
from tools import validate


class BaseView(MethodView):
    @property
    def session(self) -> Session:
        return request.session

    @property
    def token(self) -> Token:
        return request.token

    @property
    def user(self) -> User:
        return request.token.user


class UserView(BaseView):
    @check_token
    def get(self):
        return jsonify(self.user.dict)

    def post(self):
        payload = validate(CreateUser, request.json)
        payload["password"] = hash_password(payload["password"])
        user = create_item(User, payload, self.session)
        return jsonify({"id": user.id})

    @check_token
    def patch(self):
        payload = validate(PatchUser, request.json)
        user = update_item(self.token.user, payload, self.session)
        return jsonify({"id": user.id})

    @check_token
    def delete(self):
        delete_item(self.token.user, self.session)
        return jsonify({"status": "ok"})


class LoginView(BaseView):
    def post(self):
        payload = validate(Login, request.json)
        user = self.session.query(User).filter_by(name=payload["name"]).first()
        if user is None:
            raise HttpError(404, "user not found")
        if check_password(user.password, payload["password"]):
            token = create_item(Token, {"user_id": user.id}, self.session)
            add_item(token, self.session)
            return jsonify({"token": token.token})
        raise HttpError(401, "invalid password")


class TodoView(BaseView):
    @check_token
    def get(self, todo_id: int = None):
        if todo_id is None:
            return jsonify([todo.dict for todo in self.user.todos])
        todo = get_item_by_id(Todo, todo_id, self.session)
        check_owner(todo, self.token.user_id)
        return jsonify(todo.dict)

    @check_token
    def post(self):
        payload = validate(CreateTodo, request.json)
        todo = create_item(
            Todo, dict(user_id=self.token.user_id, **payload), self.session
        )
        return jsonify({"id": todo.id})

    @check_token
    def patch(self, todo_id: int):
        payload = validate(UpdateTodo, request.json)
        if "done" in payload:
            payload["finish_time"] = func.now()
        todo = get_item_by_id(Todo, todo_id, self.session)
        check_owner(todo, self.token.user_id)
        todo = update_item(todo, payload, self.session)
        return jsonify({"id": todo.id})

    @check_token
    def delete(self, todo_id: int):
        todo = get_item_by_id(Todo, todo_id, self.session)
        check_owner(todo, self.token.user_id)
        delete_item(todo, self.session)
        return jsonify({"status": "ok"})
