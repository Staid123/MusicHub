from enum import Enum


class Role(Enum):
    ARTIST = "artist"
    USER = "user"
    ADMIN = "admin"
    GUEST = "guest"