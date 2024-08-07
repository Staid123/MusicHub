import logging
from typing import Annotated, Any
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from music.enums import Genre
from music.schemas import Files, SongOut
from database import db_helper
from music.service.song_service import SongService, get_song_service
from music.utils import get_music_filters


# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)s - %(asctime)s - %(levelname)s - %(message)s'
)

router = APIRouter(
    prefix="/music", 
    tags=["Music Operations"],
)


@router.get("/", response_model=list[SongOut])
async def get_all_songs(
    song_service: Annotated[SongService, Depends(get_song_service)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    filters: Annotated[dict[str, Any], Depends(get_music_filters)],
) -> list[SongOut]:
    return await song_service.list_songs(
        session=session,
        **filters
    )

@router.post("/", response_model=Files, status_code=status.HTTP_201_CREATED)
async def create_song(
    name: Annotated[str, Form()],
    genre: Annotated[Genre, Form()],
    artist_id: Annotated[int, Form(gt=0)],
    album_id: Annotated[int, Form(gt=0)],
    song_file: Annotated[UploadFile, File(...)],
    photo_file: Annotated[UploadFile, File(...)],
    song_service: Annotated[SongService, Depends(get_song_service)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Files:
    return await song_service.create_song(
        session=session,
        name=name,
        genre=genre,
        artist_id=artist_id,
        album_id=album_id,
        song_file=song_file,
        photo_file=photo_file
    )


# async def s3_download(key: str):
#     try:
#         return s3.Object(bucket_name=AWS_BUCKET, key=key).get()['Body'].read()
#     except ClientError as err:
#         logging.error(str(err))


