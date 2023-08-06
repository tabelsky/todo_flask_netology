from flask import jsonify
from errors import HttpError


def handle_error(error: HttpError):
    response = jsonify({
        'status': 'error',
        'description': error.description
    })
    response.status_code = 200
    return response
