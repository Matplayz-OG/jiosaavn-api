# JioSaavn API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A high-performance unofficial API for JioSaavn, written in Python using the FastAPI framework. This API allows you to fetch DRM-free songs, cover art, lyrics, albums, playlists, artist information, and more.

## Tech Stack

* **Language:** Python3
* **Framework:** FastAPI
* **Libraries:**
    * `requests`: For making HTTP requests to the JioSaavn website.
    * `pyDes`: For decrypting encrypted media URLs.
    * `pydantic`: For data validation and serialization.
    * `fastapi`: For building the API.
    * `uvicorn`: For serving the API. 
    * `markdown`: For rendering the README.md in the browser.

## Architecture Overview

This API interacts with the JioSaavn website by scraping data and utilizing undocumented APIs. It then processes and formats the retrieved data, including decrypting media URLs, to provide a clean and consistent JSON response.

**Data Flow:**

1. **Request:** A client sends a request to a specific API endpoint (e.g., `/song/`).
2. **Fetch:** The API sends a request to the JioSaavn website to retrieve the relevant data.
3. **Process:** The API processes the raw data, extracts necessary information, and formats it. This may include decrypting media URLs using `pyDes` and cleaning up strings.
4. **Response:** The API returns the processed data as a JSON response to the client.

## Design Choices

* **FastAPI:** Chosen for its speed, ease of use, and built-in features like automatic documentation generation.
* **pydantic:** Used for data validation and serialization, ensuring data integrity and consistency.
* **Asynchronous Requests:**  Using `requests` to handle requests from JioSaavn Website.

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anxkhn/jiosaavn-api
   ```
2. **Install dependencies:**
   ```bash
   cd jiosaavn-api
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   fastapi dev main.py
   ```
4. **Access the API documentation:**
   * Swagger UI: http://localhost:8000/docs
   * ReDoc: http://localhost:8000/redoc

or use Docker via 
```bash
docker-compose up --build
```

## API Endpoints

**Songs:**

* **`/song/`:** Search for songs.
    * **Query Parameters:**
        * `query`: Search term for finding songs (required).
        * `lyrics`: Include song lyrics in the response (optional, default: False).
        * `songdata`: Fetch full song details or basic information (optional, default: True).
* **`/song/get`:** Retrieve a specific song by its ID.
    * **Query Parameters:**
        * `song_id`: Unique identifier of the song (required).
        * `lyrics`: Include song lyrics in the response (optional, default: False).

**Albums:**

* **`/album/`:** Retrieve album details.
    * **Query Parameters:**
        * `query`: Album URL or ID (required).
        * `lyrics`: Include song lyrics in the response (optional, default: False).

**Playlists:**

* **`/playlist/`:** Retrieve playlist details.
    * **Query Parameters:**
        * `query`: Playlist URL or ID (required).
        * `lyrics`: Include song lyrics in the response (optional, default: False).

**Lyrics:**

* **`/lyrics/`:** Retrieve song lyrics.
    * **Query Parameters:**
        * `query`: Song URL, link, or direct lyrics ID (required).

**Health:**

* **`/ping`:** Basic health check endpoint.

## File Structure and Breakdown

```
├── app
│   ├── schemas
│   │   ├── song_schema.py
│   │   ├── playlist_schema.py
│   │   └── album_schema.py
│   ├── services
│   │   ├── saavn_service.py
│   │   └── crypto_service.py
│   ├── routes
│   │   ├── song_routes.py
│   │   ├── playlist_routes.py
│   │   ├── lyrics_routes.py
│   │   └── album_routes.py
│   ├── core
│   │   └── exceptions.py
│   └── config.py
├── main.py
├── requirements.txt
└── README.md

```

* **`app/schemas`:** Contains Pydantic models for defining the structure of API responses.
* **`app/services`:** Contains the core logic for interacting with the JioSaavn website and processing data.
    * **`saavn_service.py`:**  Handles fetching and processing data from JioSaavn.
    * **`crypto_service.py`:**  Handles decryption of media URLs.
* **`app/routes`:** Defines the API endpoints and their corresponding handlers.
* **`app/core`:** Contains modules for exception handling and other core functionalities.
* **`app/config.py`:**  Manages application configuration settings.
* **`main.py`:**  The main application file that creates and runs the FastAPI app.
* **`requirements.txt`:** Lists the project dependencies.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.