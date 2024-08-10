from sqlalchemy import ForeignKey, MetaData, UniqueConstraint
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    mapped_column,
    declared_attr,
    relationship,
)
from auth.models import User
from music.enums import Genre
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
    file_url: Mapped[str]
    photo_url: Mapped[str]
    genre: Mapped["Genre"]
    artist_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    album_id: Mapped[int] = mapped_column(ForeignKey('album.id'))
    
    artist: Mapped["User"] = relationship('User', back_populates='songs')
    album: Mapped["Album"] = relationship('Album', back_populates='songs')

    __table_args__ = (
        UniqueConstraint("name", "artist_id", "album_id"),
    )


class Album(Base):
    name: Mapped[str]
    artist_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    photo_url: Mapped[str]
 
    artist: Mapped["User"] = relationship('User', back_populates='albums')
    songs: Mapped[list["Song"]] = relationship('Song', back_populates='album')

    __table_args__ = (
        UniqueConstraint("name", "artist_id"),
    )