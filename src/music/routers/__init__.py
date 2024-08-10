from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from music.routers.song_router import router as song_router
from music.routers.album_router import router as album_router


router = APIRouter()

router.include_router(song_router)
router.include_router(album_router)