from fastapi import FastAPI
from music.router import router as music_router
from fastapi_pagination import add_pagination


app = FastAPI(
    title="MusicHub API"
)

app.include_router(music_router)

add_pagination(app)