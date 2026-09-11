import os
from datetime import datetime
from typing import Optional, Any
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Text,
    DateTime,
    func
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    Session
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

# 환경 변수 로드
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv()

# 기본값을 로컬 SQLite 파일 (transcripts.db)로 설정 (비밀번호/포트 불필요!)
SQLITE_DB_PATH = os.path.join(BASE_DIR, "transcripts.db").replace(os.sep, "/")
DEFAULT_DB_URL = f"sqlite:///{SQLITE_DB_PATH}"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DB_URL)

# SQLAlchemy 2.0 Base
class Base(DeclarativeBase):
    pass

# PostgreSQL에서는 JSONB, 기타 DB에서는 범용 JSON으로 자동 적응
JsonAdaptiveType = JSON().with_variant(JSONB, "postgresql")

class Transcript(Base):
    """YouTube 영상 전사 자막 및 메타데이터 모델"""
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    uploader: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    thumbnail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 시간대별 타임스탬프 자막 배열 ([{start_time, seconds, text}])
    transcript: Mapped[Any] = mapped_column(JsonAdaptiveType, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "url": self.url,
            "title": self.title,
            "uploader": self.uploader,
            "duration": self.duration,
            "thumbnail": self.thumbnail,
            "transcript": self.transcript,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }

# Engine & Session 관리
_engine = None
_SessionLocal = None
_is_db_connected = False

def get_engine():
    global _engine
    if _engine is None:
        try:
            if DATABASE_URL.startswith("sqlite"):
                _engine = create_engine(
                    DATABASE_URL,
                    connect_args={"check_same_thread": False}
                )
            else:
                _engine = create_engine(
                    DATABASE_URL,
                    pool_pre_ping=True,
                    pool_size=10,
                    max_overflow=20
                )
        except Exception as e:
            print(f"[DB Engine Error] {e}")
            return None
    return _engine

def get_session() -> Optional[Session]:
    global _SessionLocal
    engine = get_engine()
    if engine is None:
        return None
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal()

def init_db() -> bool:
    """데이터베이스 연결 확인 및 transcripts 테이블 생성"""
    global _is_db_connected
    engine = get_engine()
    if engine is None:
        _is_db_connected = False
        return False

    try:
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        _is_db_connected = True
        db_type = "SQLite" if DATABASE_URL.startswith("sqlite") else "PostgreSQL"
        db_target = SQLITE_DB_PATH if DATABASE_URL.startswith("sqlite") else (DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL)
        print(f"[DB] {db_type} database initialized successfully! ({db_target})")
        return True
    except Exception as e:
        _is_db_connected = False
        print(f"[DB Warning] Could not connect to database: {e}")
        return False

def is_db_available() -> bool:
    return _is_db_connected
