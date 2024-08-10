from pydantic import BaseModel, ConfigDict, EmailStr

from music.enums import Role


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)

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


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"