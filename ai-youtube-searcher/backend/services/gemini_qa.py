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

def clean_json_response(raw_text: str) -> str:
    text = raw_text.strip()
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        return match.group(1).strip()
    return text

def answer_question_with_transcript(
    question: str,
    transcript: List[Dict[str, Any]],
    video_title: str = "",
    model_name: str = "gemini-3.8-flash"
) -> Dict[str, Any]:
    """
    영상 자막 타임라인을 기반으로 사용자의 질문에 답변하고,
    해당 내용이 등장하는 타임스탬프(초)를 도출하여 반환합니다.
    """
    client = get_gemini_client()

    # 자막 텍스트를 시간대별로 정리
    transcript_text = "\n".join([
        f"[{item.get('start_time', '00:00')}] ({item.get('seconds', 0)}초) {item.get('text', '')}"
        for item in transcript
    ])

    system_instruction = f"""
당신은 YouTube 동영상 탐색 및 질의응답 전문 AI 어시스턴트입니다.
사용자는 영상의 특정 내용이나 질문에 대한 답을 찾고 있으며, 해당 시점으로 즉시 이동하여 시청하고자 합니다.

[영상 제목]
{video_title}

[영상 자막 및 타임스탬프 정보]
{transcript_text}

[답변 작성 지침]
1. 위 자막 정보를 철저히 분석하여 사용자의 질문에 명확하고 친절하게 답변하세요.
2. 답변할 때 해당 내용이 영상의 몇 분 몇 초에 나오는지 언급하세요 (예: "[01:25] 구간에서 ...").
3. 질문과 가장 관련성이 높은 영상의 시작 시점(초, 정수)을 `target_seconds`로 명시하세요.
4. 만약 영상 전체에 걸친 내용이거나 특정 시점을 짚기 어려운 경우 `target_seconds`는 0으로 지정하세요.

[반드시 준수할 JSON 응답 형식]
{{
  "answer": "질문에 대한 상세하고 친절한 설명 (언급된 타임스탬프 포함)",
  "target_seconds": 85,
  "timestamp_str": "01:25"
}}
오직 위 JSON 객체 형식으로만 응답하세요.
"""

    prompt = f"질문: {question}"

    # 모델 호출 (gemini-3.8-flash 우선 시도, 지원되지 않을 경우 gemini-3.6-flash로 fallback)
    models_to_try = [model_name, "gemini-3.6-flash"]

    last_error = None
    for m in models_to_try:
        try:
            response = client.models.generate_content(
                model=m,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            raw_text = response.text or "{}"
            cleaned = clean_json_response(raw_text)
            data = json.loads(cleaned)
            return {
                "answer": data.get("answer", "답변을 생성하지 못했습니다."),
                "target_seconds": int(data.get("target_seconds", 0)),
                "timestamp_str": data.get("timestamp_str", "00:00")
            }
        except Exception as e:
            last_error = e
            continue

    return {
        "answer": f"답변 처리 중 오류가 발생했습니다: {str(last_error)}",
        "target_seconds": 0,
        "timestamp_str": "00:00"
    }
