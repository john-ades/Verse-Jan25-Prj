from pydantic import BaseModel, Field
from typing import List


class Artist(BaseModel):
    id: str = Field(..., description="Unique Spotify artist ID")
    name: str
    genres: List[str]
    # The popularity of the artist. The value will be between 0 and 100, with 100 being the most popular. The
    # artist's popularity is calculated from the popularity of all the artist's tracks.
    popularity: int = Field(..., ge=0, le=100)