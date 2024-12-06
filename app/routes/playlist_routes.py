from typing import Union

from fastapi import APIRouter, HTTPException, Query

from app.schemas.playlist_schema import PlaylistSchema
from app.services.saavn_service import SaavnService

router = APIRouter()


@router.get("/", response_model=Union[dict, PlaylistSchema])
async def get_playlist(
    query: str = Query(..., description="Playlist URL or ID"),
    lyrics: bool = Query(False, description="Include song lyrics"),
):
    """
    Retrieve playlist details from Saavn.
    - **query**: Playlist URL or ID
    - **lyrics**: Include song lyrics in the response
    """
    if not query:
        raise HTTPException(
            status_code=400, detail="Query is required to search playlists!"
        )
    try:
        # Extract playlist ID from URL or use direct ID
        playlist_id = SaavnService.get_playlist_id(query)
        playlist = SaavnService.get_playlist(
            playlist_id, include_lyrics=lyrics
        )
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found!")
        return playlist
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching playlist: {str(e)}"
        ) from e
