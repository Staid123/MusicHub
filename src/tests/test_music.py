import pytest
from fastapi.testclient import TestClient
from music.schemas import Genre

@pytest.mark.asyncio
async def test_get_all_songs(client: TestClient):
    response = client.get("/music/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_song(client: TestClient):
    with open("test_song.mp3", "rb") as song_file, open("test_photo.jpg", "rb") as photo_file:
        response = client.post(
            "/music/",
            files={
                "song_file": ("test_song.mp3", song_file, "audio/mpeg"),
                "photo_file": ("test_photo.jpg", photo_file, "image/jpeg"),
            },
            data={
                "name": "Test Song",
                "genre": Genre(name="Rock").json(),
                "artist_id": 1,
                "album_id": 1
            }
        )
        assert response.status_code == 201
        assert "song_filename" in response.json()
        assert "photo_filename" in response.json()