import pytest
from unittest.mock import Mock, patch
from verse_jan25_prj.auth_manager import SpotifyAuthManager


@pytest.fixture
def mock_requests_post():
    with patch('verse_jan25_prj.auth_manager.requests.post') as mock_post:
        yield mock_post

def test_auth_manager_initialization():
    with pytest.raises(ValueError):
        SpotifyAuthManager()  # Missing client_id and client_secret

def test_get_access_token_success(mock_requests_post):
    # Mock successful token fetch
    mock_response = Mock()  # from unittest.mock, not pytest
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test_token",
        "token_type": "Bearer",
        "expires_in": 3600
    }
    mock_requests_post.return_value = mock_response

    auth_manager = SpotifyAuthManager(client_id="dummy_id", client_secret="dummy_secret")
    token = auth_manager.get_access_token()

    assert token == "test_token"
    assert auth_manager.access_token == "test_token"
    assert auth_manager.token_expires_at > auth_manager.token_expires_at - 3600

def test_get_access_token_failure(mock_requests_post):
    # Mock failed token fetch
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_requests_post.return_value = mock_response

    auth_manager = SpotifyAuthManager(client_id="dummy_id", client_secret="dummy_secret")

    with pytest.raises(RuntimeError):
        auth_manager.get_access_token()