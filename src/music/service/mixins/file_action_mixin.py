from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from aws.s3_actions import S3Client
from music.constants import IMAGES, MUSIC, SUPPORTED_FILE_TYPES


class FileActionMixin:    
    @staticmethod
    async def _generate_file_key(file: UploadFile, file_type: str, folder_type: str) -> tuple[str, str]:
        filename = f"{uuid4()}.{file.filename.split('.')[-1]}"
        url_key = f"{folder_type}/{file_type}/{filename}"
        return filename, url_key

    @staticmethod
    async def _upload_file(s3_client: S3Client, file: UploadFile, key: str, file_type: str) -> None:
        await s3_client.s3_upload_file(file=file, key=key, SUPPORTED_FILE_TYPES=SUPPORTED_FILE_TYPES[file_type])

    @staticmethod
    async def _download_file(s3_client: S3Client, file_name: str, key: str) -> str:
        return await s3_client.s3_download_file(file_name=file_name, key=key)

    @staticmethod
    async def _update_file(s3_client: S3Client, file: UploadFile, old_key: str, new_key: str, file_type: str) -> None:
        await s3_client.s3_update_file(file=file, old_key=old_key, new_key=new_key, SUPPORTED_FILE_TYPES=SUPPORTED_FILE_TYPES[file_type])

    @staticmethod
    async def _delete_file(s3_client: S3Client, key: str) -> None:
        await s3_client.s3_delete_file(key=key)

    @staticmethod
    async def download_song_or_photo_file(file_name: str, folder_type: str) -> str:
        if not file_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='No file name provided'
            )
        file_type = file_name.split(".")[-1]
        if file_type in SUPPORTED_FILE_TYPES[IMAGES].values():
            key = f"{folder_type}/{IMAGES}/{file_name}"
        else:
            key = f"{folder_type}/{MUSIC}/{file_name}"
        async with S3Client() as s3_client:
            return await FileActionMixin._download_file(s3_client, file_name, key=key)