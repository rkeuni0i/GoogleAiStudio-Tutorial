# AI 유튜브 검색기 (AI YouTube Searcher)

유튜브 영상의 링크를 입력하면 Gemini AI 모델을 통해 영상의 음성을 분석하고, 타임스탬프 자막 추출 및 AI 질의응답을 제공하는 웹 서비스입니다. 
질문 답변 시 해당 내용이 나오는 시점으로 영상을 자동 이동(`seekTo`)하고 재생합니다.

---

## 📌 주요 특징 및 기능

1. **YouTube 스타일 헤더 UI**:
   - 상단 검색창에서 URL 입력 및 분석
   - 불필요한 마이크, 만들기(+), 알림 종 아이콘을 완전히 제거한 미니멀 다크 테마 디자인
2. **YouTube IFrame Player & 커스텀 볼륨 조절**:
   - 영상 내장 플레이어 연동
   - 커스텀 볼륨 슬라이더 (`player.setVolume`) 지원
3. **타임라인 자막 추출 (STT) & CSV 영구 캐싱**:
   - `Gemini 3.5 Transcribe / 3.6 Flash` 모델 기반 시간대별 자막(`start_time`, `seconds`, `text`) 출력
   - **CSV 영구 저장 (`transcripts.csv`)**: 최초 검색 시 링크와 transcript를 CSV 파일에 저장하고, 이후 동일 링크 검색 시 Gemini API 및 다운로드를 호출하지 않고 즉시 불러옴
   - 자막 항목 클릭 시 해당 위치로 즉시 이동 및 자동 재생
4. **AI 질의응답 (Q&A)**:
   - `Gemini 3.8 Flash` 모델이 자막 문맥을 기반으로 질문에 답변
   - 답변에 매칭되는 타임스탬프(`target_seconds`)를 반환하여 영상 자동 이동 및 재생

---

## 📁 디렉토리 구조

```text
ai-youtube-searcher/
├── backend/
│   ├── main.py                  # FastAPI 웹 서버 및 API 라우트
│   ├── transcripts.csv          # 💾 링크 주소 및 transcript 영구 저장 CSV
│   ├── requirements.txt         # 필수 라이브러리 목록
│   ├── downloads/               # 오디오 캐시 저장소
│   └── services/
│       ├── audio_extractor.py   # yt-dlp 기반 오디오 추출
│       ├── gemini_stt.py        # Gemini STT 타임스탬프 분석
│       ├── gemini_qa.py         # Gemini 3.8 Flash Q&A 처리
│       └── transcript_storage.py# CSV 파일 저장 및 캐시 조회 모듈
├── frontend/
│   ├── index.html               # 유튜브 스타일 다크 테마 웹 UI
│   ├── css/
│   │   └── style.css            # 커스텀 스타일
│   ├── js/
│   │   ├── player.js            # YouTube IFrame API 컨트롤러
│   │   └── app.js               # 이벤트 및 API 연동 로직
│   └── src/
│       ├── components/          # React 컴포넌트 (Transcript.jsx 등)
│       └── App.jsx
└── README.md
```
```

---

## 🚀 실행 방법

### 1. `myenv` 가상환경 활성화 (필요 시)
```powershell
conda activate myenv
```

### 2. 패키지 설치 확인 (이미 설치되어 있다면 건너뛰기)
```powershell
pip install -r backend/requirements.txt
```

### 3. Gemini API 키 설정
```powershell
$env:GEMINI_API_KEY="your-gemini-api-key"
```

### 4. 서버 실행
```powershell
cd ai-youtube-searcher/backend
python main.py
```
*(기본 포트: `8001`로 실행됩니다)*

### 5. 브라우저 접속
웹 브라우저를 열고 다음 주소로 접속합니다:
👉 **http://localhost:8001**
