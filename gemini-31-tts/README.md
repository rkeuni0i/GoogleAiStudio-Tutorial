# Gemini 3.1 Flash TTS 예제 코드 분석

이 문서는 [`gemini-31-tts.py`](./gemini-31-tts.py)의 동작 원리와 각 코드 라인의 역할을 한 줄 한 줄(Line-by-Line) 상세하게 설명합니다.

---

## 1. 개요 및 사전 요구 사항

이 스크립트는 **Google GenAI SDK**를 활용하여 텍스트 대본과 오디오 스타일 프로필(감정, 억양, 배경 상황)을 기반으로 음성을 합성(Text-to-Speech)하는 예제입니다. 스트리밍으로 전달되는 원시 PCM/L16 오디오 바이트 스트림을 수집한 뒤, 올바른 WAV 헤더를 생성 및 부착하여 `gemini_news_audio.wav` 파일로 저장합니다.

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

### [Lines 1~11] 라이브러리 임포트 및 초기 설정

```python
1: # To run this code you need to install the following dependencies:
2: # pip install google-genai
```
- **Line 1~2**: 필요한 패키지(`google-genai`) 설치 명령어를 안내하는 주석입니다.

```python
4: import mimetypes
5: import os
6: import re
7: import struct
8: from google import genai
9: # from google.genai import types
10: types = genai.types
```
- **Line 4**: `mimetypes`: MIME 타입 문자열로부터 파일 확장자(예: `.wav`)를 추론하기 위해 사용합니다.
- **Line 5**: `os`: 환경 변수(`GEMINI_API_KEY`)를 읽기 위해 사용합니다.
- **Line 6**: `re`: 정규표현식 모듈(MIME 타입 문자열 파싱 보조)입니다.
- **Line 7**: `struct`: C 구조체 형식의 바이너리 데이터를 패킹/언패킹하는 표준 모듈입니다. WAV 파일의 바이너리 헤더(RIFF/WAVE 규격)를 생성할 때 핵심적으로 사용됩니다.
- **Line 8**: `from google import genai`: Google의 최신 GenAI SDK 클라이언트를 임포트합니다.
- **Line 9~10**: `types = genai.types`: API 호출에 사용되는 요청/설정 데이터 타입들을 참조합니다.

---

### [Lines 14~19] 바이너리 파일 저장 함수

```python
14: def save_binary_file(file_name, data):
15:     f = open(file_name, "wb")
16:     f.write(data)
17:     f.close()
18:     print(f"File saved to to: {file_name}")
```
- **Line 14**: 전달받은 파일명과 바이너리 데이터를 파일로 저장하는 `save_binary_file` 헬퍼 함수입니다.
- **Line 15~17**: 바이너리 쓰기(`wb`) 모드로 파일을 열고 데이터 전체를 기록한 뒤 파일을 닫습니다.
- **Line 18**: 저장이 완료된 파일 경로를 콘솔에 출력합니다.

---

### [Lines 21~25] 클라이언트 생성

```python
21: def generate():
22:     client = genai.Client(
23:         api_key=os.environ.get("GEMINI_API_KEY"),
24:     )
```
- **Line 21**: 음성 생성을 총괄하는 메인 실행 함수 `generate()`를 정의합니다.
- **Line 22~24**: `genai.Client` 객체를 초기화하고, 환경 변수에서 `GEMINI_API_KEY`를 가져와 인증을 수행합니다.

---

### [Lines 26~46] 모델 선택 및 프롬프트(대본 & 연출 지시문) 정의

```python
26:     model = "gemini-3.1-flash-tts-preview"
27:     contents = [
28:         types.Content(
29:             role="user",
30:             parts=[
31:                 types.Part.from_text(text="""Read the following transcript based on the audio profile.
32: 
33: # Audio Profile
34: warm
35: 
36: ## Scene:
37: A live breaking news report from a high-energy television broadcast studio.
38: 
39: ## Sample Context:
40: An urgent breaking news alarm just played, and the anchor turns to the camera with unexpected, breaking tech news.
41: 
42: ## Transcript:
43: [urgent] Breaking news tonight! [excited] Google has just officially unveiled Gemini 4.0 Pro, [shocked] and the tech world is in absolute disbelief over the price tag! While performance has tripled across coding and complex reasoning, [amazed] Google has slashed API prices by an unprecedented ninety percent. We're talking pennies per million tokens! [enthusiastic] It's practically making frontier-level AI free for everyone."""),
44:             ],
45:         ),
46:     ]
```
- **Line 26**: TTS를 지원하는 `"gemini-3.1-flash-tts-preview"` 모델을 지정합니다.
- **Line 27~30**: 사용자 입력(`role="user"`)을 정의하는 `types.Content` 리스트를 구성합니다.
- **Line 31~44**: 모델에게 전달할 지시문 프롬프트를 텍스트 파트로 전달합니다.
  - `Audio Profile`: 톤과 분위기(`warm`).
  - `Scene` & `Sample Context`: 상황적 맥락(긴급 뉴스 속보 스튜디오 현장감).
  - `Transcript`: 감정 태그(`[urgent]`, `[excited]`, `[shocked]`, `[amazed]`, `[enthusiastic]`)가 포함된 실제 낭독 대본입니다. 모델은 이 태그들을 해석하여 어조와 음성 톤을 동적으로 변화시킵니다.

