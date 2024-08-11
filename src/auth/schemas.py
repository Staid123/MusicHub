from pydantic import BaseModel, ConfigDict, EmailStr

from auth.enums import Role
from music.enums import Genre


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr
    password_hash: str


class UserIn(UserBase):
    pass


class UserOut(UserBase):
    id: int
    active: bool = True
    role: Role = Role.GUEST
    password_hash: bytes

    albums: list["Album"] = []


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class Album(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    songs: list["Song"] = []


class Song(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    genre: "Genre"