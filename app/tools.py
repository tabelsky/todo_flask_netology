from errors import HttpError
from flask import jsonify
from pydantic import ValidationError
from schema import SCHEMA_MODEL


def get_json_response(json_data: dict, status_code: int = 200):
    response = jsonify(json_data)
    response.status_code = status_code
    return response


def handle_error(error: HttpError):
    return get_json_response(
        {"status": "error", "description": error.description}, error.status_code
    )


def validate(model: SCHEMA_MODEL, data: dict):
    try:
        return model.model_validate(data).model_dump(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise HttpError(400, error)
