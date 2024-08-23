from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from database.models import Song
from music.schemas import SongIn, SongUpdate


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
    async def _get_song_with_options(
        session: AsyncSession,
        song_id: int
    ) -> Song:
        stmt = (
            select(Song)
            .options(
                joinedload(Song.artist),
                joinedload(Song.album)
            )
            .filter_by(id=song_id)
        )
        song_with_options: Song = await session.scalars(stmt)
        return song_with_options.one_or_none()
    
    @staticmethod
    async def get_song_by_id(
        session: AsyncSession,
        song_id: int
    ) -> Song:
        song: Song = await SongRepository._get_song_with_options(
            session=session,
            song_id=song_id
        )
        if song:
           return song
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Song not found"
        )

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
    ) -> Song:
        try:
            song = Song(**song_in.model_dump())
            session.add(song)
            await session.commit()
            return await SongRepository._get_song_with_options(
                session=session,
                song_id=song.id,
            )
        except Exception:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can not add song"
            )
        
    @staticmethod
    async def update_song(
        session: AsyncSession,
        song_id: int,
        song_update: SongUpdate
    ) -> Song:
        song: Song = await SongRepository.get_song_by_id(
            session=session,
            song_id=song_id
        )
        try:
            for name, value in song_update.model_dump(exclude_none=True).items():
                setattr(song, name, value)
            await session.commit()
            return await SongRepository._get_song_with_options(session=session, song_id=song_id)
        except Exception:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can not update song"
            )

    @staticmethod
    async def delete_song(
        session: AsyncSession,
        song_id: int
    ) -> None:
        song: Song = await SongRepository.get_song_by_id(
            session=session,
            song_id=song_id
        )
        try:
            await session.delete(song)
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can not delete song"
            )

# Зависимость для получения репозитория
def get_song_repository() -> SongRepository:
    return SongRepository