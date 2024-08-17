from fastapi import FastAPI
from music.routers import router as music_router
from auth.routers import router as auth_router


app = FastAPI(
    title="MusicHub API"
)

app.include_router(music_router)
app.include_router(auth_router)

