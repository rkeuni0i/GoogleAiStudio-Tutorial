import os
import re
import json
from typing import List, Dict, Any
from google import genai
from google.genai import types

def get_gemini_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되어 있지 않습니다.")
    return genai.Client(api_key=api_key)

SYSTEM_PROMPT_TRANSCRIBE = """
당신은 YouTube 동영상 음성 타임스탬프 전문 추출기입니다.
제공된 오디오 파일의 발화를 분석하여 음성이 나오는 시간대별로 정확한 타임스탬프와 대사를 추출하세요.
반드시 아래 JSON 형식(JSON 배열)으로만 응답해야 합니다:

[
  {
    "start_time": "00:05",
    "seconds": 5,
    "text": "안녕하세요, 오늘 소개할 주제는..."
  }
]

[규칙]
1. `start_time`은 "분:초" (예: "01:25") 또는 1시간 이상일 경우 "시:분:초" 형식이어야 합니다.
2. `seconds`는 시작 시간을 정수 초 단위(예: 85)로 표현합니다.
3. 발화 흐름에 맞게 문장/문맥 단위로 적절히 분할하세요.
4. 설명이나 서두/결미 없이 오직 유효한 JSON 배열만 출력하세요.
"""

def clean_json_response(raw_text: str) -> str:
    """마크다운 코드 블록(```json ... ```)을 제거하고 순수 JSON 문자열만 추출합니다."""
    text = raw_text.strip()
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        return match.group(1).strip()
    return text

def transcribe_with_timestamps(filepath: str, mime_type: str, model_name: str = "gemini-3.6-flash") -> List[Dict[str, Any]]:
    """
    오디오 파일을 Gemini 모델에 전달하여 시간대별 타임스탬프와 자막 리스트를 추출합니다.
    """
    client = get_gemini_client()
    file_size = os.path.getsize(filepath)

    audio_part = None
    uploaded_file = None

    try:
        # 20MB 이하: inline bytes 전달
        if file_size <= 20 * 1024 * 1024:
            with open(filepath, "rb") as f:
                audio_bytes = f.read()
            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type
            )
            contents = [
                audio_part,
                SYSTEM_PROMPT_TRANSCRIBE
            ]
        else:
            # 20MB 초과: Files API 업로드
            uploaded_file = client.files.upload(file=filepath)
            contents = [
                uploaded_file,
                SYSTEM_PROMPT_TRANSCRIBE
            ]

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )

        raw_text = response.text or "[]"
        cleaned_json = clean_json_response(raw_text)
        data = json.loads(cleaned_json)

        # 혹시 딕셔너리로 감싸져 있는 경우 보정
        if isinstance(data, dict):
            for val in data.values():
                if isinstance(val, list):
                    data = val
                    break

        if isinstance(data, list):
            # 필수 필드 보정
            processed = []
            for item in data:
                if isinstance(item, dict):
                    sec = item.get("seconds", 0)
                    if not sec and "start_time" in item:
                        # start_time에서 초 계산
                        parts = str(item["start_time"]).split(":")
                        try:
                            if len(parts) == 2:
                                sec = int(parts[0]) * 60 + int(parts[1])
                            elif len(parts) == 3:
                                sec = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        except Exception:
                            sec = 0
                    processed.append({
                        "start_time": item.get("start_time", "00:00"),
                        "seconds": int(sec),
                        "text": item.get("text", "")
                    })
            return processed
        return []

    except Exception as e:
        print(f"[STT Error] {e}")
        # 오류 발생 시 기본 안내 항목 반환
        return [
            {
                "start_time": "00:00",
                "seconds": 0,
                "text": f"음성 전사 처리 중 오류가 발생했습니다: {str(e)}"
            }
        ]
    finally:
        if uploaded_file:
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass
