from sqlalchemy import Boolean, LargeBinary
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from music.enums import Role
from music.models import Album, Song, Base


    
class User(Base):
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
    password_hash: Mapped[bytes] = mapped_column(LargeBinary)
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true')
    role: Mapped["Role"] = mapped_column(default=Role.GUEST, server_default=Role.GUEST)

    songs: Mapped[list["Song"]] = relationship('Song', back_populates='artist')
    albums: Mapped[list["Album"]] = relationship('Album', back_populates='artist')