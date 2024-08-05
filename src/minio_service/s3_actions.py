from contextlib import asynccontextmanager
import logging
import aiofiles
from aiobotocore.session import get_session
from config import settings
from fastapi import UploadFile
from minio import Minio, S3Error

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)s - %(asctime)s - %(levelname)s - %(message)s'
)

# Параметры S3
# BUCKET_NAME = 'music-hub-bucket'
# имя файла с хранилища
# OBJECT_KEY = 'песня.mp3'
# Путь куда будет сохраняться загруженый файл
# DOWNLOAD_PATH = 'local/песня.mp3'


class S3Client:
    def __init__(
        self,
        service_name: str,
        endpoint_url: str,
        aws_secret_access_key: str,
        aws_access_key_id: str,
        region_name: str,
        use_ssl: bool,
        bucket_name: str
    ) -> None:
        self.config = {
            'service_name': service_name,
            'endpoint_url': endpoint_url,
            'aws_secret_access_key': aws_secret_access_key,
            'aws_access_key_id': aws_access_key_id,
            'region_name': region_name,
            'use_ssl': use_ssl,
        }
        self.bucket_name = bucket_name

    @asynccontextmanager
    async def get_client(self):
        session = get_session()
        async with session.create_client(**self.config) as client:
            if not client.bucket_exists(self.bucket_name):
                await client.make_bucket(self.bucket_name)
            yield client

    async def upload_file_to_s3(self, file_name: str, file: UploadFile):
        if file is None:
            return None
        # имя файла который будет отображаться в хранилище
        OBJECT_KEY = file_name
        # путь куда будет загружаться файл
        UPLOAD_PATH = file_name
        async with self.get_client() as client:
            try:
                # Загрузка файла в S3
                await client.put_object(Bucket=self.bucket_name, Key=OBJECT_KEY, Body=file.file)
                logging.info(f'Файл %s успешно загружен в %s/%s', UPLOAD_PATH, self.bucket_name, OBJECT_KEY)
                return file_name
            except Exception as e:
                logging.info(f'Ошибка при загрузке файла: {e}')


    async def download_file_from_s3(self, file_name: str):
        OBJECT_KEY = file_name
        DOWNLOAD_PATH = file_name
        async with self.get_client() as client:
            try:
                # Загрузка объекта из S3
                response = await client.get_object(Bucket=self.bucket_name, Key=OBJECT_KEY)
                file = response.read()
                logging.info(f'Файл %s успешно загружен в %s', OBJECT_KEY, DOWNLOAD_PATH)
                return file
            except Exception as e:
                logging.info(f'Ошибка при загрузке файла: {e}')


s3_client = S3Client(
    service_name=settings.minio.service_name,
    endpoint_url=settings.minio.endpoint_url,
    aws_secret_access_key=settings.minio.aws_secret_access_key,
    aws_access_key_id=settings.minio.aws_access_key_id,
    region_name=settings.minio.region_name,
    use_ssl=settings.minio.use_ssl,
    bucket_name=settings.minio.bucket_name
)