---

### [Lines 47~62] 오디오 생성 파라미터 및 음성(Voice) 설정

```python
47:     generate_content_config = types.GenerateContentConfig(
48:         temperature=1,
49:         response_modalities=[
50:             "audio",
51:         ],
52:         speech_config=types.SpeechConfig(
53:             voice_config=types.VoiceConfig(
54:                 prebuilt_voice_config=types.PrebuiltVoiceConfig(
55:                     voice_name="Zephyr"
56:                 )
57:             )
58:         ),
59:         automatic_function_calling=types.AutomaticFunctionCallingConfig(
60:             disable=True
61:         ),
62:     )
```
- **Line 47~48**: 요청 설정을 담는 `GenerateContentConfig`를 생성하며, 생성 다양성을 위해 `temperature=1`로 지정합니다.
- **Line 49~51**: `response_modalities=["audio"]`: 모델이 텍스트 대신 **오디오 데이터**를 출력하도록 지정합니다.
- **Line 52~58**: `speech_config`: Google GenAI 음성 옵션으로 사전 제공 음성(`PrebuiltVoiceConfig`) 중 `"Zephyr"` 보이스를 선택합니다.
- **Line 59~61**: 자동 함수 호출(Tool Use) 기능을 비활성화합니다.

---

### [Lines 64~82] 스트리밍 수신 및 오디오 데이터 누적

```python
64:     print("Generating audio stream from Gemini...")
65:     audio_buffer = bytearray()
66:     mime_type = "audio/L16;rate=24000"
```
- **Line 64**: 오디오 생성이 시작됨을 알리는 안내 메시지입니다.
- **Line 65**: 스트리밍으로 쪼개져 들어오는 오디오 바이너리 조각들을 차례대로 이어 붙이기 위해 가변 바이트 배열인 `bytearray()`를 초기화합니다.
- **Line 66**: 응답 오디오의 기본 MIME 타입을 24kHz 16비트 리니어 PCM(`audio/L16;rate=24000`)으로 기본 설정합니다.

```python
68:     for chunk in client.models.generate_content_stream(
69:         model=model,
70:         contents=contents,
71:         config=generate_content_config,
72:     ):
73:         if chunk.parts is None:
74:             continue
75:         for part in chunk.parts:
76:             if part.inline_data and part.inline_data.data:
77:                 audio_buffer.extend(part.inline_data.data)
78:                 if part.inline_data.mime_type:
79:                     mime_type = part.inline_data.mime_type
80:             elif part.text:
81:                 print(part.text, end="", flush=True)
```
- **Line 68~72**: `generate_content_stream`을 통해 실시간 스트리밍으로 모델 응답 청크를 수신합니다.
- **Line 73~74**: 청크 내에 파트(`parts`)가 비어 있는 경우 스킵합니다.
- **Line 75**: 청크 내부의 각 파트를 순회합니다.
- **Line 76~79**: 파트에 인라인 바이너리 데이터(`part.inline_data.data`)가 포함되어 있다면 `audio_buffer`에 바이트를 덧붙이고, 제공된 MIME 타입으로 갱신합니다.
- **Line 80~81**: 파트에 텍스트 응답이 함께 온 경우 즉시 터미널에 출력합니다.

---

### [Lines 83~95] 오디오 변환(WAV 헤더 부착) 및 파일 저장

```python
83:     if audio_buffer:
84:         output_file = "gemini_news_audio.wav"
85:         file_extension = mimetypes.guess_extension(mime_type)
86:         if file_extension is None or "pcm" in mime_type.lower() or "l16" in mime_type.lower():
87:             wav_data = convert_to_wav(bytes(audio_buffer), mime_type)
88:             save_binary_file(output_file, wav_data)
89:         else:
90:             output_file = f"gemini_news_audio{file_extension}"
91:             save_binary_file(output_file, bytes(audio_buffer))
92:         print(f"\nCompleted! Generated single audio file: {output_file}")
93:     else:
94:         print("\nNo audio data received.")
```
- **Line 83**: 수신된 오디오 데이터가 존재하는지 확인합니다.
- **Line 84**: 기본 출력 파일명을 `"gemini_news_audio.wav"`로 지정합니다.
- **Line 85**: MIME 타입으로부터 적절한 파일 확장자를 조회합니다.
- **Line 86~88**: 수신된 오디오가 헤더가 없는 순수 원시 PCM(L16) 데이터인 경우, 일반 미디어 플레이어에서 재생할 수 있도록 `convert_to_wav` 함수를 호출해 44바이트 WAV 헤더를 붙인 후 파일로 저장합니다.
- **Line 89~91**: 이미 헤더가 있는 완제품 포맷(mp3 등)인 경우 변환 없이 그대로 저장합니다.
- **Line 92~94**: 처리 완료 안내 또는 데이터 수신 실패 안내를 출력합니다.

