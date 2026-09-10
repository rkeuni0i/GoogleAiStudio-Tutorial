# YouTube Audio Transcriber (YouTube STT 서비스)

유튜브 영상 URL을 입력하면 영상의 오디오 스트림을 다운로드하고, Google Gemini AI를 통해 음성을 실시간 텍스트로 변환(STT)해주는 웹 서비스입니다.

---

## 주요 기능

1. **유튜브 오디오 직접 추출**: `yt-dlp`를 활용하여 ffmpeg 없이도 무손실 오디오 스트림(m4a/webm)을 고속으로 다운로드
2. **Gemini 음성 인식 (STT)**: `gemini-3.6-flash` 및 `gemini-3.5-transcribe` 모델을 활용한 고정밀 다국어 음성 전사
3. **실시간 스트리밍 (SSE)**: 다운로드 진행률 및 생성되는 텍스트를 실시간 타이핑 효과로 브라우저에 표시
4. **인라인 오디오 플레이어**: 다운로드된 오디오를 브라우저에서 바로 청취 가능
5. **텍스트 복사 & .txt 내보내기**: 추출된 대본을 한 번의 클릭으로 클립보드에 복사하거나 텍스트 파일로 저장

---

## 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. Gemini API 키 설정
환경 변수에 `GEMINI_API_KEY`를 설정합니다.

- **Windows PowerShell**:
  ```powershell
  $env:GEMINI_API_KEY="your-api-key-here"
  ```
- **Linux / macOS**:
  ```bash
  export GEMINI_API_KEY="your-api-key-here"
  ```

또는 `youtube-stt-service` 폴더 내에 `.env` 파일을 생성하고 다음과 같이 입력할 수도 있습니다:
```env
GEMINI_API_KEY=your-api-key-here
```

### 3. 웹 서버 구동
`youtube-stt-service` 디렉토리로 이동하여 다음 명령어로 서버를 구동합니다:

```bash
cd youtube-stt-service
python app.py
```
또는
```bash
python -m uvicorn app:app --port 8000 --reload
```

### 4. 웹 브라우저 접속
웹 브라우저를 열고 다음 주소로 접속합니다:
👉 **http://localhost:8000**
