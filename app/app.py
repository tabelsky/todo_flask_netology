from functools import cache

from flask import Flask


@cache
def get_app() -> Flask:
    app = Flask("todo")
    return app
