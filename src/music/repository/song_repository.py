from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from music.models import Song
from music.schemas import SongIn, SongOut, SongUpdate


class AbstractRepository(ABC):
    @staticmethod
    @abstractmethod
    async def get_songs():
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def create_song():
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    async def update_song():
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    async def delete_song():
        raise NotImplementedError


class SongRepository(AbstractRepository):
    @staticmethod
    async def get_songs(
        session: AsyncSession,
        **filters
    ) -> list[Song]:
        skip = filters.pop('skip', 0)
        limit = filters.pop('limit', 10)
        stmt = (
            select(Song)
            .options(
                joinedload(Song.artist),
                joinedload(Song.album)
            )
            .filter_by(**filters)
            .offset(skip)
            .limit(limit)
            .order_by(Song.id)
        )
        songs: list[Song] = await session.scalars(stmt)
        return songs.all()
    
    @staticmethod
    async def create_song(
        session: AsyncSession,
        song_in: SongIn
    ) -> None:
        try:
            song = Song(**song_in.model_dump())
            session.add(song)
            await session.commit()
            return song
        except Exception:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can not add song"
            )

# Зависимость для получения репозитория
def get_song_repository() -> SongRepository:
    return SongRepository