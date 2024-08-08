import logging
from typing import Annotated, Any
from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
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


@router.patch("/{song_id}/", response_model=Files, response_model_exclude_none=True)
async def update_song(
    song_id: int,
    song_service: Annotated[SongService, Depends(get_song_service)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    name: str | None = Form(default=None),
    genre: Genre | None = Form(default=None),
    song_file: UploadFile | None = File(None),
    photo_file: UploadFile | None = File(None),
) -> Files:
    return await song_service.update_song(
        session=session,
        song_id=song_id,
        name=name,
        genre=genre,
        song_file=song_file,
        photo_file=photo_file
    )


@router.delete("/{song_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_song(
    song_id: int,
    song_service: Annotated[SongService, Depends(get_song_service)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> None:
    return await song_service.delete_song(
        song_id=song_id,
        session=session
    )


@router.get("/download", description="Enter only file name without folders")
async def download_song_or_photo(
    file_name: str,
    song_service: Annotated[SongService, Depends(get_song_service)],
) -> Response:
    contents = await song_service.download_song_or_photo_file(file_name=file_name)
    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'attachment;filename={file_name}',
            'Content-Type': 'application/octet-stream',
        }
    )
