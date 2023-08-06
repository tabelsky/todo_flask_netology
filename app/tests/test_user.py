import pytest

from .api_client import HttpError
from .constants import DEFAULT_USER_NAME, DEFAULT_USER_PASSWORD, NEW_USER_NAME


class TestUser:
    def test_create_user(self, client):
        response = client.create_user("test_create_user", DEFAULT_USER_PASSWORD)
        assert response.id is not None

    def test_create_user_with_same_name(self, client):
        client.create_user("test_create_user_with_same_name", DEFAULT_USER_PASSWORD)
        with pytest.raises(HttpError) as excinfo:
            client.create_user("test_create_user_with_same_name", DEFAULT_USER_PASSWORD)
        assert excinfo.value.status_code == 409

    def test_create_user_with_simple_password(self, client):
        with pytest.raises(HttpError) as excinfo:
            client.create_user("test_create_user_with_simple_password", "123")
        assert excinfo.value.status_code == 400

    def test_auth_user(self, client):
        client.create_user("test_auth_user", DEFAULT_USER_PASSWORD)
        response = client.login("test_auth_user", DEFAULT_USER_PASSWORD)
        assert response.token is not None

    def test_auth_user_with_wrong_password(self, client):
        client.create_user("test_auth_user_with_wrong_password", DEFAULT_USER_PASSWORD)
        with pytest.raises(HttpError) as excinfo:
            client.login("test_auth_user_with_wrong_password", "wrong_password")
        assert excinfo.value.status_code == 401

    def test_auth_user_with_wrong_name(self, client):
        client.create_user("test_auth_user_with_wrong_name", DEFAULT_USER_PASSWORD)
        with pytest.raises(HttpError) as excinfo:
            client.login("wrong_name", DEFAULT_USER_PASSWORD)
        assert excinfo.value.status_code == 404

    def test_get_user(self, default_user_client):
        response = default_user_client.get_user()
        assert response.name == DEFAULT_USER_NAME

    def test_get_user_without_auth(self, client_non_authorized):
        with pytest.raises(HttpError) as excinfo:
            client_non_authorized.get_user()
        assert excinfo.value.status_code == 401

    def test_update_user(self, new_user_client):
        new_user_client.update_user(name="new_name")
        user = new_user_client.get_user()
        assert user.name == "new_name"

    def test_update_user_with_same_name(self, new_user_client):
        with pytest.raises(HttpError) as excinfo:
            new_user_client.update_user(name=DEFAULT_USER_NAME)
        assert excinfo.value.status_code == 409
        user = new_user_client.get_user()
        assert user.name != DEFAULT_USER_NAME

    def test_update_user_with_simple_password(self, new_user_client):
        with pytest.raises(HttpError) as excinfo:
            new_user_client.update_user(password="123")
        assert excinfo.value.status_code == 400
        token = new_user_client.login(NEW_USER_NAME, DEFAULT_USER_PASSWORD).token
        assert token is not None

    def test_update_user_without_auth(self, client_non_authorized):
        with pytest.raises(HttpError) as excinfo:
            client_non_authorized.update_user()
        assert excinfo.value.status_code == 401

    def test_delete_user(self, client):
        client.create_user("test_delete_user", DEFAULT_USER_PASSWORD)
        client.auth("test_delete_user", DEFAULT_USER_PASSWORD)
        client.delete_user()
        with pytest.raises(HttpError) as excinfo:
            client.get_user()
        assert excinfo.value.status_code == 401

    def test_delete_user_without_auth(self, client):
        client.headers["token"] = "wrong_token"
        with pytest.raises(HttpError) as excinfo:
            client.delete_user()
        assert excinfo.value.status_code == 401

    def test_delete_user_twice(self, client):
        client.create_user("test_delete_user", DEFAULT_USER_PASSWORD)
        client.auth("test_delete_user", DEFAULT_USER_PASSWORD)
        client.delete_user()
        with pytest.raises(HttpError) as excinfo:
            client.delete_user()
        assert excinfo.value.status_code == 401
