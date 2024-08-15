import logging
from typing import Annotated, Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import UserOut
from auth.validation import get_current_active_auth_user
from music.constants import ALBUMS
from music.schemas import Files, AlbumOut
from database import db_helper
from music.service.album_service import AlbumService, get_album_service
from music.utils import get_album_filters


# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)s - %(asctime)s - %(levelname)s - %(message)s'
)

router = APIRouter(
    prefix="/album", 
    tags=["Album Operations"],
)


@router.get("/", response_model=list[AlbumOut])
async def get_list_albums(
    album_service: Annotated[AlbumService, Depends(get_album_service)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    filters: Annotated[dict[str, Any], Depends(get_album_filters)],
) -> list[AlbumOut]:
    return await album_service.list_albums(
        session=session,
        **filters
    )


@router.post(
    "/",
    response_model=Files, 
    status_code=status.HTTP_201_CREATED, 
    response_model_exclude_none=True
)
async def create_album(
    name: Annotated[str, Form()],
    user: Annotated[UserOut, Depends(get_current_active_auth_user)],
    photo_file: Annotated[UploadFile, File(...)],
    album_service: Annotated[AlbumService, Depends(get_album_service)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Files:
    try:
        return await album_service.create_album(
            session=session,
            name=name,
            user=user,
            photo_file=photo_file
        )
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.patch(
    "/{album_id}/", 
    response_model=Files,
    response_model_exclude_none=True
)
async def update_album(
    album_id: int,
    user: Annotated[UserOut, Depends(get_current_active_auth_user)],
    album_service: Annotated[AlbumService, Depends(get_album_service)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    name: str | None = Form(default=None),
    photo_file: UploadFile | None = File(None),
) -> Files:
    return await album_service.update_album(
        session=session,
        name=name,
        album_id=album_id,
        photo_file=photo_file,
        user=user
    )


@router.delete("/{album_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(
    album_id: int,
    album_service: Annotated[AlbumService, Depends(get_album_service)],
    user: Annotated[UserOut, Depends(get_current_active_auth_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> None:
    return await album_service.delete_album(
        session=session,
        album_id=album_id,
        user=user
    )


@router.get("/download/", description="Enter only file name without folders")
async def download_album_photo(
    file_name: str,
    album_service: Annotated[AlbumService, Depends(get_album_service)],
) -> Response:
    contents = await album_service.download_song_or_photo_file(
        file_name=file_name,
        folder_type=ALBUMS
    )
    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'attachment;filename={file_name}',
            'Content-Type': 'application/octet-stream',
        }
    )
