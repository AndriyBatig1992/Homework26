from src.database.models import User
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.services.auth import auth_service
from src.conf import messages


@pytest.fixture()
def access_token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_create_contact(client, access_token, monkeypatch):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.post(
            "/api/contacts",
            json={"first_name": "Ivan", "email": "test_mmm@gmail.com", "birthday": "2020-12-21"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["email"] == "test_mmm@gmail.com"
        assert "id" in data

def test_get_contact_by_id(client, access_token):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        print('dataf', f'{data}')
        assert "id" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "birthday" in data

def test_get_contact_by_id_not_found(client, access_token):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/2",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.NOT_FOUND


def test_get_contacts(client, access_token):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["first_name"] == "Ivan"
        assert "id" in data[0]


def test_update_contact(client, access_token):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/api/contacts/1",
            json={"first_name": "new", "email": "test_mmm@gmail.com", "birthday": "2020-12-21"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        print("DATA", data)
        assert data["first_name"] == "new"
        assert "id" in data


def test_update_contact_not_found(client, access_token):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/api/contacts/2",
            json={"first_name": "new_test", "email": "test_mmm@gmail.com", "birthday": "2020-12-21"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.NOT_FOUND


def test_search_contact_by_birthday(client, access_token):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/search/birthdays",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["birthday"]


def test_search_contact_by_query(client, access_token):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/search_by/new",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["first_name"] == "new"


def test_search_contact_by_query_not_found(client, access_token):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/search_by/new_1",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_delete_contact(client, access_token):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 204, response.text


def test_repeat_delete_contact(client, access_token):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/2",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.NOT_FOUND




