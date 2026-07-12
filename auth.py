"""
YouTube MCP - One-time OAuth Authorization Script
Run this ONCE to get your refresh token.
After this, the MCP server handles token refresh automatically.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")


def main():
    print("🎬 YouTube MCP - OAuth Authorization")
    print("=" * 40)
    print("A browser window will open.")
    print("Log in with: humorketing@gmail.com")
    print("=" * 40)

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=8080, open_browser=True)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    print(f"\n✅ Authorization successful!")
    print(f"✅ Token saved to: {TOKEN_FILE}")
    print(f"\nYou can now start the YouTube MCP server.")


if __name__ == "__main__":
    main()
