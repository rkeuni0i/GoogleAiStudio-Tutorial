import os
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from services.audio_extractor import extract_audio, get_video_metadata, extract_video_id
from services.gemini_stt import transcribe_with_timestamps
from services.gemini_qa import answer_question_with_transcript
from services.transcript_storage import get_saved_transcript, save_transcript_to_csv, init_csv_storage

# 상위 폴더 또는 현재 폴더의 .env 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv() # 시스템 기본

app = FastAPI(title="AI YouTube Searcher API", version="1.1.0")

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 인메모리 자막 캐시
TRANSCRIPT_CACHE: Dict[str, Dict[str, Any]] = {}

class VideoProcessRequest(BaseModel):
    url: str

class QARequest(BaseModel):
    video_id: str
    question: str
    video_title: Optional[str] = ""
    transcript: Optional[List[Dict[str, Any]]] = None

@app.post("/api/process-video")
async def process_video(req: VideoProcessRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="유튜브 URL을 입력해주세요.")

    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="유효한 유튜브 영상 URL이 아닙니다.")

    # 1. 인메모리 캐시 확인
    cached = TRANSCRIPT_CACHE.get(video_id)
    if cached and cached.get("transcript") and len(cached["transcript"]) > 0:
        if not ("오류" in cached["transcript"][0].get("text", "")):
            print(f"[Memory Cache Hit] {video_id}")
            return cached

    # 2. 영구 CSV 파일에서 저장된 transcript가 있는지 확인
    saved_csv_data = get_saved_transcript(video_id)
    if saved_csv_data and saved_csv_data.get("transcript") and len(saved_csv_data["transcript"]) > 0:
        print(f"[CSV Cache Hit] {video_id} - 오디오 다운로드 및 Gemini 전사를 건너뛰고 저장된 CSV 데이터를 반환합니다.")
        TRANSCRIPT_CACHE[video_id] = saved_csv_data
        return saved_csv_data

    try:
        # 3. CSV에 저장된 내용이 없을 때만 오디오 다운로드 및 메타데이터 추출
        print(f"[New Video] {video_id} - 저장된 내용이 없어 새로 오디오 추출 및 Gemini 분석을 시작합니다.")
        filepath, mime_type, metadata = extract_audio(url)

        # 4. Gemini STT를 통한 타임스탬프 자막 추출
        transcript = transcribe_with_timestamps(filepath, mime_type)

        result = {
            "video_id": metadata["video_id"],
            "url": url,
            "title": metadata["title"],
            "uploader": metadata["uploader"],
            "duration": metadata["duration"],
            "thumbnail": metadata["thumbnail"],
            "transcript": transcript
        }

        # 5. CSV 파일에 새로 추출된 결과 저장 (최초 1회 영구 저장)
        if transcript and len(transcript) > 0 and not ("오류" in transcript[0].get("text", "")):
            save_transcript_to_csv(
                video_id=metadata["video_id"],
                url=url,
                title=metadata["title"],
                uploader=metadata["uploader"],
                duration=metadata["duration"],
                thumbnail=metadata["thumbnail"],
                transcript=transcript
            )

        # 6. 인메모리 캐시 저장 및 반환
        TRANSCRIPT_CACHE[video_id] = result
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"영상 처리 중 오류 발생: {str(e)}")

@app.post("/api/qa")
async def ask_question(req: QARequest):
    transcript = req.transcript
    if not transcript and req.video_id in TRANSCRIPT_CACHE:
        transcript = TRANSCRIPT_CACHE[req.video_id].get("transcript", [])

    if not transcript:
        raise HTTPException(status_code=400, detail="자막 정보가 존재하지 않습니다. 먼저 영상을 분석해주세요.")

    try:
        qa_result = answer_question_with_transcript(
            question=req.question,
            transcript=transcript,
            video_title=req.video_title or ""
        )
        return qa_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 질의응답 처리 중 오류 발생: {str(e)}")

# 프론트엔드 정적 파일 서빙
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI YouTube Searcher API is running. Frontend not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
