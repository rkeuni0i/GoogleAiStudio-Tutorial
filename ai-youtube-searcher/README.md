<div align="center">

# 🎬 AI YouTube Searcher
### Gemini AI 기반 유튜브 타임라인 자막 추출 & 스마트 질의응답 웹 서비스

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B%20(JSONB)-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Google GenAI](https://img.shields.io/badge/Google%20GenAI-SDK%202.0+-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Gemini](https://img.shields.io/badge/Gemini-3.8%20Flash%20%7C%203.6%20Flash-FF6F00?style=for-the-badge&logo=google-cloud&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <a href="#-주요-기능-key-features">주요 기능</a> •
  <a href="#-시스템-아키텍처-system-architecture">시스템 아키텍처</a> •
  <a href="#-빠른-시작-quickstart">빠른 시작</a> •
  <a href="#-postgresql-데이터베이스-설정">PostgreSQL 설정</a> •
  <a href="#-디렉토리-구조-directory-structure">디렉토리 구조</a> •
  <a href="#-api-명세-api-specification">API 명세</a>
</p>

[ English | **한국어** | 简体中文 | 日本語 ]

---

<p align="center">
  <img src="https://img.shields.io/badge/PostgreSQL-JSONB%20Storage-336791?style=flat-square&logo=postgresql&logoColor=white" />
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
| **🐘 PostgreSQL (JSONB) 영구 저장** | 타임스탬프 자막을 PostgreSQL JSONB 컬럼에 인덱싱 저장하여 다중 사용자 동시성 및 초고속 캐시 지원 | `PostgreSQL`, `SQLAlchemy 2.0` |

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
        ORM["SQLAlchemy ORM (database.py)"]
        Extractor["오디오 추출기 (audio_extractor.py)"]
        PG[("🐘 PostgreSQL (transcripts 테이블)\n[JSONB 컬럼 & UNIQUE 인덱스]")]
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
    ORM <-->|고속 JSONB 조회| PG
    Storage -.->|Fallback 조회| CSV
    
    Storage -- 캐시 미스 시 --> Extractor
    Extractor -->|3. Audio Stream 다운로드| Router
    Router -->|4. 음성 전달| STT
    STT -->|5. 타임스탬프 자막 JSON 반환| Router
    Router -->|6. PostgreSQL 영구 저장| Storage
    Router -->|7. 영상 정보 & 자막 전달| Player & TranscriptUI

    ChatUI -->|8. 질문 입력| Router
    Router -->|9. 자막 전문 + 질문 전달| QA
    QA -->|10. 답변 + 정밀 타임스탬프(초)| Router
    Router -->|11. 답변 응답| ChatUI
    ChatUI -.->|12. 자동 타임라인 이동 & 재생| Player
    TranscriptUI -.->|타임스탬프 클릭 이동| Player
```

---

## 📁 디렉토리 구조 (Directory Structure)

```text
ai-youtube-searcher/
├── backend/                             # 🐍 FastAPI 백엔드 서버
│   ├── main.py                          # API 라우트 및 앱 시작 시 DB 초기화/마이그레이션
│   ├── .env.example                     # 데이터베이스 및 API 키 환경변수 템플릿
│   ├── transcripts.csv                  # 💾 URL 및 전사 자막 로컬 백업 파일
│   ├── requirements.txt                 # 백엔드 의존 패키지 목록 (SQLAlchemy, psycopg2 포함)
│   ├── downloads/                       # 다운로드된 오디오 스트림 캐시
│   └── services/
│       ├── __init__.py
│       ├── database.py                  # 🐘 SQLAlchemy ORM 모델 (JSONB) 및 세션 엔진
│       ├── transcript_storage.py        # 🔄 PostgreSQL 저장/조회 및 CSV 자동 마이그레이션
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
└── README.md                            # 프로젝트 안내 문서
```

---

## 🚀 빠른 시작 (Quickstart)

<details open>
<summary><b>1. 환경 준비 및 가상환경 활성화</b></summary>

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
> - `yt-dlp >= 2024.0.0`
> - `python-dotenv >= 1.0.0`

</details>

<details open>
<summary><b>3. 환경 변수 (Gemini API 키 & PostgreSQL DB URL) 설정</b></summary>

`ai-youtube-searcher/backend/.env` 파일 생성 또는 환경변수 설정:

```env
# Google Gemini API Key
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere...

# PostgreSQL 연결 URL (로컬 또는 클라우드 DB)
DATABASE_URL=postgresql://postgres:password@localhost:5432/youtube_searcher
```

> **💡 데이터베이스 자동 구성 및 마이그레이션 안내:**
> - 서버 시작 시 `transcripts` 테이블이 **자동 생성**됩니다.
> - 기존 `transcripts.csv` 파일이 있을 경우 자동으로 PostgreSQL 데이터베이스로 **일괄 마이그레이션**됩니다.
> - PostgreSQL 미설치/미기동 환경에서도 로컬 CSV 백업을 통해 시스템이 중단 없이 안전하게 작동합니다.

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

## 🐘 PostgreSQL 영구 저장 및 캐싱 시스템 (JSONB Storage)

분석된 영상과 자막은 PostgreSQL 데이터베이스의 `transcripts` 테이블에 영구 저장됩니다. 동일한 영상 URL 검색 시 **Gemini API 호출 비용과 오디오 다운로드 시간을 0으로 절감**하며 0.1초 만에 화면에 출력됩니다.

### 📋 테이블 스키마 (`transcripts`)
```sql
CREATE TABLE transcripts (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) UNIQUE NOT NULL,    -- 인덱스 적용 및 유일성 보장
    url VARCHAR(500) NOT NULL,
    title VARCHAR(500),
    uploader VARCHAR(255),
    duration INTEGER,
    thumbnail TEXT,
    transcript JSONB NOT NULL,               -- 타임스탬프 자막 배열 ([{start_time, seconds, text}])
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

- **JSONB 네이티브 타입**: PostgreSQL의 `JSONB`를 사용하여 파싱 오버헤드 없이 고속 인덱싱 및 쿼리 지원
- **동시성 제어**: `video_id` UNIQUE 제약으로 중복 저장 및 Race Condition 방지
- **자동 마이그레이션**: 서버 기동 시 기존 `transcripts.csv` 데이터를 PostgreSQL로 자동 적재

---

## 🌐 API 명세 (API Specification)

<details>
<summary><b>POST /api/process-video</b> - 유튜브 영상 분석 및 자막 추출</summary>

- **Request Body:**
  ```json
  {
    "url": "https://youtu.be/Eba93Qw6_CM"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "video_id": "Eba93Qw6_CM",
    "url": "https://youtu.be/Eba93Qw6_CM",
    "title": "[루카] '특별한 친구' 30초 예고편",
    "uploader": "디즈니 코리아",
    "duration": 30,
    "thumbnail": "https://i.ytimg.com/vi/Eba93Qw6_CM/maxresdefault.jpg",
    "transcript": [
      { "start_time": "00:00", "seconds": 0, "text": "Come on, Luca. Just follow my lead." },
      { "start_time": "00:05", "seconds": 5, "text": "That's not it, try it again." },
      { "start_time": "00:14", "seconds": 14, "text": "특별한 친구 바다괴물!" }
    ]
  }
  ```

</details>

<details>
<summary><b>POST /api/qa</b> - 자막 컨텍스트 기반 AI 질문 및 타임라인 탐색</summary>

- **Request Body:**
  ```json
  {
    "video_id": "Eba93Qw6_CM",
    "question": "바다괴물이 나오는 부분이 몇 초야?",
    "video_title": "[루카] 30초 예고편",
    "transcript": [...]
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "answer": "바다괴물에 대해 언급하는 장면은 [00:14] 구간입니다. '특별한 친구 바다괴물!'이라는 대사와 함께 등장합니다.",
    "target_seconds": 14,
    "timestamp_str": "00:14"
  }
  ```

</details>

---

## 🛠️ 모델 파이프라인 (AI Model Pipeline)

```text
[YouTube Audio]
       │
       ▼
[Gemini 3.5 Transcribe / 3.6 Flash] ──► { start_time, seconds, text } JSON 구조화 자막
       │
       ▼
[Gemini 3.8 Flash Context Engine]   ──► 질문 의도 분석 및 정밀 타임스탬프(초) 도출
       │
       ▼
[YouTube IFrame Player Controller]  ──► player.seekTo(target_seconds, true) & playVideo()
```

---

<div align="center">

### 🤝 Contributing & Support

버그 제보나 기능 제안은 이슈를 통해 남겨주세요.

**Made with ❤️ using Google Gemini & FastAPI**

</div>
