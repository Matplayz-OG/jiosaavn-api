from typing import Union

from fastapi import APIRouter, HTTPException, Query

from app.schemas.album_schema import AlbumSchema
from app.services.saavn_service import SaavnService

router = APIRouter()


@router.get("/", response_model=Union[dict, AlbumSchema])
async def get_album(
    query: str = Query(..., description="Album URL or ID"),
    lyrics: bool = Query(False, description="Include song lyrics"),
):
    """
    Retrieve album details from Saavn.
    - **query**: Album URL or ID
    - **lyrics**: Include song lyrics in the response
    """
    if not query:
        raise HTTPException(
            status_code=400, detail="Query is required to search albums!"
        )
    try:
        # Extract album ID from URL or use direct ID
        album_id = SaavnService.get_album_id(query)
        album = SaavnService.get_album(album_id, include_lyrics=lyrics)
        if not album:
            raise HTTPException(status_code=404, detail="Album not found!")
        return album
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching album: {str(e)}"
        ) from e
