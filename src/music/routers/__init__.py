from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from music.routers.song_router import router as song_router
from music.routers.album_router import router as album_router

# интерфейс для введения токена (который автоматически отправляеятся в заголовки) после логина
http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(dependencies=[Depends(http_bearer)])

router.include_router(song_router)
router.include_router(album_router)