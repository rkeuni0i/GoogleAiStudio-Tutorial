import os
import mimetypes
from typing import Dict, Any, Tuple
import yt_dlp

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MIME_MAP = {
    ".m4a": "audio/mp4",
    ".mp3": "audio/mp3",
    ".wav": "audio/wav",
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
    ".opus": "audio/opus",
    ".aac": "audio/aac",
}

def get_video_info(url: str) -> Dict[str, Any]:
    """유튜브 영상의 메타데이터(제목, 썸네일, 길이 등)를 조회합니다."""
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "id": info.get("id"),
            "title": info.get("title", "Unknown Title"),
            "uploader": info.get("uploader", "Unknown Channel"),
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail"),
            "description": info.get("description", "")[:200],
        }

def download_audio(url: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    유튜브 영상에서 오디오 스트림을 다운로드합니다.
    ffmpeg가 설치되어 있지 않은 환경을 고려하여
    m4a 또는 원본 오디오 포맷을 직접 다운로드합니다.
    
    Returns:
        (filepath, mime_type, video_info)
    """
    # 1. 메타데이터 먼저 조회
    info = get_video_info(url)
    video_id = info["id"]
    
    # 2. 이미 동일 ID의 오디오 파일이 존재하는지 확인 (캐싱)
    for ext, mime in MIME_MAP.items():
        candidate = os.path.join(DOWNLOAD_DIR, f"{video_id}{ext}")
        if os.path.exists(candidate) and os.path.getsize(candidate) > 0:
            return candidate, mime, info

    # 3. 오디오 스트림 다운로드
    # bestaudio[ext=m4a]를 최우선으로 다운로드하고, 없을 경우 다른 오디오 포맷 시도
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s")
    ydl_opts = {
        'format': 'ba[ext=m4a]/ba[ext=webm]/ba/b',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        # 스트림만 다운로드 (ffmpeg 후처리 제외)
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        download_result = ydl.extract_info(url, download=True)
        # 실제 저장된 파일 경로 찾기
        filename = ydl.prepare_filename(download_result)
        
        # 파일 확장자 확인 및 MIME 타입 결정
        ext = os.path.splitext(filename)[1].lower()
        mime_type = MIME_MAP.get(ext, "audio/mp4")
        
        if not os.path.exists(filename):
            # 간혹 outtmpl 확장자가 달라지는 경우 폴더 내 탐색
            for file in os.listdir(DOWNLOAD_DIR):
                if file.startswith(video_id):
                    filename = os.path.join(DOWNLOAD_DIR, file)
                    ext = os.path.splitext(filename)[1].lower()
                    mime_type = MIME_MAP.get(ext, "audio/mp4")
                    break

        return filename, mime_type, info
