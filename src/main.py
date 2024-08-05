from fastapi import FastAPI
from music.routers.song_router import router as music_router


app = FastAPI(
    title="MusicHub API"
)

app.include_router(music_router)
