from unittest.mock import Mock
from verse_jan25_prj.strategies.related_strategy import RelatedArtistsIngestionStrategy
from verse_jan25_prj.models import Artist





def test_related_strategy_runs_correctly():
    # Mock SpotifyClient
    mock_spotify_client = Mock()
    mock_spotify_client.get_artist.side_effect = [
        {"id": "1", "name": "Artist One", "genres": ["rock"], "popularity": 70},
        {"id": "2", "name": "Artist Two", "genres": ["pop"], "popularity": 60}
    ]
    mock_spotify_client.get_related_artists.side_effect = [
        {"artists": [{"id": "2", "name": "Artist Two", "genres": ["pop"], "popularity": 60}]},
        {"artists": []}  # No related artists for Artist Two
    ]

    # Mock Storage
    mock_storage = Mock()

    # Initialize strategy
    visited_ids = set()
    to_process = ["1"]
    strategy = RelatedArtistsIngestionStrategy(
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