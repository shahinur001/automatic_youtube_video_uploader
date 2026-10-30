# YouTube Automated Uploader

An automated Python tool utilizing the YouTube Data API v3 to manage scheduled video uploads, metadata parsing, and automated time-slot generation for a single YouTube channel.

## 🚀 Features

- **Automated Scheduling**: Generates sequential ISO-8601 UTC timestamp slots for scheduled uploads.
- **OAuth2 Token Persistence**: Securely caches credentials via `token.pickle` to avoid repetitive browser logins.
- **Batch Processing**: Automatically scans local directories for video files and matching `video_info.txt` metadata (titles, descriptions, tags).
- **Private-to-Public Automation**: Handles private scheduling (`publishAt`) via the YouTube API.

---

## 📁 Project Structure

```text
youtube-auto-uploader/
│
├── config/
│   └── client_secret.json       # Your Google Cloud OAuth credentials
|
├── videos/
│   └── video (1)/
│       └── grok-video-<video_name>.mp4
│       └── video_info.txt
│   └── video (2)/
│       └── grok-video-<video_name>.mp4
│       └── video_info.txt
│   └── video (3)/
│       └── grok-video-<video_name>.mp4
│       └── video_info.txt
├── token.pickle                 # Generated OAuth session token
├── main.py                      # Core automation script
├── requirements.txt             # Python package dependencies
├── .gitignore                   # Excludes sensitive files and local media
└── README.md                    # Project documentation