from abc import ABC, abstractmethod
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import UserOut
from aws.s3_actions import S3Client
from music.repository.song_repository import SongRepository, get_song_repository
from music.schemas import AlbumIn, AlbumOut, AlbumUpdate, Files
from database.models import Album
from music.repository.album_repository import AlbumRepository, get_album_repository
from music.constants import ALBUMS, IMAGES
from music.service.mixins.file_action_mixin import FileActionMixin
from music.utils import check_user_role


class AbstractAlbumService(ABC):
    @staticmethod
    @abstractmethod
    async def list_albums():
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


class AlbumService(AbstractAlbumService, FileActionMixin):
    @staticmethod
    async def list_albums(
        session: AsyncSession,
        album_repository: AlbumRepository = get_album_repository(),
        **filters,
    ) -> list[AlbumOut]:
        albums: list[Album] = await album_repository.get_albums(session=session, **filters)
        return [AlbumOut.model_validate(album, from_attributes=True) for album in albums]
    
    
    @staticmethod
    @check_user_role
    async def create_album(
        session: AsyncSession,
        name: str,
        user: UserOut,
        photo_file: UploadFile,
        album_repository: AlbumRepository = get_album_repository(),
    ) -> Files:
        photo_filename, photo_url_key = await AlbumService._generate_file_key(photo_file, IMAGES, ALBUMS)

        async with S3Client() as s3_client:
            await AlbumService._upload_file(s3_client, photo_file, photo_url_key, IMAGES)

        album_in = AlbumIn(
            name=name,
            artist_id=user.id,
            photo_url=photo_url_key,
        )

        await album_repository.create_album(session=session, album_in=album_in)
        return Files(photo_filename=photo_filename)


    @staticmethod
    @check_user_role
    async def update_album(
        album_id: int,
        user: UserOut,
        session: AsyncSession,
        name: str | None = None,
        photo_file: UploadFile | None = None,
        album_repository: AlbumRepository = get_album_repository(),
    ) -> Files:
        album_to_update: AlbumOut = await album_repository.get_album_by_id(session=session, album_id=album_id)

        photo_filename, photo_url_key = None, None

        async with S3Client() as s3_client:
            if photo_file:
                photo_filename, photo_url_key = await AlbumService._generate_file_key(photo_file, IMAGES, ALBUMS)
                await AlbumService._update_file(s3_client, photo_file, album_to_update.photo_url, photo_url_key, IMAGES)

        album_update = AlbumUpdate(
            name=name or album_to_update.name,
            photo_url=photo_url_key or album_to_update.photo_url,
        )
        
        await album_repository.update_album(session=session, album_id=album_id, album_update=album_update)
        return Files(photo_filename=photo_filename)


    @staticmethod
    @check_user_role
    async def delete_album(
        session: AsyncSession,
        album_id: int,
        user: UserOut,
        album_repository: AlbumRepository = get_album_repository(),
        song_repository: SongRepository = get_song_repository()
    ) -> None:        
        album: AlbumOut = await album_repository.get_album_by_id(session=session, album_id=album_id)
        
        async with S3Client() as s3_client:
            await AlbumService._delete_file(s3_client, album.photo_url)

        for song in album.songs:
            await song_repository.delete_song(session=session, song_id=song.id)

        await album_repository.delete_album(session=session, album_id=album_id)
    

def get_album_service() -> AlbumService:
    return AlbumService