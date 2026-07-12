# YouTube MCP - Claude Desktop Config Setup
# Automatically adds the YouTube MCP server to Claude's config file.
# Run this once from PowerShell:
#   python setup_claude_config.py

import json
import os
from pathlib import Path

# Paths
CONFIG_PATH = Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
MCP_SCRIPT  = r"C:\Users\gdp\Documents\Claude\Projects\YouTube\youtube-mcp\youtube_mcp.py"

# The YouTube MCP entry to add
YT_MCP_ENTRY = {
    "command": "python",
    "args": [MCP_SCRIPT]
}

def main():
    print("🎬 YouTube MCP - Claude Desktop Config Setup")
    print("=" * 50)

    # Load existing config or start fresh
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"✅ Existing config found: {CONFIG_PATH}")
    else:
        config = {}
        print(f"📄 Creating new config at: {CONFIG_PATH}")

    # Ensure mcpServers key exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Check if already added
    if "youtube" in config["mcpServers"]:
        print("ℹ️  YouTube MCP already in config — updating...")

    # Add/update the YouTube MCP entry
    config["mcpServers"]["youtube"] = YT_MCP_ENTRY

    # Show current MCP servers
    print(f"\n📋 MCP servers in config after update:")
    for name in config["mcpServers"]:
        marker = "⭐" if name == "youtube" else "  "
        print(f"  {marker} {name}")

    # Save config
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Config saved to: {CONFIG_PATH}")
    print("\n🔄 FONTOS: Indítsd újra a Claude desktop appot!")
    print("   File → Quit → nyisd meg újra")
    print("\n🎉 YouTube MCP kész! Az Agent Team mostantól tud publikálni.")

if __name__ == "__main__":
    main()
