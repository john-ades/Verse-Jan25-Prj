# storage.py
import csv
from verse_jan25_prj.models import Artist
import threading
import json
from pathlib import Path


CHECKPOINT_FILE = ".cache/checkpoint.json"


class CSVStorage:
    def __init__(self, filepath):
        self.filepath = filepath
        self.lock = threading.Lock()

    def save_artist(self, artist: Artist):
        with self.lock, open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([artist.id, artist.name, ",".join(artist.genres), artist.popularity])


def save_checkpoint(visited_ids, to_process, checkpoint_file=Path(CHECKPOINT_FILE)):
    data = {
        "visited_ids": list(visited_ids),
        "to_process": to_process
    }
    with checkpoint_file.open("w") as f:
        json.dump(data, f, indent=2)


def load_checkpoint(checkpoint_file=Path(CHECKPOINT_FILE)):
    try:
        with open(checkpoint_file, "r") as f:
            data = json.load(f)
        visited_ids = set(data["visited_ids"])
        to_process = data["to_process"]
    except FileNotFoundError:
        visited_ids = set()
        to_process = []
    return visited_ids, to_process