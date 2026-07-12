# Check which YouTube channel is connected to the MCP token
# Run: python check_channel.py

import os, json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).parent
TOKEN_FILE = BASE_DIR / "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

youtube = build('youtube', 'v3', credentials=creds)

result = youtube.channels().list(part='snippet,id,statistics', mine=True).execute()

print("=" * 55)
print("CONNECTED YOUTUBE CHANNEL")
print("=" * 55)
for ch in result.get('items', []):
    print(f"Channel ID  : {ch['id']}")
    print(f"Name        : {ch['snippet']['title']}")
    print(f"Custom URL  : {ch['snippet'].get('customUrl', 'N/A')}")
    print(f"Subscribers : {ch['statistics'].get('subscriberCount', 'hidden')}")
    print(f"Videos      : {ch['statistics'].get('videoCount', '?')}")
    print(f"Channel URL : https://www.youtube.com/channel/{ch['id']}")
print("=" * 55)
print()
print("Expected: @zoltangero / youtube.com/zoltangero")
print("If different -> wrong channel was authorized!")
