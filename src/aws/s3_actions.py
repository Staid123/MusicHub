import boto3
import logging
import mimetypes
from fastapi import HTTPException, UploadFile, status
from config import settings
from music.constants import MAX_FILE_SIZES
from botocore.exceptions import ClientError


logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)s - %(asctime)s - %(levelname)s - %(message)s'
)


class S3Client:
    def __init__(self):
        self.AWS_BUCKET_NAME = settings.aws.bucket_name
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(self.AWS_BUCKET_NAME)


    async def __aenter__(self):
        logging.info("Entering async context")
        return self

    
    async def __aexit__(self, exc_type, exc, tb):
        logging.info("Exiting async context")


    async def get_file_type(
        self, 
        file_name: str, 
        SUPPORTED_FILE_TYPES: dict
    ) -> str:
        # Получаем тип файла
        file_type, _ = mimetypes.guess_type(file_name)

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
        file_type = await self.get_file_type(file.filename, SUPPORTED_FILE_TYPES)
        max_file_size = MAX_FILE_SIZES[file_type]
        size = len(contents)
        
        if not 0 < size <= max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Supported {file_type} file size is 0 - {max_file_size} MB'
            )

        logging.info(f'Uploading {key} to s3')
        s3_object = self.bucket.put_object(Key=key, Body=contents)
        if not s3_object:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during loading file {file.filename}"
            )


    async def s3_delete_file(
        self,
        key: str,
    ) -> None:
        logging.info(f'Deleting {key} from s3')
        response = self.bucket.delete_objects(
            Delete={
                'Objects': [
                    {
                        'Key': key
                    }
                ]
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during deletion file {key}"
            )


    async def s3_update_file(
        self,
        file: UploadFile,
        old_key: str,
        new_key: str,
        SUPPORTED_FILE_TYPES: dict,
    ) -> None:
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='No file found!!'
            )
        logging.info(f'Trying to update {old_key} to {new_key} in s3')
        await self.s3_delete_file(
            key=old_key
        )
        await self.s3_upload_file(
            file=file,
            key=new_key,
            SUPPORTED_FILE_TYPES=SUPPORTED_FILE_TYPES
        )

    
    async def s3_download_file(
        self,
        file_name: str,
        key: str
    ) -> bytes:
        
        try:
            logging.info(f"Downloading file {file_name} from s3")
            return self.s3.Object(
                bucket_name=self.AWS_BUCKET_NAME, 
                key=key).get()['Body'].read()
        except ClientError as err:
            logging.error(str(err))

