<div align="center">

# 🎬 AI YouTube Searcher
### Gemini AI 기반 유튜브 타임라인 자막 추출 & 스마트 질의응답 웹 서비스

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Default%20Embedded-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported%20(JSONB)-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Google GenAI](https://img.shields.io/badge/Google%20GenAI-SDK%202.0+-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Gemini](https://img.shields.io/badge/Gemini-3.8%20Flash%20%7C%203.6%20Flash-FF6F00?style=for-the-badge&logo=google-cloud&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <a href="#-주요-기능-key-features">주요 기능</a> •
  <a href="#-시스템-아키텍처-system-architecture">시스템 아키텍처</a> •
  <a href="#-빠른-시작-quickstart">빠른 시작</a> •
  <a href="#-antigravity-ide에서-데이터베이스-테이블-보는-방법">DB 테이블 뷰어 가이드</a> •
  <a href="#-디렉토리-구조-directory-structure">디렉토리 구조</a> •
  <a href="#-api-명세-api-specification">API 명세</a>
</p>

[ English | **한국어** | 简体中文 | 日本語 ]

---

<p align="center">
  <img src="https://img.shields.io/badge/Storage-SQLite%20%7C%20PostgreSQL-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/YouTube%20IFrame%20API-FF0000?style=flat-square&logo=youtube&logoColor=white" />
  <img src="https://img.shields.io/badge/yt--dlp-FF4154?style=flat-square&logo=youtube&logoColor=white" />
  <img src="https://img.shields.io/badge/TailwindCSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/React%20Components-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square" />
</p>

</div>

> **AI YouTube Searcher**는 긴 유튜브 영상을 처음부터 끝까지 시청하지 않고도 핵심 내용을 신속하게 탐색하고, **Google Gemini 3.8 Flash**와의 대화를 통해 원하는 내용이 나오는 정확한 영상 위치로 즉시 이동하여 자동 재생할 수 있는 고성능 멀티모달 웹 플랫폼입니다.

---

## 🌟 주요 기능 (Key Features)

| 기능 | 설명 | 기술 스택 / 모델 |
| :--- | :--- | :--- |
| **🎨 집중도 높은 UI** | 유튜브 상단의 마이크, 만들기(+), 알림 등 불필요한 요소를 전면 배제한 미니멀 다크 모드 검색창 | Tailwind CSS, Lucide Icons |
| **⚡ 무손실 오디오 추출** | 시스템 `ffmpeg` 설치 없이도 `yt-dlp`를 통해 고속 무손실 오디오 스트림(`m4a`, `webm`) 직접 다운로드 | `yt-dlp` |
| **🎙️ 고정밀 타임스탬프 STT** | 음성을 분석하여 구간별 타임스탬프(`start_time`, `seconds`, `text`) 구조화 자막 추출 | `Gemini 3.5 Transcribe` / `Gemini 3.6 Flash` |
| **🤖 Context 기반 AI Q&A** | 전체 자막을 컨텍스트로 학습하여 질문에 답변하고, 관련 영상 시점(`target_seconds`) 도출 | `Gemini 3.8 Flash` |
| **🎯 스마트 자동 점프 재생** | 타임스탬프 자막 클릭 또는 AI 답변 시 **해당 시점으로 영상을 자동 이동(`seekTo`) 및 즉시 재생** | YouTube IFrame Player API |
| **🔊 커스텀 볼륨 컨트롤** | 플레이어 자체 음향 외에 웹 UI 슬라이더를 통한 정밀한 볼륨 조절 지원 | `player.setVolume(val)` |
| **🗄️ 하이브리드 DB 영구 캐싱** | 기본 **SQLite(`transcripts.db`)**로 설치 없이 즉시 구동되며, 설정 시 **PostgreSQL(JSONB)**로 즉시 전환 지원 | `SQLAlchemy 2.0`, `SQLite`, `PostgreSQL` |

---

## 🏗️ 시스템 아키텍처 (System Architecture)

```mermaid
flowchart TB
    subgraph Client ["🖥️ Web Client (Frontend)"]
        UI["YouTube 스타일 Header\n(URL Search Bar)"]
        Player["YouTube IFrame Player\n(Video & Custom Volume)"]
        TranscriptUI["타임라인 자막 패널\n(Transcript List)"]
        ChatUI["Gemini 3.8 Flash Q&A 패널\n(AI Chat)"]
    end

    subgraph Backend ["⚙️ FastAPI Server Engine"]
        Router["FastAPI Application (main.py)"]
        Storage["스토리지 매니저 (transcript_storage.py)"]
        ORM["SQLAlchemy 2.0 ORM (database.py)"]
        Extractor["오디오 추출기 (audio_extractor.py)"]
        DB[("🗄️ Database (transcripts 테이블)\n[기본: SQLite / 선택: PostgreSQL]")]
        CSV[("💾 transcripts.csv\n(로컬 백업 캐시)")]
    end

    subgraph Gemini ["🧠 Google Gemini AI Services"]
        STT["Gemini 3.5 Transcribe / 3.6 Flash\n(Audio -> Timestamps & Subtitles)"]
        QA["Gemini 3.8 Flash\n(Context Q&A & Target Seek Seconds)"]
    end

    %% Flow
    UI -->|1. YouTube URL 입력| Router
    Router -->|2. 캐시 조회| Storage
    Storage <-->|ORM 쿼리| ORM
    ORM <-->|고속 조회| DB
    Storage -.->|Fallback 조회| CSV
    
    Storage -- 캐시 미스 시 --> Extractor
    Extractor -->|3. Audio Stream 다운로드| Router
    Router -->|4. 음성 전달| STT
    STT -->|5. 타임스탬프 자막 JSON 반환| Router
    Router -->|6. 데이터베이스 영구 저장| Storage
    Router -->|7. 영상 정보 & 자막 전달| Player & TranscriptUI

    ChatUI -->|8. 질문 입력| Router
    Router -->|9. 자막 전문 + 질문 전달| QA
    QA -->|10. 답변 + 정밀 타임스탬프(초)| Router
    Router -->|11. 답변 응답| ChatUI
    ChatUI -.->|12. 자동 타임라인 이동 & 재생| Player
    TranscriptUI -.->|타임스탬프 클릭 이동| Player
```

---

## 🚀 빠른 시작 (Quickstart)

<details open>
<summary><b>1. 환경 준비 및 디렉토리 이동</b></summary>

```powershell
# Anaconda 가상환경 활성화 (myenv)
conda activate myenv

# 프로젝트 백엔드 디렉토리로 이동
cd ai-youtube-searcher/backend
```

</details>

<details open>
<summary><b>2. 의존성 패키지 설치</b></summary>

```powershell
pip install -r requirements.txt
```

> **주요 의존 패키지:**
> - `google-genai >= 2.0.0`
> - `fastapi >= 0.115.0`
> - `uvicorn >= 0.30.0`
> - `sqlalchemy >= 2.0.0`
> - `psycopg2-binary >= 2.9.9`
> - `yt-dlp >= 2024.0.0`
> - `python-dotenv >= 1.0.0`

</details>

<details open>
<summary><b>3. 환경 변수 설정 (`.env`)</b></summary>

`ai-youtube-searcher/backend/.env` 파일에서 API 키와 데이터베이스를 설정합니다:

```env
# Google Gemini API Key
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere...

# Database Connection URL (기본값: 로컬 SQLite 파일 모드 - 별도 설치/비번 불필요!)
DATABASE_URL=sqlite:///transcripts.db

# (선택 사항) 대규모 배포용 PostgreSQL 연결 시:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/youtube_searcher
```

> **💡 데이터베이스 자동 구성 및 마이그레이션 안내:**
> - 기본 상태에서는 포트나 비밀번호 없이 즉시 동작하는 **`transcripts.db` (SQLite)** 파일이 자동 생성됩니다.
> - 서버 시작 시 기존 `transcripts.csv` 파일의 데이터가 데이터베이스로 **자동 마이그레이션**됩니다.

</details>

<details open>
<summary><b>4. 서버 실행</b></summary>

```powershell
python main.py
```

서버가 구동되면 웹 브라우저를 열고 아래 주소로 접속합니다:  
👉 **[http://localhost:8001](http://localhost:8001)**

</details>

---

## 📊 Antigravity IDE에서 데이터베이스 테이블 보는 방법

Antigravity IDE 내부에서 저장된 영상과 자막 데이터를 **엑셀(Excel) 스프레드시트 형태**로 확인하실 수 있습니다.

```mermaid
graph LR
    A["Antigravity IDE\n좌측 DB 아이콘"] --> B["Create Connection\n(SQLite 선택)"]
    B --> C["Database Path\n(transcripts.db 파일 선택)"]
    C --> D["transcripts 테이블 더블 클릭\n(엑셀 표로 열람)"]
```

1. **확장 설치**:
   - 좌측 사이드바 마켓플레이스(`Ctrl + Shift + X`)에서 **`Database Client`** (개발자: *cweijan*)를 설치합니다.
2. **새 연결 생성**:
   - 좌측에 추가된 **데이터베이스(원통 모양) 아이콘** 클릭 ➜ 상단 **`+` (Create Connection)** 클릭
3. **SQLite 연결**:
   - DB 종류에서 **`SQLite`** 선택 (비밀번호/포트 입력 필요 없음!)
   - **`Database Path`**에 [`ai-youtube-searcher/backend/transcripts.db`](file:///c:/Users/2003g/Documents/Project_sesac/GoogleAiStudio-Tutorial/ai-youtube-searcher/backend/transcripts.db) 파일 선택 후 **[Save]** 클릭
4. **테이블 조회**:
   - 좌측 트리에서 `transcripts.db` ➜ `main` ➜ **`transcripts` 테이블을 더블 클릭**하면 중앙 화면에 정렬 및 필터가 가능한 **스프레드시트 표**가 바로 열립니다.

---

## 📁 디렉토리 구조 (Directory Structure)

```text
ai-youtube-searcher/
├── backend/                             # 🐍 FastAPI 백엔드 서버
│   ├── main.py                          # API 라우트 및 앱 시작 시 DB 자동 초기화/마이그레이션
│   ├── .env                             # API 키 및 DATABASE_URL 환경 설정
│   ├── .env.example                     # 환경 설정 템플릿 파일
│   ├── transcripts.db                   # 🗄️ SQLite 데이터베이스 파일 (테이블 뷰어 연동)
│   ├── transcripts.csv                  # 💾 URL 및 전사 자막 로컬 백업 파일
│   ├── requirements.txt                 # 백엔드 의존 패키지 목록 (SQLAlchemy, psycopg2 포함)
│   ├── downloads/                       # 다운로드된 오디오 스트림 캐시
│   └── services/
│       ├── __init__.py
│       ├── database.py                  # 🗄️ SQLAlchemy 2.0 ORM 모델 & 세션 (SQLite/Postgres 지원)
│       ├── transcript_storage.py        # 🔄 DB 영구 저장/조회 및 CSV 자동 마이그레이션 엔진
│       ├── audio_extractor.py           # yt-dlp 기반 오디오 스트림 추출 & 메타데이터
│       ├── gemini_stt.py                # Gemini 타임스탬프 음성 전사 (Fallback 포함)
│       └── gemini_qa.py                 # Gemini 3.8 Flash 자막 기반 질의응답
│
├── frontend/                            # ⚛️ 프론트엔드 웹 애플리케이션
│   ├── index.html                       # 유튜브 다크 테마 SPA (마이크/만들기/알림 제거)
│   ├── package.json                     # 프론트엔드 패키지 명세
│   ├── css/
│   │   └── style.css                    # 커스텀 슬라이더, 스크롤바, 플레이어 스타일
│   ├── js/
│   │   ├── player.js                    # YouTube IFrame API 컨트롤러 (seekTo, volume)
│   │   └── app.js                       # 검색, 탭 전환, 실시간 렌더링, Q&A 연동
│   └── src/                             # 🧩 React 컴포넌트 라이브러리
│       ├── App.jsx                      # 메인 통합 React 애플리케이션
│       └── components/
│           ├── Header.jsx               # 미니멀 상단 검색 헤더
│           ├── VideoPlayer.jsx          # 비디오 플레이어 & 볼륨 컨트롤러
│           ├── Transcript.jsx           # 시간대별 타임스탬프 자막 리스트
│           └── ChatQA.jsx               # Gemini 3.8 Flash 질의응답 채팅창
│
└── README.md                            # 프로젝트 공식 안내 문서
```

---

## 🔌 API 명세 (API Specification)

### 1. 영상 자막 처리 및 분석 API
- **Endpoint**: `POST /api/process-video`
- **Description**: 입력된 URL에 대해 DB 캐시를 우선 조회하고, 없을 경우 오디오를 다운로드하여 Gemini STT 타임스탬프 자막을 추출한 뒤 DB에 영구 저장합니다.

```json
// Request
{
  "url": "https://www.youtube.com/watch?v=Eba93Qw6_CM"
}

// Response (200 OK)
{
  "video_id": "Eba93Qw6_CM",
  "url": "https://www.youtube.com/watch?v=Eba93Qw6_CM",
  "title": "[루카] 30초 예고편",
  "uploader": "Disney Korea",
  "duration": 30,
  "thumbnail": "https://i.ytimg.com/vi/Eba93Qw6_CM/maxresdefault.jpg",
  "transcript": [
    {
      "start_time": "00:00",
      "seconds": 0,
      "text": "Come on, Luca."
    },
    {
      "start_time": "00:05",
      "seconds": 5,
      "text": "What are we doing?"
    }
  ]
}
```

### 2. Gemini 3.8 Flash 기반 질의응답 API
- **Endpoint**: `POST /api/qa`
- **Description**: 영상의 자막 전문과 사용자의 질문을 분석하여 맥락에 맞는 답변과 해당 영상 재생 시점(`target_seconds`)을 반환합니다.

```json
// Request
{
  "video_id": "Eba93Qw6_CM",
  "question": "루카가 자전거를 타는 장면은 언제 나와?"
}

// Response (200 OK)
{
  "answer": "루카가 친구와 함께 자전거를 타고 달리는 장면은 00:15 구간에 등장합니다.",
  "target_seconds": 15
}
```

---

<div align="center">

### 💡 AI 모델 파이프라인 흐름도

```
[YouTube Video URL]
        │
        ▼ (yt-dlp)
[Audio Stream (.m4a/.webm)] ────▶ [Google Gemini 3.5 Transcribe / 3.6 Flash]
                                                 │
                                                 ▼ (JSON Extraction)
                                  [Timestamped Transcripts]
                                                 │
                                  ┌──────────────┴──────────────┐
                                  ▼                             ▼
                    [🗄️ transcripts.db / PG]    [Gemini 3.8 Flash Context Q&A]
                                                                │
                                                                ▼
                                                [Answer + Seek Seconds (seekTo)]
```

Made with ❤️ by Advanced Agentic Pair Programming

</div>
