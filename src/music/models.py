from sqlalchemy import Boolean, ForeignKey, LargeBinary, MetaData
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    mapped_column,
    declared_attr,
    relationship,
)
from music.enums import Genre, Role
from config import settings



class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    metadata = MetaData(
        naming_convention=settings.db.naming_convention
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    

class Song(Base):
    name: Mapped[str]
    genre: Mapped["Genre"]
    artist_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    album_id: Mapped[int] = mapped_column(ForeignKey('album.id'), nullable=True)

    artist: Mapped["User"] = relationship('User', back_populates='songs')
    album: Mapped["Album"] = relationship('Album', back_populates='songs')


class Album(Base):
    name: Mapped[str]
    artist_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
 
    artist: Mapped["User"] = relationship('User', back_populates='albums')
    songs: Mapped[list["Song"]] = relationship('Song', back_populates='album')


class User(Base):
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
    password_hash: Mapped[bytes] = mapped_column(LargeBinary)
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true')
    role: Mapped["Role"]

    songs: Mapped[list["Song"]] = relationship('Song', back_populates='artist')
    albums: Mapped[list["Album"]] = relationship('Album', back_populates='artist')