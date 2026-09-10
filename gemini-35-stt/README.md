# Gemini 3.5 Transcribe (STT) 예제 코드 분석

이 문서는 [`gemini-35-stt-example.py`](./gemini-35-stt-example.py)의 동작 원리와 각 코드 라인의 역할을 한 줄 한 줄(Line-by-Line) 상세하게 설명합니다.

---

## 1. 개요 및 사전 요구 사항

이 스크립트는 **Google GenAI SDK**를 사용하여 오디오 파일(`gemini_news_audio.wav`)을 음성 인식(Speech-to-Text) 모델인 `gemini-3.5-transcribe`에 입력하고, 텍스트 전사(Transcription) 결과를 스트리밍 형태로 실시간 출력하는 예제입니다.

### 의존성 설치 및 환경 변수
```bash
pip install google-genai
```
실행 전 환경 변수에 Google AI Studio의 API 키가 설정되어 있어야 합니다:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-api-key-here"

# Linux / macOS
export GEMINI_API_KEY="your-api-key-here"
```

---

## 2. Line-by-Line 코드 상세 설명

```python
1: # To run this code you need to install the following dependencies:
2: # pip install google-genai
```
- **Line 1~2**: 코드 실행을 위해 필요한 Python 패키지(`google-genai`) 설치 명령어를 안내하는 주석입니다.

```python
4: import base64
5: import os
6: from google import genai
7: # from google.genai import types
8: types = genai.types
```
- **Line 4**: `base64` 모듈을 임포트합니다. 바이너리 데이터 인코딩/디코딩에 사용될 수 있습니다.
- **Line 5**: `os` 모듈을 임포트합니다. 환경 변수(`GEMINI_API_KEY`) 조회 및 파일 경로 연산에 사용됩니다.
- **Line 6**: `google` 패키지에서 신규 공식 SDK인 `genai`를 임포트합니다.
- **Line 7~8**: `types` 네임스페이스를 `genai.types`로부터 가져옵니다. 모델 요청/응답에 사용되는 데이터 클래스(`Content`, `Part`, `GenerateContentConfig` 등)를 정의할 때 사용합니다.

```python
10: def generate():
11:     client = genai.Client(
12:         api_key=os.environ.get("GEMINI_API_KEY"),
13:     )
```
- **Line 10**: 전사 로직을 수행할 `generate()` 함수를 정의합니다.
- **Line 11~13**: GenAI API와 통신하기 위한 `client` 객체를 생성합니다. `os.environ.get("GEMINI_API_KEY")`를 통해 시스템 환경 변수에 등록된 API 키를 읽어와 인증에 사용합니다.

```python
15:     model = "gemini-3.5-transcribe"
```
- **Line 15**: 음성 전사(STT) 전용 모델인 `"gemini-3.5-transcribe"` 모델명을 지정합니다.

```python
16:     audio_path = os.path.join(os.path.dirname(__file__), "gemini_news_audio.wav")
17:     if not audio_path:
18:         print("오디오를 찾을 수 없음")
19:         return 
20:         
21:     with open(audio_path, "rb") as f:
22:         audio_bytes = f.read()
```
- **Line 16**: 현재 스크립트 파일(`__file__`)이 위치한 디렉토리를 기준으로 `gemini_news_audio.wav` 오디오 파일의 경로를 안전하게 조합합니다. 작업 디렉토리 위치에 구애받지 않고 항상 스크립트 옆의 파일을 참조할 수 있습니다.
- **Line 17~19**: 오디오 경로 변수가 비어 있는지 확인하는 안전 검사 코드입니다.
- **Line 21~22**: `open(audio_path, "rb")`를 사용하여 WAV 오디오 파일을 바이너리 읽기(`rb`) 모드로 열고, 전체 바이너리 바이트 데이터를 `audio_bytes` 변수에 저장합니다.

```python
24:     contents = [
25:         types.Content(
26:             role="user",
27:             parts=[
28:                 types.Part.from_bytes(
29:                     data=audio_bytes,
30:                     mime_type="audio/wav",
31:                 ),
32:             ],
33:         ),
34:     ]
```
- **Line 24~34**: 모델에 전송할 입력 메시지 리스트(`contents`)를 구성합니다.
  - `role="user"`: 사용자의 요청임을 나타냅니다.
  - `types.Part.from_bytes(...)`: 로컬 바이너리 데이터를 직접 API 파트로 패키징합니다.
  - `data=audio_bytes`: 읽어온 WAV 파일의 원시 바이트 데이터입니다.
  - `mime_type="audio/wav"`: 입력 오디오의 포맷을 명시하여 모델이 오디오를 정확히 디코딩할 수 있도록 합니다.

```python
35:     generate_content_config = types.GenerateContentConfig(
36:         audio_transcription_config=types.AudioTranscriptionConfig(
37:             word_timestamp=True,
38:             diarization=True,
39:         ),
40:     )
```
- **Line 35~40**: 모델의 추론 및 전사 옵션을 설정하는 `GenerateContentConfig` 객체를 생성합니다.
  - `audio_transcription_config`: 음성 전사 전용 고급 옵션을 지정합니다.
  - `word_timestamp=True`: 각 단어별 시작/종료 타임스탬프(시간 정보) 추출을 활성화합니다.
  - `diarization=True`: 화자 분리(Speaker Diarization)를 활성화하여 서로 다른 발화자를 구분하도록 합니다.

```python
42:     for chunk in client.models.generate_content_stream(
43:         model=model,
44:         contents=contents,
45:         config=generate_content_config,
46:     ):
47:         if text := chunk.text:
48:             print(text, end="")
```
- **Line 42~46**: `client.models.generate_content_stream` 메서드를 호출하여 전사 결과를 스트리밍(Chunk 단위) 방식으로 받아옵니다. 전체 오디오 처리가 끝날 때까지 기다리지 않고 생성되는 대로 실시간 스트림을 받습니다.
- **Line 47~48**: 바다코끼리 연산자(`:=`)를 사용하여 수신된 청크에 텍스트(`chunk.text`)가 존재하는 경우, 줄바꿈 없이(`end=""`) 터미널에 즉시 출력합니다.

```python
50: if __name__ == "__main__":
51:     generate()
```
- **Line 50~51**: 스크립트가 직접 실행되었을 때(`__main__`) `generate()` 함수를 호출하여 전사 파이프라인을 구동합니다.
