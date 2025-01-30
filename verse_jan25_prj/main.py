import argparse
import logging
import time
import os
from pathlib import Path
import string

from verse_jan25_prj.rate_limiter import RateLimiter
from verse_jan25_prj.auth_manager import SpotifyAuthManager
from verse_jan25_prj.spotify import SpotifyClient
from verse_jan25_prj.storage import CSVStorage, load_checkpoint, save_checkpoint
from verse_jan25_prj.strategies.search_strategy import SearchIngestionStrategy
from verse_jan25_prj.strategies.related_strategy import RelatedArtistsIngestionStrategy

def float_or_int(value: str):
    """
    Allows period argument to be passed as either int (e.g. '1')
    or float (e.g. '0.5').
    """
    try:
        return int(value)
    except ValueError:
        return float(value)

def main():
    parser = argparse.ArgumentParser(
        description="Spotify Artist Ingestion Script (Client Credentials). "
                    "If --client-id or --client-secret are not provided, "
                    "the script will attempt to use env vars SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET."
    )

    parser.add_argument(
        "--client-id",
        help="Spotify Client ID (optional; if not provided, uses SPOTIFY_CLIENT_ID from environment)."
    )
    parser.add_argument(
        "--client-secret",
        help="Spotify Client Secret (optional; if not provided, uses SPOTIFY_CLIENT_SECRET from environment)."
    )
    parser.add_argument(
        "--strategy",
        choices=["search", "related"],
        default="search",
        help="Which ingestion strategy to use: 'search' or 'related'."
    )
    parser.add_argument(
        "--output",
        default="artists.csv",
        help="CSV file for storing results. Default: 'artists.csv'."
    )
    parser.add_argument(
        "--checkpoint",
        default=".cache/spotify_ingest_checkpoint.json",
        help="Path to the checkpoint file (default: .cache/spotify_ingest_checkpoint.json)."
    )
    parser.add_argument(
        "--max-calls",
        type=int,
        default=1,
        help="Maximum requests per second for the rate limiter (default: 1)."
    )
    parser.add_argument(
        "--period",
        type=float_or_int,
        default=1.0,
        help="Period in seconds for the rate limiter's token bucket (default: 1.0)."
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SpotifyIngestion")

    # Resolve client credentials from CLI or environment
    client_id = args.client_id or os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = args.client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        parser.error(
            "Spotify Client ID/Secret are required. "
            "Provide via --client-id/--client-secret or set env variables "
            "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET."
        )

    # 1) Load checkpoint
    cache_dir = Path(".cache")
    cache_dir.mkdir(exist_ok=True)
    visited_ids, to_process = load_checkpoint(args.checkpoint)

    # 2) Initialize Auth & RateLimiter
    auth_manager = SpotifyAuthManager(client_id=client_id, client_secret=client_secret)
    rate_limiter = RateLimiter(max_calls=args.max_calls, period=args.period)

    # 3) Create a SpotifyClient
    spotify_client = SpotifyClient(auth_manager=auth_manager, rate_limiter=rate_limiter, logger=logger)

    # 4) If there's no queue from checkpoint, seed it
    if not to_process:
        if args.strategy == "search":
            # Define the characters to include: letters, digits, and common special characters
            letters = list(string.ascii_lowercase)  # 'a' to 'z'
            digits = list(string.digits)  # '0' to '9'
            special_chars = ['_', '-', '&', ' ']
            to_process = letters + digits + special_chars
            logger.info(f"Seeding search queries with letters, digits, and special characters: {to_process}")

        else:
            trending_artists = spotify_client.get_trending_artists()
            to_process = [art["id"] for art in trending_artists]

    # 5) Set up data storage
    storage = CSVStorage(filepath=args.output)

    # 6) Choose the ingestion strategy
    if args.strategy == "search":
        strategy = SearchIngestionStrategy(
            spotify_client, storage, visited_ids, to_process
        )
    else:
        strategy = RelatedArtistsIngestionStrategy(
            spotify_client, storage, visited_ids, to_process
        )

    # 7) Run the ingestion
    start_time = time.time()
    try:
        strategy.run()
    except KeyboardInterrupt:
        logger.warning("Interrupted by user. Saving checkpoint...")

    # 8) Save checkpoint after run
    save_checkpoint(strategy.visited_ids, strategy.to_process, args.checkpoint)

    # 9) Log summary
    elapsed = time.time() - start_time
    logger.info("Run complete. Discovered %d artists.", len(strategy.visited_ids))
    logger.info("Total run time: %.2f seconds", elapsed)


if __name__ == "__main__":
    main()