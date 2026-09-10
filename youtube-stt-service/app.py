import os
import json
import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from downloader import download_audio, get_video_info, DOWNLOAD_DIR
from transcriber import transcribe_audio_stream

# .env 파일이 있으면 로드
load_dotenv()

app = FastAPI(title="YouTube Audio Transcriber", version="1.0.0")

# CORS 활성화
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 다운로드된 오디오 서빙
app.mount("/downloads", StaticFiles(directory=DOWNLOAD_DIR), name="downloads")

# 정적 웹 파일 서빙 경로
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class InfoRequest(BaseModel):
    url: str

class TranscribeRequest(BaseModel):
    url: str
    model_name: str = "gemini-3.6-flash"

@app.get("/")
def read_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "YouTube STT Web Service Running. Please open /static/index.html"}

@app.post("/api/info")
def api_get_info(req: InfoRequest):
    try:
        info = get_video_info(req.url)
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/transcribe-stream")
async def api_transcribe_stream(
    url: str = Query(..., description="유튜브 영상 URL"),
    model_name: str = Query("gemini-3.6-flash", description="Gemini 모델명")
):
    """
    Server-Sent Events(SSE)를 통해 다운로드 진행률 및 전사 텍스트를 실시간 스트리밍합니다.
    """
    async def event_generator():
        try:
            # 1. 상태 알림
            yield f"event: status\ndata: {json.dumps({'message': '1/3 유튜브 영상 정보를 분석하고 있습니다...'})}\n\n"
            await asyncio.sleep(0.1)

            # 2. 오디오 다운로드 (블로킹 작업을 스레드풀에서 실행)
            loop = asyncio.get_event_loop()
            filepath, mime_type, info = await loop.run_in_executor(None, download_audio, url)
            
            audio_filename = os.path.basename(filepath)
            audio_url = f"/downloads/{audio_filename}"

            yield f"event: info\ndata: {json.dumps(info)}\n\n"
            yield f"event: audio_ready\ndata: {json.dumps({'audio_url': audio_url, 'filename': audio_filename})}\n\n"
            
            # 3. Gemini 음성 전사
            yield f"event: status\ndata: {json.dumps({'message': f'2/3 Gemini 모델({model_name})로 음성을 텍스트로 변환 중입니다...'})}\n\n"
            
            # 동기 제너레이터를 비동기 루프에서 순회
            def get_chunks():
                return list(transcribe_audio_stream(filepath, mime_type, model_name=model_name))
            
            # 실시간 chunk 스트리밍
            def run_stream():
                for chunk in transcribe_audio_stream(filepath, mime_type, model_name=model_name):
                    yield chunk

            # 스레드풀에서 실행하면서 yield
            for chunk in await loop.run_in_executor(None, get_chunks):
                yield f"event: chunk\ndata: {json.dumps({'text': chunk})}\n\n"
                await asyncio.sleep(0.01)

            yield f"event: status\ndata: {json.dumps({'message': '3/3 전사가 성공적으로 완료되었습니다!'})}\n\n"
            yield f"event: done\ndata: {json.dumps({'status': 'completed'})}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream; charset=utf-8",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
