from pydantic import ConfigDict, BaseModel, EmailStr, field_validator
from fastapi import UploadFile

from music.enums import Role
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


class AlbumIn(AlbumBase):
    pass
    # image: UploadFile


class AlbumOut(AlbumIn):
    id: int
    artist: "UserBase"
    songs: list["SongBase"]


class AlbomUpdate(BaseModel):
    image: UploadFile


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)

    username: str
    email: EmailStr
    role: "Role"
    

class UserIn(UserBase):
    password_hash: str


class UserOut(UserBase):
    id: int
    active: bool = True
    password_hash: bytes


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class Files(BaseModel):
    song_filename: str | None = None
    photo_filename: str | None = None