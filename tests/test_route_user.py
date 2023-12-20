from src.database.models import User
import pytest
from unittest.mock import MagicMock, patch


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

def test_read_users_me(client, access_token):
    response = client.get('api/users/me/')
    assert response.status_code == 401
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('api/users/me/', headers=headers)
    assert response.status_code == 200
    assert 'id' in response.json()
    assert 'username' in response.json()
    assert 'email' in response.json()
    assert 'roles' in response.json()
    assert 'avatar' in response.json()

def test_update_avatar_user(client, access_token, monkeypatch, user, session):
    test_file = ("test.jpg", b"fakefile")
    with patch("src.services.cloud_image.CloudImage.generate_name_avatar", return_value="mock_public_id"), \
            patch("src.services.cloud_image.CloudImage.upload", return_value={"version": "mock_version"}), \
            patch("src.services.cloud_image.CloudImage.get_url_for_avatar", return_value="mock_url"), \
            patch("src.repository.users.update_avatar",
                  return_value={
                      "email": user.get("email"),
                      "avatar": "mock_url",
                      "id": 123,
                      "username": user.get("username"),
                      "roles": "user"
                  }):
        response = client.patch(
            "/api/users/avatar",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": test_file},
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == user.get("email")
    assert data["avatar"] == "mock_url"
    assert data["username"] == user.get("username")
    assert data["roles"] == "user"
    assert data["id"] == 123