import os
from typing import Generator
from google import genai
# from google.genai import types
types = genai.types

def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되어 있지 않습니다.")
    return genai.Client(api_key=api_key)

def transcribe_audio_stream(
    filepath: str,
    mime_type: str,
    model_name: str = "gemini-3.6-flash",
    prompt: str = "오디오의 모든 음성을 정확하게 한국어(또는 원어)로 전사해주세요. 화자가 바뀔 때 줄바꿈을 해주고 가능한 한 타임스탬프([분:초])를 표시해주세요."
) -> Generator[str, None, None]:
    """
    오디오 파일을 Gemini 모델에 전달하고 전사 텍스트를 실시간 스트리밍 형태로 yield합니다.
    """
    client = get_client()
    file_size = os.path.getsize(filepath)
    
    # 20MB 이하: inline bytes 전달
    if file_size <= 20 * 1024 * 1024:
        with open(filepath, "rb") as f:
            audio_bytes = f.read()
            
        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type=mime_type
        )
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    audio_part,
                    types.Part.from_text(text=prompt)
                ]
            )
        ]
        
        # 모델에 따른 config 설정
        config = None
        if "transcribe" in model_name:
            config = types.GenerateContentConfig(
                audio_transcription_config=types.AudioTranscriptionConfig(
                    word_timestamp=True,
                    diarization=True
                )
            )
            # transcribe 전용 모델의 경우 프롬프트 텍스트 없이 오디오만 전달
            contents = [
                types.Content(
                    role="user",
                    parts=[audio_part]
                )
            ]

        response_stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config
        )
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    else:
        # 20MB 초과: Google GenAI Files API 사용
        uploaded_file = client.files.upload(file=filepath)
        try:
            contents = [
                uploaded_file,
                prompt
            ]
            response_stream = client.models.generate_content_stream(
                model=model_name,
                contents=contents
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        finally:
            # 처리 완료 후 업로드된 파일 정리 (선택 사항)
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass

def transcribe_audio(filepath: str, mime_type: str, model_name: str = "gemini-3.6-flash") -> str:
    """전체 텍스트 전사 결과를 한 번에 문자열로 반환합니다."""
    chunks = list(transcribe_audio_stream(filepath, mime_type, model_name))
    return "".join(chunks)
