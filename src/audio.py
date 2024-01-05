"""
    Audio 관련 유틸리티 함수를 정의합니다.
"""
from typing import List, Dict, Any
import pyaudio
import speech_recognition
import pygame
import noisereduce as nr
import numpy as np

def list_audio_input_devices(
    pa: pyaudio.PyAudio
) -> List[Dict[str, Any]]:
    """
    사용자가 가지고 있는 오디오 Input 장치의 목록을 반환합니다.

    Args:
        pyaudio (pyaudio.PyAudio): PyAudio 인스턴스

    Returns:
        List[Dict[str, Any]]: 오디오 장치 목록
    """
    result = []
    info = pa.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        device = pa.get_device_info_by_host_api_device_index(0, i)
        if (device.get('maxInputChannels')) > 0:
            result.append(device)
            print("Input Device id ", i, " - ", device.get('name'))
    return result

def list_audio_output_devices(
    pa: pyaudio.PyAudio
) -> List[Dict[str, Any]]:
    """
    사용자가 가지고 있는 오디오 Output 장치의 목록을 반환합니다.

    Args:
        pyaudio (pyaudio.PyAudio): PyAudio 인스턴스

    Returns:
        List[Dict[str, Any]]: 오디오 장치 목록
    """
    result = []
    info = pa.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        device = pa.get_device_info_by_host_api_device_index(0, i)
        if (device.get('maxOutputChannels')) > 0:
            result.append(device)
            print("Output Device id ", i, " - ", device.get('name'))
    return result

def listen_voice_and_return_text(
    recognizer: speech_recognition.Recognizer,
    audio_source: speech_recognition.Microphone,
    language: str = 'en-US',
) -> str:
    """
    사용자의 음성 텍스트로 반환합니다.

    Args:
        recognizer (speech_recognition.Recognizer): Recognizer 인스턴스
        audio_source (speech_recognition.Microphone): Microphone 인스턴스
    """
    print("Audio listening...")
    while True:
        audio = recognizer.listen(audio_source)
        raw = audio.get_raw_data()
        audio_np = np.frombuffer(raw, dtype=np.int16)
        # 소음 감소 적용
        reduced_noise_audio = nr.reduce_noise(y=audio_np, sr=audio.sample_rate)

        # NumPy 배열을 AudioData 객체로 변환
        reduced_noise_audio_data = speech_recognition.AudioData(
            reduced_noise_audio.tobytes(),
            audio.sample_rate,
            audio.sample_width
        )

        try:
            text = recognizer.recognize_google(reduced_noise_audio_data, language=language)
            print("Audio detected: ", text)
            return text
        except speech_recognition.UnknownValueError:
            print("Audio detected: no words were understood")

def listen_for_wake_word(
    recognizer: speech_recognition.Recognizer,
    audio_source: speech_recognition.Microphone,
    wake_words: List[str],
    language: str = 'en-US',
) -> None:
    """
    wake word 가 감지될 때까지 대기합니다.

    Args:
        recognizer (speech_recognition.Recognizer): Recognizer 인스턴스
        audio_source (speech_recognition.Microphone): Microphone 인스턴스
        wake_words (List[str]): 감지할 단어 목록
    """
    while True:
        text = listen_voice_and_return_text(
            recognizer=recognizer,
            audio_source=audio_source,
            language=language
        )
        if any(word.lower() in text.lower() for word in wake_words):
            print("Wake word detected.")
            break

def play(
    path: str,
) -> None:
    """
    음악 파일을 재생합니다.

    Args:
        path (str): 음악 파일 경로
    """
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
