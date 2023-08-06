from errors import HttpError
from flask import request
from flask_bcrypt import Bcrypt
from models import MODEL, Token

from app import get_app

bcrypt = Bcrypt(get_app())


def hash_password(password: str):
    return bcrypt.generate_password_hash(password.encode()).decode()


def check_password(password: str, hashed_password: str):
    return bcrypt.check_password_hash(password.encode(), hashed_password.encode())


def check_token(handler):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token is None:
            raise HttpError(401, "token not found")
        token = request.session.query(Token).filter_by(token=token).first()
        if token is None:
            raise HttpError(401, "invalid token")
        request.token = token
        return handler(*args, **kwargs)

    return wrapper


def check_owner(item: MODEL, user_id: int):
    if item.user_id != user_id:
        raise HttpError(403, "access denied")
