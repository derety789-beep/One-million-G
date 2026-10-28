"""Accès à l'API YouTube Data v3."""

import logging
from functools import lru_cache
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import config

log = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


@lru_cache(maxsize=1)
def client():
    creds = Credentials(
        token=None,
        refresh_token=config.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.google_client_id,
        client_secret=config.google_client_secret,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


@lru_cache(maxsize=1)
def my_channel() -> dict:
    resp = client().channels().list(part="id,snippet,statistics,contentDetails", mine=True).execute()
    items = resp.get("items", [])
    if not items:
        raise RuntimeError("Aucune chaîne YouTube trouvée pour ce compte Google.")
    return items[0]


def channel_statistics() -> dict:
    resp = client().channels().list(part="statistics", mine=True).execute()
    return resp["items"][0]["statistics"]


def upload_video(path: Path, title: str, description: str, tags: list[str], privacy: str,
                 category_id: str = "22", thumbnail: Path | None = None) -> str:
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(path), chunksize=8 * 1024 * 1024, resumable=True)
    request = client().videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            log.info("Envoi de %s : %d%%", path.name, int(status.progress() * 100))

    video_id = response["id"]
    if thumbnail and thumbnail.exists():
        client().thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumbnail))).execute()
    return video_id


def recent_comment_threads(max_results: int = 50) -> list[dict]:
    resp = client().commentThreads().list(
        part="snippet,replies",
        allThreadsRelatedToChannelId=my_channel()["id"],
        order="time",
        maxResults=max_results,
        textFormat="plainText",
    ).execute()
    return resp.get("items", [])


def video_title(video_id: str) -> str:
    resp = client().videos().list(part="snippet", id=video_id).execute()
    items = resp.get("items", [])
    return items[0]["snippet"]["title"] if items else ""


def reply_to_comment(parent_id: str, text: str) -> None:
    client().comments().insert(
        part="snippet",
        body={"snippet": {"parentId": parent_id, "textOriginal": text}},
    ).execute()


def latest_videos_stats(count: int = 5) -> list[dict]:
    uploads_playlist = my_channel()["contentDetails"]["relatedPlaylists"]["uploads"]
    items = client().playlistItems().list(
        part="contentDetails", playlistId=uploads_playlist, maxResults=count
    ).execute().get("items", [])
    ids = [item["contentDetails"]["videoId"] for item in items]
    if not ids:
        return []
    videos = client().videos().list(part="snippet,statistics", id=",".join(ids)).execute()
    return [
        {
            "title": v["snippet"]["title"],
            "views": int(v["statistics"].get("viewCount", 0)),
            "likes": int(v["statistics"].get("likeCount", 0)),
            "comments": int(v["statistics"].get("commentCount", 0)),
        }
        for v in videos.get("items", [])
    ]
