import os
import csv
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, "transcripts.csv")

FIELDNAMES = [
    "video_id",
    "url",
    "title",
    "uploader",
    "duration",
    "thumbnail",
    "transcript_json",
    "created_at"
]

def init_csv_storage():
    """CSV 파일이 존재하지 않으면 헤더를 작성하여 초기화합니다."""
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def get_saved_transcript(video_id_or_url: str) -> Optional[Dict[str, Any]]:
    """
    CSV 파일에서 video_id 또는 url과 일치하는 저장된 전사 데이터를 조회합니다.
    존재할 경우 파싱된 딕셔너리를 반환하고, 없으면 None을 반환합니다.
    """
    if not os.path.exists(CSV_FILE_PATH):
        return None

    try:
        with open(CSV_FILE_PATH, mode="r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # video_id 또는 url이 일치하는지 확인
                if (row.get("video_id") == video_id_or_url or 
                    row.get("url") == video_id_or_url or 
                    (video_id_or_url in row.get("url", ""))):
                    
                    try:
                        transcript_data = json.loads(row.get("transcript_json", "[]"))
                    except Exception:
                        transcript_data = []

                    # 정상적인 자막 데이터가 있는 경우만 반환
                    if transcript_data and len(transcript_data) > 0:
                        return {
                            "video_id": row.get("video_id", ""),
                            "url": row.get("url", ""),
                            "title": row.get("title", ""),
                            "uploader": row.get("uploader", ""),
                            "duration": int(row.get("duration") or 0),
                            "thumbnail": row.get("thumbnail", ""),
                            "transcript": transcript_data,
                            "created_at": row.get("created_at", "")
                        }
    except Exception as e:
        print(f"[CSV Read Error] {e}")

    return None

def save_transcript_to_csv(
    video_id: str,
    url: str,
    title: str,
    uploader: str,
    duration: int,
    thumbnail: str,
    transcript: List[Dict[str, Any]]
) -> bool:
    """
    새로 추출된 영상 정보와 transcript를 CSV 파일에 저장합니다.
    이미 동일한 video_id가 저장되어 있으면 중복 저장을 방지합니다.
    """
    init_csv_storage()

    # 이미 저장되어 있는지 확인
    existing = get_saved_transcript(video_id)
    if existing:
        return True

    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transcript_json_str = json.dumps(transcript, ensure_ascii=False)

        new_row = {
            "video_id": video_id,
            "url": url,
            "title": title,
            "uploader": uploader,
            "duration": duration,
            "thumbnail": thumbnail or "",
            "transcript_json": transcript_json_str,
            "created_at": now_str
        }

        with open(CSV_FILE_PATH, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(new_row)

        print(f"[CSV Saved] {video_id} saved to {CSV_FILE_PATH}")
        return True
    except Exception as e:
        print(f"[CSV Save Error] {e}")
        return False
