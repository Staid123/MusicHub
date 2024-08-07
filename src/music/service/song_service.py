from abc import ABC, abstractmethod
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from aws.s3_actions import S3Client
from music.enums import Genre
from music.schemas import SongIn, SongOut, SongUpdate, Files
# from music.schemas.user import User
from music.models import Song
from music.repository.song_repository import SongRepository, get_song_repository
from aws.s3_actions import S3Client
from music.constants import SUPPORTED_FILE_TYPES, MUSIC, SONGS, IMAGES, PHOTO


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
            # song_schema.image = await s3_client.download_file_from_s3(song.name)
            songs_schemas.append(song_schema)
        return songs_schemas
    
    @staticmethod
    async def create_song(
        session: AsyncSession,
        name: str,
        genre: Genre,
        artist_id: int,
        album_id: int,
        song_file: UploadFile,
        photo_file: UploadFile,
        song_repository: SongRepository = get_song_repository(),
    ) -> str:
        song_filename = f"{uuid4()}.{song_file.filename.split('.')[-1]}"
        photo_filename = f"{uuid4()}.{photo_file.filename.split('.')[-1]}"
        song_url_key = f"{SONGS}/{MUSIC}/{song_filename}"
        photo_url_key = f"{SONGS}/{PHOTO}/{photo_filename}"

        async with S3Client() as s3_client:
            await s3_client.s3_upload_file(
                file=song_file, 
                key=song_url_key, 
                SUPPORTED_FILE_TYPES=SUPPORTED_FILE_TYPES[MUSIC]
            )
            await s3_client.s3_upload_file(
                file=photo_file, 
                key=photo_url_key, 
                SUPPORTED_FILE_TYPES=SUPPORTED_FILE_TYPES[IMAGES]
            )

        song_in = SongIn(
            name=name,
            genre=genre,
            artist_id=artist_id,
            album_id=album_id,
            file_url=song_url_key,
            photo_url=photo_url_key
        )

        await song_repository.create_song(
            session=session,
            song_in=song_in
        )
        return Files(
            song_filename=song_filename, 
            photo_filename=photo_filename
        )

# Зависимость для получения сервиса
def get_song_service():
    return SongService