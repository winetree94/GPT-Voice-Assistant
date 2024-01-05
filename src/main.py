#!/usr/bin/env python3
"""
    ChatGPT Voice Assistant
"""
import json
import time
from typing import Final, List
import concurrent.futures
import pyaudio
import speech_recognition
import numpy
import audio
import gpt
import tts
import utils

with open('configuration.json', 'r', encoding='utf-8') as file:
    env = json.load(file)

OPENAI_API_KEY: Final[str] = str(env.get('openai_api_key'))
OPENAI_GPT_MODEL: Final[str] = str(env.get('openai_gpt_model', 'gpt-4'))
OPENAI_GPT_INSTRUCTIONS: Final[str] = str(env.get('openai_gpt_instructions', ''))
LANGUAGE_CODE: Final[str] = str(env.get('language_code', 'en'))
COUNTRY_CODE: Final[str] = str(env.get('country_code', 'US'))
WAKE_WORDS: Final[List[str]] = env.get('wake_words', ['Jarvis'])
GREETING_MESSAGES: Final[List[str]] = env.get('greeting_messages', ['Hello'])

pilot_gpt = gpt.ChatGPT(
    key = OPENAI_API_KEY,
    default_model = OPENAI_GPT_MODEL,
    instructions = OPENAI_GPT_INSTRUCTIONS,
)
pyaudio = pyaudio.PyAudio()
recognizer = speech_recognition.Recognizer()

audio_input_device_id = int(env.get('audio_input_device_id'))
if audio_input_device_id == -1:
    audio.list_audio_input_devices(pyaudio)
    audio_input_device_id = int(input("Enter the ID of the audio input device you want to use: "))

def listen_wake_word():
    """
        음성을 녹음하고 Wake Word 가 감지될 때까지 대기합니다.
    """
    audio.listen_for_wake_word(
        recognizer=recognizer,
        audio_source=source,
        wake_words=WAKE_WORDS,
        language=LANGUAGE_CODE + '-' + COUNTRY_CODE
    )
    greeting_audio = tts.parse(numpy.random.choice(GREETING_MESSAGES), LANGUAGE_CODE)
    audio.play(greeting_audio)
    time.sleep(0.5)
    listen_and_response()

def listen_and_response():
    """
        음성을 녹음하고 텍스트로 변환하여 ChatGPT 로 전송합니다.
        수신받은 응답은 다시 음성으로 변환하여 출력합니다.
    """
    audio.play('./assets/in.wav')
    question = audio.listen_voice_and_return_text(
        recognizer = recognizer,
        audio_source = source,
        language = LANGUAGE_CODE + '-' + COUNTRY_CODE
    )
    audio.play('./assets/out.wav')
    print("You said: ", question)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_loading_sound = executor.submit(
            audio.play,
            './assets/loading.wav'
        )
        response_text = executor.submit(pilot_gpt.chat, question).result()
        response_voice = executor.submit(tts.parse, response_text, LANGUAGE_CODE).result()
        future_loading_sound.cancel()
        time.sleep(0.5)
        future_print = executor.submit(utils.print_slowly, response_text)
        future_voice = executor.submit(audio.play, response_voice)
        future_print.result()
        future_voice.result()
    listen_wake_word()

with speech_recognition.Microphone(
    device_index = None if audio_input_device_id == -2 else audio_input_device_id,
) as source:
    audio.play('./assets/boot.wav')
    print("ChatGPT Assistant is ready")
    listen_wake_word()
