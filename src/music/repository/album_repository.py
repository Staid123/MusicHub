from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from database.models import Album
from music.schemas import AlbumIn, AlbumOut, AlbumUpdate



class AbstractRepository(ABC):
    @staticmethod
    @abstractmethod
    async def get_album_by_id():
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def get_albums():
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def create_album():
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    async def update_album():
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    async def delete_album():
        raise NotImplementedError


class AlbumRepository(AbstractRepository):
    @staticmethod
    async def get_album_by_id(
        session: AsyncSession,
        album_id: int
    ) -> Album | None:
        stmt = (
            select(Album)
            .options(
                joinedload(Album.artist),
                selectinload(Album.songs)
            )
            .filter_by(id=album_id)
        )
        result = await session.scalars(stmt)
        album: Album = result.one_or_none()
        if album:
           return album
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Album not found"
        )
    
    @staticmethod
    async def get_albums(
        session: AsyncSession,
        **filters
    ) -> list[Album]:
        skip = filters.pop('skip', 0)
        limit = filters.pop('limit', 10)
        stmt = (
            select(Album)
            .options(
                joinedload(Album.artist),
                selectinload(Album.songs)
            )
            .filter_by(**filters)
            .offset(skip)
            .limit(limit)
            .order_by(Album.id)
        )
        albums: list[Album] = await session.scalars(stmt)
        return albums.all()
    
    @staticmethod
    async def create_album(
        session: AsyncSession,
        album_in: AlbumIn
    ) -> Album:
        try:
            album = Album(**album_in.model_dump())
            session.add(album)
            await session.commit()
            return album
        except Exception:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can not add album"
            )
        
    @staticmethod
    async def update_album(
        session: AsyncSession,
        album_id: int,
        album_update: AlbumUpdate
    ) -> Album:
        album: Album = await AlbumRepository.get_album_by_id(
            session=session,
            album_id=album_id
        )
        try:
            for name, value in album_update.model_dump(exclude_none=True).items():
                setattr(album, name, value)
            await session.commit()
            return album
        except Exception:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can not update album"
            )
        
    @staticmethod
    async def delete_album(
        session: AsyncSession,
        album_id: int
    ) -> Album:
        album: Album = await AlbumRepository.get_album_by_id(
            session=session,
            album_id=album_id
        )
        try:
            await session.delete(album)
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can not delete album"
            )

        
        


def get_album_repository() -> AlbumRepository:
    return AlbumRepository