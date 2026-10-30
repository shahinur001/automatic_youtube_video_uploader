import os
import json
import time
import pickle
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# OAuth scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def generate_publish_times():
    """Generates a list of scheduled UTC ISO timestamps for uploads."""
    utc_time = datetime.now(timezone.utc)
    time_for_publish = []
    
    start_minute = 0 if utc_time.minute <= 40 else utc_time.minute
    for i in range(20):
        new_hour = utc_time.hour + i
        if new_hour < 23:
            new_time = utc_time.replace(hour=new_hour % 24, minute=0, second=0, microsecond=0)
        elif 24 <= new_hour <= 25:
            new_time = utc_time.replace(day=utc_time.day + 1, hour=new_hour % 24, minute=0, second=0, microsecond=0)
        else:
            new_time = utc_time.replace(day=utc_time.day + 1, hour=(new_hour + 4) % 24, minute=0, second=0, microsecond=0)
        time_for_publish.append(str(new_time))
    return time_for_publish

def get_authenticated_service():
    """Handles OAuth2 authentication and saves/loads token.pickle securely."""
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("config/client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
            
    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description, tags, channel_id=None, privacy="public", publish_time=None):
    youtube = get_authenticated_service()
    
    snippet = {
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": "24"  # Entertainment
    }
    
    if channel_id:
        snippet["channelId"] = channel_id

    request_body = {
        "snippet": snippet,
        "status": {
            "privacyStatus": privacy,
            "madeForKids": False
        }
    }

    if publish_time:
        request_body["status"]["privacyStatus"] = "private"
        if isinstance(publish_time, str):
            try:
                publish_time = datetime.fromisoformat(publish_time)
            except ValueError:
                publish_time = None
        if publish_time:
            request_body["status"]["publishAt"] = publish_time.astimezone(timezone.utc).isoformat()

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    upload_request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)

    response = None
    while response is None:
        status, response = upload_request.next_chunk()
        if status:
            print(f"Uploading {os.path.basename(file_path)}... {int(status.progress() * 100)}%")
            
    print(f"✅ Upload complete! Title: {title} | Video ID: {response.get('id')}")
    return response

if __name__ == "__main__":
    # Change this to your local video directory
    base_folder = r"D:\<video folder name>" 
    publish_times = generate_publish_times()
    
    # Optional: specify your channel ID if required, otherwise leave as None
    CHANNEL_ID = "YOUR CHANNEL ID" 

    for i in range(1, 4):
        folder_name = f"video ({i})"
        folder_path = os.path.join(base_folder, folder_name)
        
        if os.path.isdir(folder_path):
            txt_file = os.path.join(folder_path, "video_info.txt")
            if os.path.exists(txt_file):
                with open(txt_file, "r", encoding="utf-8") as f:
                    video_info = json.load(f)

                video_names = video_info.get("fileName")
                video_name = f"grok-video-{video_names}.mp4"
                video_path = os.path.join(folder_path, video_name)
                
                if os.path.exists(video_path):
                    pub_time = publish_times[i-1]
                    upload_video(
                        file_path=video_path,
                        title=video_info.get("title", "Default Title"),
                        description=video_info.get("description", "No description"),
                        tags=video_info.get("tags", []),
                        channel_id=CHANNEL_ID,
                        privacy=video_info.get("privacy", "public"),
                        publish_time=pub_time
                    )
                    time.sleep(60)  # Pause 1 minute between uploads
                else:
                    print(f"❌ Video file '{video_name}' not found in {folder_path}")