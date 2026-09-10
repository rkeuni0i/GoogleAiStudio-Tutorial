import os
import re
from typing import Dict, Any, Tuple, Optional
import yt_dlp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MIME_MAP = {
    ".m4a": "audio/mp4",
    ".mp3": "audio/mp3",
    ".wav": "audio/wav",
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
    ".opus": "audio/opus",
}

def extract_video_id(url: str) -> Optional[str]:
    """YouTube URL에서 11자리 비디오 ID를 추출합니다."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})',
        r'youtu\.be\/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_metadata(url: str) -> Dict[str, Any]:
    """YouTube 영상의 메타데이터(제목, 채널명, 길이, 썸네일 등)를 조회합니다."""
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_id = info.get("id") or extract_video_id(url)
        return {
            "video_id": video_id,
            "title": info.get("title", "YouTube Video"),
            "uploader": info.get("uploader", "Unknown Channel"),
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail"),
            "view_count": info.get("view_count", 0),
        }

def extract_audio(url: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    YouTube 영상의 오디오 스트림을 다운로드합니다.
    ffmpeg 의존성 없이 m4a/webm 스트림을 직접 다운로드합니다.
    캐시가 존재하면 재다운로드를 건너뜁니다.
    
    Returns:
        (filepath, mime_type, metadata)
    """
    metadata = get_video_metadata(url)
    video_id = metadata["video_id"]
    
    # 1. 캐시 확인
    for ext, mime in MIME_MAP.items():
        cached_path = os.path.join(DOWNLOAD_DIR, f"{video_id}{ext}")
        if os.path.exists(cached_path) and os.path.getsize(cached_path) > 0:
            return cached_path, mime, metadata

    # 2. 오디오 스트림 다운로드
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s")
    ydl_opts = {
        'format': 'ba[ext=m4a]/ba[ext=webm]/ba/b',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        download_result = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(download_result)
        ext = os.path.splitext(filename)[1].lower()
        mime_type = MIME_MAP.get(ext, "audio/mp4")

        if not os.path.exists(filename):
            for file in os.listdir(DOWNLOAD_DIR):
                if file.startswith(video_id):
                    filename = os.path.join(DOWNLOAD_DIR, file)
                    ext = os.path.splitext(filename)[1].lower()
                    mime_type = MIME_MAP.get(ext, "audio/mp4")
                    break

        return filename, mime_type, metadata
