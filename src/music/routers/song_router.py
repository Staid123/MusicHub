import logging
from typing import Annotated, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from music.schemas import SongIn, SongOut
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

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_song(
    song_in: SongIn,
    # user: Annotated[User, Depends(admin)],
    song_service: Annotated[SongService, Depends(get_song_service)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> None:
    return await song_service.create_song(
        session=session,
        song_in=song_in
    )