---

### [Lines 96~134] WAV 헤더 바이너리 패킹 함수 (`convert_to_wav`)

```python
96: def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
...
106:     parameters = parse_audio_mime_type(mime_type)
107:     bits_per_sample = parameters["bits_per_sample"]
108:     sample_rate = parameters["rate"]
109:     num_channels = 1
110:     data_size = len(audio_data)
111:     bytes_per_sample = bits_per_sample // 8
112:     block_align = num_channels * bytes_per_sample
113:     byte_rate = sample_rate * block_align
114:     chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size
```
- **Line 96~105**: 함수의 역할과 인자, 반환 타입을 설명하는 독스트링입니다.
- **Line 106~108**: MIME 타입 문자열을 파싱하여 비트 심도(기본 16비트)와 샘플 레이트(기본 24000Hz)를 구합니다.
- **Line 109**: 채널 수를 1(모노)로 설정합니다.
- **Line 110**: 원시 오디오 데이터의 총 바이트 길이를 구합니다.
- **Line 111~114**: 표준 WAV 규격에 맞추어 `block_align`, `byte_rate`, 전체 청크 크기(`chunk_size = 36 + data_size`)를 계산합니다.

```python
118:     header = struct.pack(
119:         "<4sI4s4sIHHIIHH4sI",
120:         b"RIFF",          # ChunkID
121:         chunk_size,       # ChunkSize (total file size - 8 bytes)
122:         b"WAVE",          # Format
123:         b"fmt ",          # Subchunk1ID
124:         16,               # Subchunk1Size (16 for PCM)
125:         1,                # AudioFormat (1 for PCM)
126:         num_channels,     # NumChannels
127:         sample_rate,      # SampleRate
128:         byte_rate,        # ByteRate
129:         block_align,      # BlockAlign
130:         bits_per_sample,  # BitsPerSample
131:         b"data",          # Subchunk2ID
132:         data_size         # Subchunk2Size (size of audio data)
133:     )
134:     return header + audio_data
```
- **Line 118~133**: `struct.pack`을 사용해 리틀 엔디언(`"<"`) 바이너리 규격으로 44바이트 WAV 표준 헤더를 만듭니다:
  - `RIFF`: RIFF 컨테이너 식별자
  - `chunk_size`: 전체 파일 크기 - 8바이트
  - `WAVE`: WAV 파일 형식
  - `fmt `: 오디오 포맷 메타데이터 청크 식별자
  - `16, 1`: PCM 포맷 크기(16바이트) 및 PCM 식별 번호(1)
  - `num_channels`, `sample_rate`, `byte_rate`, `block_align`, `bits_per_sample`: 오디오 스펙 정보
  - `data`, `data_size`: 실제 오디오 파형 바이트 스트림 시작 식별자 및 크기
- **Line 134**: 44바이트 헤더 뒤에 원시 오디오 바이트(`audio_data`)를 붙여 완전한 WAV 바이너리를 반환합니다.

---

### [Lines 136~169] MIME 타입 파싱 헬퍼 함수 (`parse_audio_mime_type`)

```python
136: def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
...
148:     bits_per_sample = 16
149:     rate = 24000
150: 
151:     # Extract rate from parameters
152:     parts = mime_type.split(";")
153:     for param in parts: # Skip the main type part
154:         param = param.strip()
155:         if param.lower().startswith("rate="):
156:             try:
157:                 rate_str = param.split("=", 1)[1]
158:                 rate = int(rate_str)
159:             except (ValueError, IndexError):
160:                 pass # Keep rate as default
161:         elif param.startswith("audio/L"):
162:             try:
163:                 bits_per_sample = int(param.split("L", 1)[1])
164:             except (ValueError, IndexError):
165:                 pass # Keep bits_per_sample as default if conversion fails
166: 
167:     return {"bits_per_sample": bits_per_sample, "rate": rate}
```
- **Line 136~150**: MIME 타입 문자열로부터 오디오 인코딩 파라미터를 추출하는 함수입니다. 기본값으로 16비트, 24000Hz를 설정합니다.
- **Line 152~166**: 세미콜론(`;`)으로 구분된 문자열 세그먼트를 순회하며 `rate=` 값(샘플 레이트)과 `audio/L` 뒤의 숫자(비트 심도, 예: L16 -> 16비트)를 추출하여 정수로 변환합니다. 변환에 실패하더라도 예외 처리(`except`)를 통해 기본값을 유지합니다.
- **Line 167**: 추출된 파라미터 딕셔너리를 반환합니다.

---

### [Lines 171~172] 진입점 실행부

```python
171: if __name__ == "__main__":
172:     generate()
```
- **Line 171~172**: 파이썬 인터프리터에서 스크립트를 직접 실행할 때 메인 파이프라인인 `generate()` 함수를 호출합니다.
