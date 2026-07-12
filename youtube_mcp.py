"""
YouTube MCP Server
Provides tools for the YT Flywheel Agent Team to publish videos autonomously.

Tools:
  - upload_video         : Upload MP4 to YouTube channel
  - set_thumbnail        : Set custom thumbnail for a video
  - update_video_metadata: Update title, description, tags
  - publish_video        : Make video public or schedule it
  - list_channel_videos  : List recent channel videos
  - get_video_status     : Get status + stats for a video
"""

import os
import json
from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

mcp = FastMCP("YouTube")

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")


def get_youtube_client():
    """Get authenticated YouTube API client, refreshing token if needed."""
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            "token.json not found. Run auth.py first to authorize."
        )

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        else:
            raise ValueError(
                "Credentials expired and cannot refresh. Run auth.py again."
            )

    return build("youtube", "v3", credentials=creds)


# ─────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────

@mcp.tool()
def upload_video(
    file_path: str,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "27",
    privacy_status: str = "private",
) -> dict:
    """
    Upload a video file to the YouTube channel.

    Args:
        file_path     : Absolute path to the .mp4 file
        title         : Video title (max 100 chars)
        description   : Full video description including links and chapters
        tags          : List of keyword tags
        category_id   : YouTube category ID (27 = Education, 28 = Science & Tech)
        privacy_status: 'private', 'unlisted', or 'public'

    Returns dict with video_id and URL.
    """
    youtube = get_youtube_client()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        _, response = request.next_chunk()

    return {
        "video_id": response["id"],
        "url": f"https://www.youtube.com/watch?v={response['id']}",
        "title": response["snippet"]["title"],
        "status": response["status"]["privacyStatus"],
    }


@mcp.tool()
def set_thumbnail(video_id: str, thumbnail_path: str) -> dict:
    """
    Set a custom thumbnail for a YouTube video.

    Args:
        video_id       : YouTube video ID (e.g. 'dQw4w9WgXcQ')
        thumbnail_path : Absolute path to .jpg or .png file (max 2MB)

    Returns success confirmation.
    """
    youtube = get_youtube_client()

    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path),
    ).execute()

    return {"success": True, "video_id": video_id}


@mcp.tool()
def update_video_metadata(
    video_id: str,
    title: str = None,
    description: str = None,
    tags: list[str] = None,
    privacy_status: str = None,
) -> dict:
    """
    Update metadata for an existing YouTube video.
    Only provide the fields you want to change.

    Args:
        video_id      : YouTube video ID
        title         : New title (optional)
        description   : New description (optional)
        tags          : New tags list (optional)
        privacy_status: 'private', 'unlisted', or 'public' (optional)
    """
    youtube = get_youtube_client()

    video = youtube.videos().list(part="snippet,status", id=video_id).execute()
    if not video["items"]:
        return {"error": f"Video {video_id} not found"}

    snippet = video["items"][0]["snippet"]
    status = video["items"][0]["status"]

    if title:
        snippet["title"] = title
    if description:
        snippet["description"] = description
    if tags:
        snippet["tags"] = tags
    if privacy_status:
        status["privacyStatus"] = privacy_status

    response = youtube.videos().update(
        part="snippet,status",
        body={"id": video_id, "snippet": snippet, "status": status},
    ).execute()

    return {
        "video_id": response["id"],
        "title": response["snippet"]["title"],
        "status": response["status"]["privacyStatus"],
    }


@mcp.tool()
def publish_video(video_id: str, scheduled_time: str = None) -> dict:
    """
    Publish a video immediately or schedule it for later.

    Args:
        video_id       : YouTube video ID
        scheduled_time : ISO 8601 UTC datetime to schedule (e.g. '2024-06-01T15:00:00Z')
                         Leave empty to publish immediately.
    """
    youtube = get_youtube_client()

    if scheduled_time:
        status_body = {
            "privacyStatus": "private",
            "publishAt": scheduled_time,
        }
    else:
        status_body = {"privacyStatus": "public"}

    response = youtube.videos().update(
        part="status",
        body={"id": video_id, "status": status_body},
    ).execute()

    return {
        "video_id": video_id,
        "status": response["status"]["privacyStatus"],
        "scheduled_at": scheduled_time or "published immediately",
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


@mcp.tool()
def list_channel_videos(max_results: int = 10) -> list:
    """
    List the most recent videos on the channel.

    Args:
        max_results: Number of videos to return (default 10, max 50)
    """
    youtube = get_youtube_client()

    channel = youtube.channels().list(part="contentDetails", mine=True).execute()
    playlist_id = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=max_results,
    ).execute()

    return [
        {
            "video_id": item["snippet"]["resourceId"]["videoId"],
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"],
            "url": f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}",
        }
        for item in videos.get("items", [])
    ]


@mcp.tool()
def get_video_status(video_id: str) -> dict:
    """
    Get the current status, metadata, and basic stats for a video.

    Args:
        video_id: YouTube video ID
    """
    youtube = get_youtube_client()

    response = youtube.videos().list(
        part="snippet,status,statistics", id=video_id
    ).execute()

    if not response["items"]:
        return {"error": f"Video {video_id} not found"}

    item = response["items"][0]
    return {
        "video_id": video_id,
        "title": item["snippet"]["title"],
        "status": item["status"]["privacyStatus"],
        "views": item["statistics"].get("viewCount", 0),
        "likes": item["statistics"].get("likeCount", 0),
        "comments": item["statistics"].get("commentCount", 0),
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


if __name__ == "__main__":
    mcp.run()
