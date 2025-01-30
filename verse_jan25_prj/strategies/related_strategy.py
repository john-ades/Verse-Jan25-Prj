from .base_strategy import BaseIngestionStrategy
from verse_jan25_prj.models import Artist

class RelatedArtistsIngestionStrategy(BaseIngestionStrategy):
    """
    Ingestion strategy that starts with a seed list of artist IDs
    (e.g. from trending or top charts) and explores their 'related artists'
    to discover new IDs.
    """
    def run(self):
        """
        Pops an artist from self.to_process, fetches its details + related artists,
        stores data, and adds new unique artist IDs to the queue.
        """
        while self.to_process:
            current_artist_id = self.to_process.pop()
            if current_artist_id in self.visited_ids:
                # Already processed or discovered
                continue

            # Fetch the artist's details
            artist_json = self.spotify_client.get_artist(current_artist_id)
            if not artist_json or "id" not in artist_json:
                # If there's an error or the response is empty, skip
                continue

            # Validate with Pydantic
            artist_model = Artist(
                id=artist_json["id"],
                name=artist_json.get("name", ""),
                genres=artist_json.get("genres", []),
                popularity=artist_json.get("popularity", 0)
            )
            # Store in DB, CSV, etc.
            self.storage.save_artist(artist_model)

            # Mark as visited
            self.visited_ids.add(current_artist_id)

            # Fetch related artists
            related_resp = self.spotify_client.get_related_artists(current_artist_id)
            related_artists = related_resp.get("artists", [])
            for rel_art in related_artists:
                rel_id = rel_art.get("id")
                if rel_id and rel_id not in self.visited_ids:
                    self.to_process.append(rel_id)

            # (Optional) partial checkpoint or rate-limit backoff
            # is handled by self.spotify_client internally, so no manual sleep needed.

        self.logger.info("[RelatedStrategy] Finished expanding all related artists in the queue.")