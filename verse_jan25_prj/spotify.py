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

    def get_seed_artists(self):
        # Collected from random a-z artists.
        # Can be updated as needed
        return ["1Uff91EOsvd99rtAupatMP", "0oSGxfWSnnOXhD2fKuz2Gy", "7u9m43vPVTERaALXXOzrRq", "5cj0lLjcoR7YOSnhnX0Po5", "3YCKuqpv9nCsIhJ2v8SMix", "5szilpXHcwOqnyKLqGco5j", "0ceH34CATvfgphxnLRWFkm", "0n94vC3S9c3mb2HyNAOcjg", "6ASri4ePR7RlsvIQgWPJpS", "14zUHaJZo1mnYtn6IBRaRP", "7dGJo4pcD2V6oG8kP0tJRR", "2wY79sveU1sp5g7SokKOiI", "1HY2Jd0NmPuamShAr6KMms", "6H3nFALN4zLX9AJr79VeVz", "2tfWguHr2nj4e8KXLKciVq", "6wPhSqRtPu1UhRCDX5yaDJ", "1kRABJWDxSnOJFteI351V6", "0MvSBMGRQJY3mRwIbJsqF1", "1gl0S9pS0Zw0qfa14rDD3D", "3WrFJ7ztbogyGnTHbHJFl2", "5Qv1EsPany9Fc3yyCJnoxw", "1KYszkVzlhV3rAqmAcYIgd", "6qYqwkrBvv9Pt3gn3spmCX", "6DfwFHZZibSgQqg8ta9wnW", "6GI52t8N5F02MxU0g5U69P", "1alf4P7GDe5aNpALBzWIGf"]