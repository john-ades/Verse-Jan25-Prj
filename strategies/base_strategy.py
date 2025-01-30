import time
import logging
from abc import ABC, abstractmethod
from typing import Set, List

class BaseIngestionStrategy(ABC):
    def __init__(self, spotify_client, storage, visited_ids: Set[str], to_process: List[str]):
        """
        :param spotify_client: A helper/client for Spotify requests & auth
        :param storage: Some storage interface (DB, CSV, or other)
        :param visited_ids: Set of artist IDs already processed
        :param to_process: Queue/list of artist IDs (or queries) to process
        """
        self.spotify_client = spotify_client
        self.storage = storage
        self.visited_ids = visited_ids
        self.to_process = to_process
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def run(self):
        """Run the strategy until no more items to process."""
        pass

    def save_checkpoint(self):
        """Persist current progress (visited_ids, to_process) for fault tolerance."""
        # Implementation specifics can vary (e.g., to JSON, DB, etc.)
        pass