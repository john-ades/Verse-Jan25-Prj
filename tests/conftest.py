import pytest
from unittest.mock import Mock
from verse_jan25_prj.auth_manager import SpotifyAuthManager
from verse_jan25_prj.rate_limiter import RateLimiter
from verse_jan25_prj.spotify import SpotifyClient


@pytest.fixture
def spotify_client_mock():
    auth_manager = SpotifyAuthManager(client_id="dummy_id", client_secret="dummy_secret")
    rate_limiter = RateLimiter(max_calls=10, period=1.0)
    client = SpotifyClient(auth_manager=auth_manager, rate_limiter=rate_limiter)
    client.get_trending_artists = Mock(return_value=[])
    return client