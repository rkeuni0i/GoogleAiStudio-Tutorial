<div align="center">

# 🚀 Google AI Studio & Gemini API Tutorials

### Google GenAI SDK를 활용한 멀티모달 AI(TTS, STT, 영상 분석 및 Q&A) 실습 및 웹 서비스 모음

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google GenAI SDK](https://img.shields.io/badge/Google%20GenAI-SDK%202.0+-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Gemini](https://img.shields.io/badge/Gemini-3.1%20%7C%203.5%20%7C%203.6%20%7C%203.8-FF6F00?style=for-the-badge&logo=google-cloud&logoColor=white)](https://aistudio.google.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

<p align="center">
  <a href="#-저장소-소개-overview">소개</a> •
  <a href="#-프로젝트-구성-project-structure">프로젝트 구성</a> •
  <a href="#-사전-요구사항--환경-설정">환경 설정</a> •
  <a href="#-하위-프로젝트-상세-소개">프로젝트 상세</a> •
  <a href="#-기술-스택-tech-stack">기술 스택</a>
</p>

</div>

---

## 📖 저장소 소개 (Overview)

본 저장소는 **Google AI Studio** 및 최신 **Google GenAI SDK (`google-genai`)**를 활용하여 음성 합성(Text-to-Speech), 음성 인식(Speech-to-Text), 유튜브 오디오 처리 및 영상 타임라인 스마트 질의응답을 구현한 튜토리얼 및 풀스택 웹 애플리케이션 모음입니다.

기초적인 단일 스크립트 예제부터 데이터베이스 연동과 스트리밍(SSE), 자동 점프 재생 기능을 갖춘 프로덕션 지향 웹 서비스까지 단계별로 구성되어 있습니다.

---

## 📂 프로젝트 구성 (Project Structure)

```text
GoogleAiStudio-Tutorial/
├── 🎬 ai-youtube-searcher/     # [Full-Stack] 타임라인 자막 추출 & 스마트 질의응답 및 자동 점프 재생 웹 서비스
│   ├── backend/                # FastAPI 백엔드, DB 모델(SQLite/PostgreSQL), Gemini 파이프라인
│   ├── frontend/               # 미니멀 다크 모드 UI, YouTube IFrame 연동
│   └── README.md
├── 🗣️ gemini-31-tts/           # [Script] Gemini 3.1 Flash 기반 오디오 스타일 지정 TTS 예제
│   ├── gemini-31-tts.py        # PCM 스트림 수집 및 RIFF/WAV 헤더 생성 코드
│   └── README.md
├── 🎙️ gemini-35-stt/           # [Script] Gemini 3.5 Transcribe 기반 스트리밍 STT 예제
│   ├── gemini-35-stt-example.py# 로컬 오디오 실시간 음성 전사 코드
│   ├── gemini_news_audio.wav   # 테스트 오디오 파일
│   └── README.md
├── 🌐 youtube-stt-service/     # [Web App] 유튜브 오디오 다운로드 & 실시간 STT 웹 서비스
│   ├── app.py                  # FastAPI 웹 서버 및 SSE 스트리밍 엔드포인트
│   ├── downloader.py           # yt-dlp 기반 오디오 스트림 추출기
│   ├── transcriber.py          # Gemini STT 처리기
│   ├── static/                 # 웹 프론트엔드 HTML/JS
│   └── README.md
└── 📄 README.md                # 전체 프로젝트 메인 안내 문서 (현재 파일)
```

---

## ⚙️ 사전 요구사항 & 환경 설정

### 1. API 키 발급
Google GenAI 모델을 이용하려면 [Google AI Studio](https://aistudio.google.com/)에서 API 키를 발급받아야 합니다.

### 2. 환경 변수 등록
발급받은 키를 시스템 환경 변수에 등록합니다:

- **Windows PowerShell**:
  ```powershell
  $env:GEMINI_API_KEY="your-gemini-api-key-here"
  ```
- **Linux / macOS**:
  ```bash
  export GEMINI_API_KEY="your-gemini-api-key-here"
  ```

> 각 웹 애플리케이션 프로젝트 디렉토리 내에 `.env` 파일을 생성하여 `GEMINI_API_KEY=your-key` 형식으로 저장할 수도 있습니다.

---

## 🔍 하위 프로젝트 상세 소개

### 1. 🎬 [ai-youtube-searcher](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/ai-youtube-searcher/README.md)
**유튜브 타임라인 자막 추출 & Gemini 3.8 Flash 기반 스마트 질의응답 서비스**

- **주요 기능**:
  - `yt-dlp` 기반 ffmpeg 무설치 무손실 오디오 스트림 추출
  - `Gemini 3.5 Transcribe` / `Gemini 3.6 Flash`를 통한 초 단위 타임스탬프(`start_time`, `seconds`, `text`) 구조화 자막 생성
  - `Gemini 3.8 Flash` 기반 컨텍스트 Q&A 및 관련 영상 시점(`target_seconds`) 자동 도출
  - 타임스탬프 클릭 및 AI 답변 클릭 시 유튜브 영상 해당 위치로 **자동 이동(`seekTo`) 및 즉시 재생**
  - SQLite(`transcripts.db`) 및 PostgreSQL(JSONB) 하이브리드 캐싱 지원
- **실행 방법**:
  ```bash
  cd ai-youtube-searcher
  pip install -r backend/requirements.txt
  python backend/main.py
  # 브라우저에서 http://localhost:8000 접속
  ```
- 자세한 내용은 [ai-youtube-searcher/README.md](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/ai-youtube-searcher/README.md)를 참고하세요.

---

### 2. 🗣️ [gemini-31-tts](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/gemini-31-tts/README.md)
**Gemini 3.1 Flash Text-to-Speech (TTS) 코드 분석 및 실습**

- **주요 기능**:
  - 텍스트 대본과 함께 오디오 스타일 프로필(감정, 억양, 배경 분위기 등)을 프롬프트로 부여하여 오디오 합성
  - API 스트리밍 청크(PCM/L16) 수집 및 표준 RIFF/WAVE 44바이트 바이너리 헤더를 Python `struct` 모듈로 직접 생성하여 `.wav`로 저장
- **코드 파일**: [`gemini-31-tts.py`](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/gemini-31-tts/gemini-31-tts.py)
- **실행 방법**:
  ```bash
  cd gemini-31-tts
  pip install google-genai
  python gemini-31-tts.py
  ```
- 라인별 코드 상세 분석은 [gemini-31-tts/README.md](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/gemini-31-tts/README.md)를 참고하세요.

---

### 3. 🎙️ [gemini-35-stt](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/gemini-35-stt/README.md)
**Gemini 3.5 Transcribe Speech-to-Text (STT) 음성 전사 실습**

- **주요 기능**:
  - `gemini-3.5-transcribe` 전용 음성 인식 모델을 활용한 로컬 오디오 파일 실시간 텍스트 변환
  - 스트리밍 응답(`generate_content_stream`) 처리를 통한 실시간 콘솔 텍스트 출력
- **코드 파일**: [`gemini-35-stt-example.py`](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/gemini-35-stt/gemini-35-stt-example.py)
- **실행 방법**:
  ```bash
  cd gemini-35-stt
  pip install google-genai
  python gemini-35-stt-example.py
  ```
- 라인별 코드 상세 분석은 [gemini-35-stt/README.md](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/gemini-35-stt/README.md)를 참고하세요.

---

### 4. 🌐 [youtube-stt-service](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/youtube-stt-service/README.md)
**경량 유튜브 오디오 추출 & 실시간 STT 웹 애플리케이션**

- **주요 기능**:
  - 유튜브 URL 입력 시 실시간 오디오 스트림 다운로드 및 SSE(Server-Sent Events) 진행률 표시
  - Gemini AI 기반 실시간 스트리밍 음성 전사
  - 웹 브라우저 내 인라인 오디오 플레이어 청취, 텍스트 클립보드 복사 및 `.txt` 다운로드 기능 제공
- **핵심 모듈**:
  - [`app.py`](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/youtube-stt-service/app.py): FastAPI 웹 서버
  - [`downloader.py`](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/youtube-stt-service/downloader.py): 오디오 다운로더
  - [`transcriber.py`](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/youtube-stt-service/transcriber.py): STT 전사기
- **실행 방법**:
  ```bash
  cd youtube-stt-service
  pip install -r requirements.txt
  python app.py
  # 브라우저에서 http://localhost:8000 접속
  ```
- 자세한 내용은 [youtube-stt-service/README.md](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/youtube-stt-service/README.md)를 참고하세요.

---

## 🛠️ 기술 스택 (Tech Stack)

| 분류 | 세부 기술 |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **AI Models & SDK** | Google GenAI SDK (`google-genai`), Gemini 3.8 Flash, Gemini 3.6 Flash, Gemini 3.5 Transcribe, Gemini 3.1 Flash TTS |
| **Web Framework** | FastAPI, Uvicorn, SSE (Server-Sent Events) |
| **Database & ORM** | SQLite, PostgreSQL, SQLAlchemy 2.0 |
| **Frontend** | HTML5, Tailwind CSS, Vanilla JavaScript, YouTube IFrame Player API |
| **Media Processing** | `yt-dlp` (무손실 오디오 추출), Python `struct` (바이너리 WAV 인코딩) |

---

## 📜 라이선스 (License)

이 튜토리얼 프로젝트는 [MIT License](LICENSE)를 따릅니다.
