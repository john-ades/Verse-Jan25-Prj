import os
import time
import requests
import logging
from base64 import b64encode

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

class SpotifyAuthManager:
    def __init__(self, client_id=None, client_secret=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client_id = client_id or os.environ.get("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError("Missing Spotify Client ID or Secret.")

        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self):
        current_time = time.time()
        if self.access_token is None or current_time >= self.token_expires_at:
            self._fetch_token()
        return self.access_token

    def _fetch_token(self):
        self.logger.info("Fetching new Spotify access token...")
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = b64encode(auth_str.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
        if response.status_code != 200:
            self.logger.error(f"Token fetch failed: {response.text}")
            raise RuntimeError("Could not obtain Spotify token")

        token_json = response.json()
        self.access_token = token_json["access_token"]
        expires_in = token_json["expires_in"]  # typically 3600
        self.token_expires_at = time.time() + expires_in
        self.logger.info(f"Obtained Spotify token. Expires in {expires_in} seconds.")