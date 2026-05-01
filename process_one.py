import json
import os
import re
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi

def sanitize_filename(title, max_length=50):
    if not title:
        return ""
    invalid_chars = r'[\\/*?:"<>|]'
    sanitized = re.sub(invalid_chars, '', title)
    sanitized = sanitized.replace(' ', '_')
    return sanitized[:max_length].rstrip('_')

video_url = 'https://www.youtube.com/watch?v=D4fkiQfzw_I'
video_id = 'D4fkiQfzw_I'
output_dir = 'Raw_Data'

# Get metadata with yt-dlp
ydl_opts = {
    'skip_download': True,
    'quiet': True,
    'no_warnings': True
}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(video_url, download=False)
    
    metadata = {
        'title': info.get('title'),
        'description': info.get('description'),
        'duration': info.get('duration'),
        'channel': info.get('channel'),
        'view_count': info.get('view_count'),
        'upload_date': info.get('upload_date'),
        'tags': info.get('tags', []),
        'thumbnail': info.get('thumbnail'),
        'categories': info.get('categories', [])
    }

# Get transcript with youtube-transcript-api
transcript_text = ""
try:
    transcript_list = YouTubeTranscriptApi().list(video_id)
    try:
        transcript = transcript_list.find_manually_created_transcript(['en'])
    except:
        transcript = transcript_list.find_generated_transcript(['en'])
    data = transcript.fetch()
    transcript_text = " ".join([item.text for item in data])
except Exception as e:
    print(f"Transcript error: {e}")
    transcript_text = ""

output = {
    'video_id': video_id,
    'metadata': metadata,
    'transcript': transcript_text
}

os.makedirs(output_dir, exist_ok=True)

# New filename format: {video_id}_{sanitized_title}.json
sanitized_title = sanitize_filename(metadata.get('title', ''))
if sanitized_title:
    filename = f'{video_id}_{sanitized_title}.json'
else:
    filename = f'{video_id}.json'

output_path = os.path.join(output_dir, filename)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'Saved: {filename}')
print(f'Title: {metadata["title"]}')
print(f'Transcript length: {len(transcript_text)} chars')
