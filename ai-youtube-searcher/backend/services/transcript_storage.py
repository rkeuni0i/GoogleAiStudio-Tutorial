import os
import csv
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import select, or_

from services.database import (
    Transcript,
    get_session,
    init_db,
    is_db_available
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, "transcripts.csv")

CSV_FIELDNAMES = [
    "video_id",
    "url",
    "title",
    "uploader",
    "duration",
    "thumbnail",
    "transcript_json",
    "created_at"
]

def init_storage():
    """데이터베이스 초기화 및 기존 CSV 데이터 마이그레이션 실행"""
    db_ok = init_db()
    if db_ok:
        migrate_csv_to_db()
    else:
        # DB 미연결 시 로컬 CSV 백업 초기화
        init_csv_backup()

def init_csv_backup():
    """CSV 파일이 없으면 헤더 생성"""
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()

def get_saved_transcript(video_id_or_url: str) -> Optional[Dict[str, Any]]:
    """
    1순위: PostgreSQL 데이터베이스에서 조회
    2순위: DB 미연결 시 로컬 CSV 파일에서 fallback 조회
    """
    # 1. PostgreSQL DB 조회
    if is_db_available():
        session = get_session()
        if session:
            try:
                stmt = select(Transcript).where(
                    or_(
                        Transcript.video_id == video_id_or_url,
                        Transcript.url == video_id_or_url
                    )
                )
                record = session.scalars(stmt).first()
                if record and record.transcript and len(record.transcript) > 0:
                    return record.to_dict()
            except Exception as e:
                print(f"[DB Query Error] {e}")
            finally:
                session.close()

    # 2. CSV 파일 Fallback 조회
    if os.path.exists(CSV_FILE_PATH):
        try:
            with open(CSV_FILE_PATH, mode="r", newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if (row.get("video_id") == video_id_or_url or 
                        row.get("url") == video_id_or_url or 
                        (video_id_or_url in row.get("url", ""))):
                        try:
                            transcript_data = json.loads(row.get("transcript_json", "[]"))
                        except Exception:
                            transcript_data = []

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
            print(f"[CSV Fallback Read Error] {e}")

    return None

def save_transcript(
    video_id: str,
    url: str,
    title: str,
    uploader: str,
    duration: int,
    thumbnail: str,
    transcript: List[Dict[str, Any]]
) -> bool:
    """
    새로 추출된 영상 정보와 transcript를 PostgreSQL 데이터베이스에 저장합니다.
    (안전을 위해 CSV 파일에도 백업 저장)
    """
    saved_to_db = False

    # 1. PostgreSQL 데이터베이스 저장
    if is_db_available():
        session = get_session()
        if session:
            try:
                # 이미 존재하는지 확인
                existing = session.scalars(
                    select(Transcript).where(Transcript.video_id == video_id)
                ).first()

                if existing:
                    existing.title = title
                    existing.uploader = uploader
                    existing.duration = duration
                    existing.thumbnail = thumbnail
                    existing.transcript = transcript
                else:
                    new_transcript = Transcript(
                        video_id=video_id,
                        url=url,
                        title=title,
                        uploader=uploader,
                        duration=duration,
                        thumbnail=thumbnail,
                        transcript=transcript
                    )
                    session.add(new_transcript)

                session.commit()
                print(f"[DB Saved] {video_id} successfully saved to PostgreSQL database.")
                saved_to_db = True
            except Exception as e:
                session.rollback()
                print(f"[DB Save Error] {e}")
            finally:
                session.close()

    # 2. 로컬 CSV 파일 백업 저장
    save_to_csv_backup(video_id, url, title, uploader, duration, thumbnail, transcript)

    return saved_to_db

def save_to_csv_backup(
    video_id: str,
    url: str,
    title: str,
    uploader: str,
    duration: int,
    thumbnail: str,
    transcript: List[Dict[str, Any]]
):
    """CSV 파일에 백업 보관"""
    try:
        init_csv_backup()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = {
            "video_id": video_id,
            "url": url,
            "title": title,
            "uploader": uploader,
            "duration": duration,
            "thumbnail": thumbnail or "",
            "transcript_json": json.dumps(transcript, ensure_ascii=False),
            "created_at": now_str
        }
        with open(CSV_FILE_PATH, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            writer.writerow(new_row)
    except Exception as e:
        print(f"[CSV Backup Save Error] {e}")

def migrate_csv_to_db():
    """기존 transcripts.csv에 있는 레코드를 PostgreSQL로 자동 마이그레이션"""
    if not os.path.exists(CSV_FILE_PATH) or not is_db_available():
        return

    session = get_session()
    if not session:
        return

    try:
        migrated_count = 0
        with open(CSV_FILE_PATH, mode="r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                vid = row.get("video_id")
                if not vid:
                    continue

                # 이미 DB에 있는지 확인
                existing = session.scalars(
                    select(Transcript).where(Transcript.video_id == vid)
                ).first()

                if not existing:
                    try:
                        transcript_data = json.loads(row.get("transcript_json", "[]"))
                    except Exception:
                        transcript_data = []

                    if transcript_data:
                        item = Transcript(
                            video_id=vid,
                            url=row.get("url", ""),
                            title=row.get("title", ""),
                            uploader=row.get("uploader", ""),
                            duration=int(row.get("duration") or 0),
                            thumbnail=row.get("thumbnail", ""),
                            transcript=transcript_data
                        )
                        session.add(item)
                        migrated_count += 1

        if migrated_count > 0:
            session.commit()
            print(f"[DB Migration] Migrated {migrated_count} records from transcripts.csv to PostgreSQL!")
    except Exception as e:
        session.rollback()
        print(f"[DB Migration Error] {e}")
    finally:
        session.close()

# 호환성 alias
init_csv_storage = init_storage
save_transcript_to_csv = save_transcript
