# JagoBD IPTV Playlist Generator

Automatically generates M3U playlist from jagobd.com website and updates every 2 hours using GitHub Actions.

## Features
- Auto-scrapes jagobd.com for stream links
- Tests links for functionality
- Generates M3U playlist
- Auto-updates every 2 hours via GitHub Actions

## Manual Usage
```bash
pip install -r requirements.txt
python generate_playlist.py
