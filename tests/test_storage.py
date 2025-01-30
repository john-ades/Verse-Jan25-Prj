import pytest
import csv
from verse_jan25_prj.storage import CSVStorage
from verse_jan25_prj.models import Artist


@pytest.fixture
def temp_csv(tmp_path):
    return tmp_path / "test_artists.csv"


def test_save_artist(temp_csv):
    storage = CSVStorage(filepath=temp_csv)
    artist = Artist(id="123", name="Test Artist", genres=["rock", "pop"], popularity=80)
    storage.save_artist(artist)

    with open(temp_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0] == ["123", "Test Artist", "rock,pop", "80"]