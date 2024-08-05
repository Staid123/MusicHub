from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from music.routers.song_router import router as song_router
# from music.routers.answer_router import router as answer_router


router = APIRouter()

router.include_router(song_router)
# router.include_router(answer_router)