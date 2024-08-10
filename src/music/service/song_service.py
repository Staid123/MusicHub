from abc import ABC, abstractmethod
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from aws.s3_actions import S3Client
from music.enums import Genre
from music.schemas import SongIn, SongOut, SongUpdate, Files
from music.models import Song
from music.repository.song_repository import SongRepository, get_song_repository
from music.constants import MUSIC, SONGS, IMAGES
from music.service.mixins.file_action_mixin import FileActionMixin


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


class SongService(AbstractSongService, FileActionMixin):
    @staticmethod
    async def list_songs(
        session: AsyncSession,
        song_repository: SongRepository = get_song_repository(),
        **filters,
    ) -> list[SongOut]:
        songs: list[Song] = await song_repository.get_songs(session=session, **filters)
        return [SongOut.model_validate(song, from_attributes=True) for song in songs]
    
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
    ) -> Files:
        song_filename, song_url_key = await SongService._generate_file_key(song_file, MUSIC, SONGS)
        photo_filename, photo_url_key = await SongService._generate_file_key(photo_file, IMAGES, SONGS)

        async with S3Client() as s3_client:
            await SongService._upload_file(s3_client, song_file, song_url_key, MUSIC)
            await SongService._upload_file(s3_client, photo_file, photo_url_key, IMAGES)

        song_in = SongIn(
            name=name,
            genre=genre,
            artist_id=artist_id,
            album_id=album_id,
            file_url=song_url_key,
            photo_url=photo_url_key,
        )

        await song_repository.create_song(session=session, song_in=song_in)
        return Files(song_filename=song_filename, photo_filename=photo_filename)

    @staticmethod
    async def update_song(
        session: AsyncSession,
        song_id: int,
        name: str | None = None,
        genre: Genre | None = None,
        song_file: UploadFile | None = None,
        photo_file: UploadFile | None = None,
        song_repository: SongRepository = get_song_repository(),
    ) -> Files:
        song_to_update: SongOut = await song_repository.get_song_by_id(session=session, song_id=song_id)

        song_filename, song_url_key = None, None
        photo_filename, photo_url_key = None, None

        async with S3Client() as s3_client:
            if song_file:
                song_filename, song_url_key = await SongService._generate_file_key(song_file, MUSIC, SONGS)
                await SongService._update_file(s3_client, song_file, song_to_update.file_url, song_url_key, MUSIC)

            if photo_file:
                photo_filename, photo_url_key = await SongService._generate_file_key(photo_file, IMAGES, SONGS)
                await SongService._update_file(s3_client, photo_file, song_to_update.photo_url, photo_url_key, IMAGES)

        song_update = SongUpdate(
            name=name or song_to_update.name,
            genre=genre or song_to_update.genre,
            file_url=song_url_key or song_to_update.file_url,
            photo_url=photo_url_key or song_to_update.photo_url,
        )
        
        await song_repository.update_song(session=session, song_id=song_id, song_update=song_update)
        return Files(song_filename=song_filename, photo_filename=photo_filename)

    @staticmethod
    async def delete_song(
        session: AsyncSession,
        song_id: int,
        song_repository: SongRepository = get_song_repository(),
    ) -> None:
        song: Song = await song_repository.get_song_by_id(session=session, song_id=song_id)
        
        async with S3Client() as s3_client:
            await SongService._delete_file(s3_client, song.file_url)
            await SongService._delete_file(s3_client, song.photo_url)

        await song_repository.delete_song(session=session, song_id=song_id)


# Зависимость для получения сервиса
def get_song_service() -> SongService:
    return SongService()
