import boto3
import logging

from fastapi import HTTPException, UploadFile, status
import magic
from config import settings
from music.constants import MAX_FILE_SIZES

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)s - %(asctime)s - %(levelname)s - %(message)s'
)


class S3Client:
    def __init__(self):
        self.AWS_BUCKET_NAME = settings.aws.bucket_name
        self.bucket = boto3.resource('s3').Bucket(self.AWS_BUCKET_NAME)


    async def __aenter__(self):
        logging.info("Entering async context")
        return self

    
    async def __aexit__(self, exc_type, exc, tb):
        logging.info("Exiting async context")


    async def get_file_type(
        self, 
        contents: bytes, 
        SUPPORTED_FILE_TYPES: dict
    ) -> str:
        # Получаем тип файла
        file_type = magic.from_buffer(buffer=contents, mime=True)

        # Проверка, что этот тип есть в разрешенных типах файлов
        if file_type not in SUPPORTED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Unsupported file type: {file_type}. Supported types are {SUPPORTED_FILE_TYPES}'
            )
        return SUPPORTED_FILE_TYPES[file_type]


    async def s3_upload_file(
        self, 
        file: UploadFile, 
        key: str, 
        SUPPORTED_FILE_TYPES: dict
    ) -> None:
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='No file found!!'
            )
        contents = await file.read()
        file_type = await self.get_file_type(contents, SUPPORTED_FILE_TYPES)
        max_file_size = MAX_FILE_SIZES[file_type]
        size = len(contents)
        
        if not 0 < size <= max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Supported {file_type} file size is 0 - {max_file_size} MB'
            )

        logging.info(f'Uploading {key} to s3')
        self.bucket.put_object(Key=key, Body=contents)

