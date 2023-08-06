from flask import Flask
from functools import cache


@cache
def get_app() -> Flask:
    app = Flask('todo')
    return app
