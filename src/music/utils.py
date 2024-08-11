from typing import Any, Optional

from fastapi import Query

from music.enums import Genre


def get_music_filters(
    id: Optional[int] = Query(default=None, gt=0),
    name: str = Query(default=None),
    genre: "Genre" = Query(default=None),
    artist_id: int = Query(default=None, gt=0),
    album_id: int = Query(default=None, gt=0),
    skip: int = Query(default=0, ge=0), 
    limit: int = Query(default=10, ge=1),
) -> dict[str, Any]:
    filters = {}
    if id:
        filters['id'] = id
    if name:
        filters['name'] = name
    if genre:
        filters['genre'] = genre
    if artist_id:
        filters['artist_id'] = artist_id
    if album_id:
        filters['album_id'] = album_id

    filters['skip'] = skip
    filters['limit'] = limit
    return filters


def get_album_filters(
    id: Optional[int] = Query(default=None, gt=0),
    name: str = Query(default=None),
    artist_id: int = Query(default=None, gt=0),
    skip: int = Query(default=0, ge=0), 
    limit: int = Query(default=10, ge=1),
) -> dict[str, Any]:
    filters = {}
    if id:
        filters['id'] = id
    if name:
        filters['name'] = name
    if artist_id:
        filters['artist_id'] = artist_id
    filters['skip'] = skip
    filters['limit'] = limit
    return filters
