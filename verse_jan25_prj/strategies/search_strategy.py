import logging
from typing import Set, List
from .base_strategy import BaseIngestionStrategy
from verse_jan25_prj.models import Artist

class SearchIngestionStrategy(BaseIngestionStrategy):
    """
    Ingestion strategy that uses the Spotify /search endpoint
    with various string queries to discover artists, paginating
    through all pages for each query. Logs each newly found artist.
    """

    def __init__(
        self,
        spotify_client,
        storage,
        visited_ids: Set[str],
        to_process: List[str],
        page_limit: int = 50
    ):
        """
        :param spotify_client: An instance of SpotifyClient
        :param storage: Object that implements .save_artist(Artist)
        :param visited_ids: A set of already processed artist IDs
        :param to_process: A list of search queries (e.g. ["a", "b", "c"])
        :param page_limit: How many items per page (Spotify max is 50)
        """
        super().__init__(spotify_client, storage, visited_ids, to_process)
        self.page_limit = page_limit
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        """
        Continually pop queries from self.to_process, call Spotify's search,
        retrieve all pages for each query, and store newly discovered artists.
        Skips any artist IDs already in visited_ids. Logs each newly found artist.
        """
        max_offset = 1000  # Spotify doesn't typically allow offset beyond 1000
        while self.to_process:
            query = self.to_process.pop()
            self.logger.info(f"[SearchStrategy] Searching for query: '{query}'")

            offset = 0
            while True:
                # Fetch one page of search results
                results_json = self.spotify_client.search_artists(
                    query=query,
                    limit=self.page_limit,
                    offset=offset
                )
                if not results_json:
                    self.logger.warning(f"No results or error for query='{query}' at offset={offset}.")
                    break

                # Parse the 'artists' object
                artists_obj = results_json.get('artists', {})
                artist_items = artists_obj.get('items', [])
                total_artists = artists_obj.get('total', 0)

                if not artist_items:
                    self.logger.info(f"No more items for query='{query}' at offset={offset}.")
                    break

                # Process each artist in this page
                page_new_count = 0
                for artist_json in artist_items:
                    artist_id = artist_json.get('id')
                    if not artist_id:
                        continue  # Skip if ID missing

                    if artist_id not in self.visited_ids:
                        # Mark as visited
                        self.visited_ids.add(artist_id)

                        # Construct Pydantic Artist
                        artist_model = Artist(
                            id=artist_id,
                            name=artist_json.get('name', ''),
                            genres=artist_json.get('genres', []),
                            popularity=artist_json.get('popularity', 0)
                        )

                        # Save to storage
                        self.storage.save_artist(artist_model)

                        # LOG: Found a new unique artist
                        self.logger.info(
                            f"Discovered new artist: ID={artist_model.id}, "
                            f"name='{artist_model.name}', popularity={artist_model.popularity}"
                        )
                        page_new_count += 1

                self.logger.info(
                    f"Page offset={offset}, discovered {page_new_count} new artists "
                    f"(out of {len(artist_items)} items) for query='{query}'. "
                    f"Total unique so far: {len(self.visited_ids)}."
                )

                # Check if there's a next page
                next_url = artists_obj.get('next')
                if not next_url:
                    # No more pages
                    self.logger.info(
                        f"No more pages for query='{query}'. "
                        f"Fetched up to offset={offset} (total={total_artists})."
                    )
                    break

                offset += self.page_limit
                if offset >= total_artists or offset >= max_offset:
                    self.logger.info(
                        f"Reached offset limit or end of results for query='{query}' "
                        f"(offset={offset}, total={total_artists})."
                    )
                    break

        self.logger.info("[SearchStrategy] Finished processing all queries in to_process.")