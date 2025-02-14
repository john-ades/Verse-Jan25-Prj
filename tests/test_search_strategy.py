from unittest.mock import Mock
from verse_jan25_prj.strategies.search_strategy import SearchIngestionStrategy
from verse_jan25_prj.models import Artist


def test_search_strategy_runs_correctly():
    # Mock SpotifyClient
    mock_spotify_client = Mock()
    mock_spotify_client.search_artists.side_effect = [
        {
            "artists": {
                "href": "https://api.spotify.com/v1/search?query=a&type=artist&limit=50&offset=0",
                "items": [
                    {"id": "1", "name": "Artist One", "genres": ["rock"], "popularity": 70},
                    {"id": "2", "name": "Artist Two", "genres": ["pop"], "popularity": 60}
                ],
                "limit": 50,
                "next": None,
                "offset": 0,
                "previous": None,
                "total": 2
            }
        },
        # Second call if any
    ]

    # Mock Storage
    mock_storage = Mock()

    # Initialize strategy
    visited_ids = set()
    to_process = ["a"]
    strategy = SearchIngestionStrategy(
        spotify_client=mock_spotify_client,
        storage=mock_storage,
        visited_ids=visited_ids,
        to_process=to_process
    )

    # Run strategy
    strategy.run()

    # Assertions
    assert len(strategy.visited_ids) == 2
    assert mock_storage.save_artist.call_count == 2
    mock_storage.save_artist.assert_any_call(Artist(id="1", name="Artist One", genres=["rock"], popularity=70))
    mock_storage.save_artist.assert_any_call(Artist(id="2", name="Artist Two", genres=["pop"], popularity=60))