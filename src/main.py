from fastapi import FastAPI
from music.routers import router


app = FastAPI(
    title="MusicHub API"
)

app.include_router(router)
