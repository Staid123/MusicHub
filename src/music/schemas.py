from pydantic import ConfigDict, BaseModel, EmailStr
from typing import TYPE_CHECKING
from fastapi import UploadFile

from music.enums import Role
from music.enums import Genre


class SongBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    genre: "Genre"
    artist_id: int
    album_id: int


class SongIn(SongBase):
    image: UploadFile


class SongOut(SongIn):
    id: int
    artist: "UserBase"
    album: "AlbumBase"


class SongUpdate(BaseModel):
    image: UploadFile


class AlbumBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    artist_id: int


class AlbumIn(AlbumBase):
    image: UploadFile


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
