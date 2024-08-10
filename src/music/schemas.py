from pydantic import ConfigDict, BaseModel

from auth.schemas import UserBase
from music.enums import Genre


class SongBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    genre: "Genre"
    artist_id: int
    album_id: int
    file_url: str | None = None
    photo_url: str | None = None


class SongIn(SongBase):
    pass


class SongOut(SongIn):
    id: int
    artist: "UserBase"
    album: "AlbumBase"


class SongUpdate(BaseModel):
    name: str | None = None
    genre: Genre | None = None
    file_url: str | None = None
    photo_url: str | None = None


class AlbumBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    artist_id: int
    photo_url: str | None = None


class AlbumIn(AlbumBase):
    pass


class AlbumOut(AlbumIn):
    id: int
    artist: "UserBase"
    songs: list["SongBase"]


class AlbumUpdate(BaseModel):
    name: str | None = None
    photo_url: str | None = None

 
class Files(BaseModel):
    song_filename: str | None = None
    photo_filename: str | None = None