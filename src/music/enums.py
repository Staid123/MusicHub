from enum import Enum


class Genre(Enum):
    ROCK = "rock"
    POP = "pop"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    HIPHOP = "hiphop"
    ELECTRONIC = "electronic"
    REGGAE = "reggae"
    BLUES = "blues"


class Role(Enum):
    ARTIST = "artist"
    USER = "user"
    ADMIN = "admin"
    GUEST = "guest"