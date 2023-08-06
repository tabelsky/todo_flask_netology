from app import get_app
from tools import handle_error
from errors import HttpError
from views import login

app = get_app()

app.add_url_rule(
    '/login',
    view_func=login,
    methods=['POST']
)
app.register_error_handler(
    HttpError,
    handle_error
)

if __name__ == '__main__':
    app.run()