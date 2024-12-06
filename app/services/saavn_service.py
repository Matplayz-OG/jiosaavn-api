import json
import logging
import re
from typing import Dict, List, Optional, Union

import requests

from app.config import settings
from app.services.crypto_service import CryptoService

logger = logging.getLogger(__name__)


class SaavnService:
    """
    Service responsible for interacting with Saavn API and processing music data.
    """

    BASE_URL = settings.SAAVN_BASE_URL

    @classmethod
    def _format_string(cls, string: str) -> str:
        """
        Clean and format input strings.
        Args:
            string (str): Input string to format
        Returns:
            str: Formatted string
        """
        return (
            string.encode()
            .decode()
            .replace("&quot;", "'")
            .replace("&amp;", "&")
            .replace("&#039;", "'")
        )

    @classmethod
    def get_song_id(cls, url: str) -> str:
        """
        Extract song ID from a Saavn URL.
        Args:
            url (str): Saavn song URL
        Returns:
            str: Song ID
        """
        try:
            res = requests.get(url, timeout=settings.REQUEST_TIMEOUT)
            try:
                return (res.text.split('"pid":"'))[1].split('","')[0]
            except IndexError:
                return (
                    res.text.split('"song":{"type":"')[1]
                    .split('","image":')[0]
                    .split('"id":"')[-1]
                )
        except Exception as e:
            logger.error("Error extracting song ID: %s", e)
            raise

    @classmethod
    def get_album_id(cls, input_url: str) -> str:
        """
        Extract album ID from a Saavn URL.
        Args:
            input_url (str): Saavn album URL
        Returns:
            str: Album ID
        """
        try:
            res = requests.get(input_url, timeout=settings.REQUEST_TIMEOUT)
            try:
                return res.text.split('"album_id":"')[1].split('"')[0]
            except IndexError:
                return res.text.split('"page_id","')[1].split('","')[0]
        except Exception as e:
            logger.error("Error extracting album ID: %s", e)
            raise

    @classmethod
    def get_playlist_id(cls, input_url: str) -> str:
        """
        Extract playlist ID from a Saavn URL.
        Args:
            input_url (str): Saavn playlist URL
        Returns:
            str: Playlist ID
        """
        try:
            res = requests.get(input_url, timeout=settings.REQUEST_TIMEOUT)
            try:
                return res.text.split('"type":"playlist","id":"')[1].split(
                    '"'
                )[0]
            except IndexError:
                return res.text.split('"page_id","')[1].split('","')[0]
        except Exception as e:
            logger.error("Error extracting playlist ID: %s", e)
            raise

    @classmethod
    def get_song(
        cls, song_id: str, include_lyrics: bool = False
    ) -> Optional[Dict]:
        """
        Retrieve detailed song information.
        Args:
            song_id (str): Song ID
            include_lyrics (bool, optional): Whether to include lyrics. Defaults to False.
        Returns:
            Optional[Dict]: Processed song data
        """
        try:
            song_url = f"{cls.BASE_URL}?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids={song_id}"
            song_response = requests.get(
                song_url, timeout=settings.REQUEST_TIMEOUT
            )
            song_data = song_response.text.encode().decode("unicode-escape")
            song_data = json.loads(song_data)
            if song_id not in song_data:
                return None
            processed_song = cls.format_song_data(
                song_data[song_id], include_lyrics
            )
            return processed_song
        except Exception as e:
            logger.error("Error fetching song details: %s", e)
            raise

    @classmethod
    def get_album(
        cls, album_id: str, include_lyrics: bool = False
    ) -> Optional[Dict]:
        """
        Retrieve album details.
        Args:
            album_id (str): Album ID
            include_lyrics (bool, optional): Whether to include lyrics. Defaults to False.
        Returns:
            Optional[Dict]: Processed album data
        """
        try:
            album_url = f"{cls.BASE_URL}?__call=content.getAlbumDetails&_format=json&cc=in&_marker=0%3F_marker%3D0&albumid={album_id}"
            response = requests.get(
                album_url, timeout=settings.REQUEST_TIMEOUT
            )
            album_data = response.text.encode().decode("unicode-escape")
            album_data = json.loads(album_data)
            # Process album data
            album_data["image"] = album_data["image"].replace(
                "150x150", "500x500"
            )
            album_data["name"] = cls._format_string(album_data["name"])
            album_data["primary_artists"] = cls._format_string(
                album_data["primary_artists"]
            )
            # Process songs in the album
            for song in album_data["songs"]:
                cls.format_song_data(song, include_lyrics)
            return album_data
        except Exception as e:
            logger.error("Error fetching album details: %s", e)
            raise

    @classmethod
    def get_playlist(
        cls, playlist_id: str, include_lyrics: bool = False
    ) -> Optional[Dict]:
        """
        Retrieve playlist details.
        Args:
            playlist_id (str): Playlist ID
            include_lyrics (bool, optional): Whether to include lyrics. Defaults to False.
        Returns:
            Optional[Dict]: Processed playlist data
        """
        try:
            playlist_url = f"{cls.BASE_URL}?__call=playlist.getDetails&_format=json&cc=in&_marker=0%3F_marker%3D0&listid={playlist_id}"
            response = requests.get(
                playlist_url, timeout=settings.REQUEST_TIMEOUT
            )
            playlist_data = response.text.encode().decode("unicode-escape")
            playlist_data = json.loads(playlist_data)
            # Process playlist data
            playlist_data["firstname"] = cls._format_string(
                playlist_data["firstname"]
            )
            playlist_data["listname"] = cls._format_string(
                playlist_data["listname"]
            )
            # Process songs in the playlist
            for song in playlist_data["songs"]:
                cls.format_song_data(song, include_lyrics)
            return playlist_data
        except Exception as e:
            logger.error("Error fetching playlist details: %s", e)
            raise

    @classmethod
    def get_lyrics(cls, song_id: str) -> str:
        """
        Retrieve song lyrics.
        Args:
            song_id (str): Song ID
        Returns:
            str: Song lyrics
        """
        try:
            lyrics_url = f"{cls.BASE_URL}?__call=lyrics.getLyrics&ctx=web6dot0&api_version=4&_format=json&_marker=0%3F_marker%3D0&lyrics_id={song_id}"
            response = requests.get(
                lyrics_url, timeout=settings.REQUEST_TIMEOUT
            )
            lyrics_data = json.loads(response.text)
            return lyrics_data["lyrics"]
        except Exception as e:
            logger.error("Error fetching lyrics: %s", e)
            raise

    @classmethod
    def format_song_data(
        cls, data: Dict, include_lyrics: bool = False
    ) -> Dict[str, Union[str, None]]:
        """
        Format and process song data.
        Args:
            data (Dict): Raw song data
            include_lyrics (bool, optional): Whether to include lyrics. Defaults to False.
        Returns:
            Dict: Processed song data
        """
        try:
            # Process media URL
            data["media_url"] = CryptoService.decrypt_url(
                data["encrypted_media_url"]
            )
            # Adjust URL based on quality
            if data["320kbps"] != "true":
                data["media_url"] = data["media_url"].replace(
                    "_320.mp4", "_160.mp4"
                )
            # Process various fields
            for field in [
                "song",
                "music",
                "singers",
                "starring",
                "album",
                "primary_artists",
            ]:
                data[field] = cls._format_string(data.get(field, ""))
            data["image"] = data["image"].replace("150x150", "500x500")
            # Process lyrics if requested
            if include_lyrics and data.get("has_lyrics") == "true":
                data["lyrics"] = cls.get_lyrics(data["id"])
            else:
                data["lyrics"] = None
            # Process copyright text
            data["copyright_text"] = data.get("copyright_text", "").replace(
                "&copy;", "©"
            )
            return data
        except Exception as e:
            logger.error("Error formatting song data: %s", e)
            raise

    @classmethod
    def search_songs(
        cls, query: str, include_lyrics: bool = False, full_data: bool = True
    ) -> List[Dict]:
        """
        Search for songs on Saavn.
        Args:
            query (str): Search query
            include_lyrics (bool, optional): Whether to include lyrics. Defaults to False.
            full_data (bool, optional): Whether to fetch full song details. Defaults to True.
        Returns:
            List[Dict]: List of songs
        """
        try:
            search_url = f"{cls.BASE_URL}?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query={query}"
            response = requests.get(
                search_url, timeout=settings.REQUEST_TIMEOUT
            )
            # Process response
            response_text = response.text.encode().decode("unicode-escape")
            response_text = re.sub(
                r'\(From "([^"]+)"\)', r"(From '\1')", response_text
            )
            search_results = json.loads(response_text)
            song_results = search_results.get("songs", {}).get("data", [])
            # Return basic or full data
            if not full_data:
                return song_results
            songs = []
            for song in song_results:
                song_details = cls.get_song(song["id"], include_lyrics)
                if song_details:
                    songs.append(song_details)
            return songs
        except Exception as e:
            logger.error("Song search error: %s", e)
            raise
