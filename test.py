import json
from extensions import bcrypt, db
from flask.testing import FlaskClient
from app import app
import pytest
import ast

from models import User


@pytest.fixture
def client():
    app.testing = True
    client = app.test_client()
    yield client


@pytest.fixture
def admin_user_login(client: FlaskClient):
    response = client.get(
        f'/api/user/login?email=kanaujia.rishabh@gmail.com&password=user123')
    return response.get_json()


@pytest.fixture
def normal_user_login(client: FlaskClient):
    response = client.get(
        f'/api/user/login?email=sourav@gmail.com&password=user123')
    return response.get_json()


def test_create_user_account(client: FlaskClient, admin_user_login: str):
    json_body = {
        "name": "User 3",
        "email": "user_3@gmail.com",
        "password": "user123",
        "role": 2
    }
    response = client.post('/api/user/', json=json_body,
                           headers=get_auth_header(admin_user_login))
    assert response.status_code == 200


def test_user_login(client: FlaskClient):
    response = client.get(
        f'/api/user/login?email=sourav@gmail.com&password=user123')
    assert response.status_code == 200


def test_suspend_account(client: FlaskClient, admin_user_login):
    response = client.post(f'/api/user/suspend', json={
                           "email": "aditya@gmail.com"}, headers=get_auth_header(admin_user_login))
    assert response.status_code == 200
    response2 = client.post(f'/api/user/suspend', json={
        "email": "aditya@gmail.com"}, headers=get_auth_header(admin_user_login))
    assert response2.status_code == 200


def test_add_item_to_db(client: FlaskClient, admin_user_login):
    response = client.post(
        f'/api/item/', json={"name": "Gillete", "units": 3}, headers=get_auth_header(admin_user_login))
    assert response.status_code == 200
    assert response.get_json()["message"] == 'Item added successfully'


def test_list_item_in_db(client: FlaskClient, normal_user_login: str):
    response = client.get(
        '/api/item/', headers=get_auth_header(normal_user_login))
    assert response.status_code == 200
    assert type(response.get_json()["items"]) == list


def test_item_delete_in_db(client: FlaskClient, admin_user_login):
    response = client.delete(
        '/api/item/1', headers=get_auth_header(admin_user_login))
    assert response.status_code == 200
    assert response.get_json()["message"] == "Item deleted successfully"


def get_auth_header(token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {token}'}
