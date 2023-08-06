class HttpError(Exception):
    def __init__(self, status_code: int, description: dict | list | str):
        self.status_code = status_code
        self.description = description
