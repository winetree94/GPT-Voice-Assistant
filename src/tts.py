"""_summary_
    TTS 관련 유틸 모음
"""
import io
import gtts

def parse(text: str, language: str) -> io.BytesIO:
    """
    텍스트를 Google TTS 를 사용하여 음성으로 전환하고 재생합니다.
    Args:
        text (str): 음성으로 변환할 텍스트
    """
    tts = gtts.gTTS(text, lang=language)

    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp
