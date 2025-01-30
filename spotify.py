import time
import requests
import logging
from typing import Optional


class SpotifyClient:
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, auth_manager, rate_limiter=None, logger: Optional[logging.Logger] = None):
        self.auth_manager = auth_manager
        self.rate_limiter = rate_limiter
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def _make_request(self, endpoint, params=None):
        url = f"{self.BASE_URL}/{endpoint}"
        while True:
            if self.rate_limiter:
                self.rate_limiter.acquire()

            access_token = self.auth_manager.get_access_token()
            headers = {"Authorization": f"Bearer {access_token}"}
            resp = requests.get(url, headers=headers, params=params)

            # Handle rate-limit (429)
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 1))
                self.logger.warning(f"Hit 429 Rate Limit; sleeping {retry_after} seconds.")
                time.sleep(retry_after)
                continue

            # Handle unauthorized token
            if resp.status_code == 401:
                self.logger.warning("Token expired or invalid. Forcing refresh.")
                self.auth_manager.access_token = None
                continue

            if resp.status_code != 200:
                self.logger.error(f"Request failed: {resp.status_code} {resp.text}")
                return {}

            return resp.json()

    def search_artists(self, query, limit=50, offset=0):
        endpoint = "search"
        params = {
            "q": query,
            "type": "artist",
            "limit": limit,
            "offset": offset
        }
        return self._make_request(endpoint, params)

    def get_artist(self, artist_id):
        endpoint = f"artists/{artist_id}"
        return self._make_request(endpoint)

    def get_related_artists(self, artist_id):
        endpoint = f"artists/{artist_id}/related-artists"
        return self._make_request(endpoint)

    def get_trending_artists(self):
        # Placeholder if you want an endpoint for top/trending
        return []