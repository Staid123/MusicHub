from abc import ABC, abstractmethod
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from music.schemas import SongIn, SongOut, SongUpdate
# from music.schemas.user import User
from music.models import Song
from music.repository.song_repository import SongRepository, get_song_repository
from minio_service.s3_actions import s3_client


class AbstractSongService(ABC):
    @staticmethod
    @abstractmethod
    async def list_songs():
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
    

class SongService(AbstractSongService):
    @staticmethod
    async def list_songs(
        session: AsyncSession,
        song_repository: SongRepository = get_song_repository(),
        **filters,
    ) -> list[SongOut]:
        songs: list[Song] = await song_repository.get_songs(
            session=session,
            **filters
        )
        songs_schemas = []
        for song in songs:
            song_schema = SongOut.model_validate(song, from_attributes=True)
            song_schema.image = s3_client.download_file_from_s3(song.name)
            songs_schemas.append(song_schema)
        return songs_schemas
    
    @staticmethod
    async def create_song(
        session: AsyncSession,
        song_in: SongIn,
        song_repository: SongRepository = get_song_repository(),
    ) -> None:
        pass


# Зависимость для получения сервиса
def get_song_service():
    return SongService