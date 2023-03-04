import sys, os

import requests
import json

from rich.console import Console
from rich.markdown import Markdown

from google.cloud import texttospeech
import speech_recognition as sr
import keyboard

import time
from time import sleep

import threading

from dotenv import load_dotenv

# Hide pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# Initialize the recognizer
r = sr.Recognizer()

console = Console()

extDataDir = os.getcwd()
if getattr(sys, 'frozen', False):
    extDataDir = sys._MEIPASS
load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))

api_key = os.environ['OPENAI_API_KEY']

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Instantiates a client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = resource_path('ServiceAccount.json')
client = texttospeech.TextToSpeechClient()

def speak(response, speak_response, code):
    synthesis_input = texttospeech.SynthesisInput(text=speak_response)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB", 
        name='en-GB-Neural2-D',
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        effects_profile_id = [
            "small-bluetooth-speaker-class-device"
        ],
        pitch = -4.40,
        speaking_rate = 1.23

    )
    response_audio = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open("response.mp3", "wb") as out:
        out.write(response_audio.audio_content)
    play_tts_audio("response.mp3", response, code)

def play_tts_audio(filename, response, code):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(filename)

    # Create a new thread and run the append_text function on it
    thread = threading.Thread(target=print_stream, args=(response, code,))
    thread.start()

    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.quit()

    os.remove(filename)

    thread.join()

def print_message(message):
    console.print(Markdown(message))

def get_latest_message(messages):
    # Define the API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Set the headers for the API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Set the data for the API request
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
    }

    # Make the API request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Get the latest message from the response
    latest_message = response.json()["choices"][0]["message"]["content"]

    # Add the latest message to the list of messages
    messages.append({"role": "assistant", "content": latest_message})

    return latest_message

def listen():
    # Loop until the user presses the Escape key
    while not keyboard.is_pressed('esc'):
        # Wait for the user to hold down the space bar
        while not keyboard.is_pressed('space'):
            pass

        # Exception handling to handle
        # exceptions at the runtime
        try:
            print("Listening...")
            # use the microphone as source for input.
            with sr.Microphone() as source:
                # wait for a second to let the recognizer
                # adjust the energy threshold based on
                # the surrounding noise level
                r.adjust_for_ambient_noise(source, duration=0.2)

                #listens for the user's input
                audio = r.listen(source)

                # Using Google to recognize audio
                MyText = r.recognize_google(audio)
                MyText = MyText.lower()

                print(MyText)
                return(MyText)
                

        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print("Unknown error occurred")

def print_stream(response, code):
        print("")
        code_index = 0
        in_code = False
        words = response.split()
        for word in words:
            if word == "```":
                if in_code:
                    in_code = False
                    continue
                else:
                    print('\n')
                    in_code = True
                    if code_index < len(code):
                        console.print(Markdown(code[code_index]))
                        print('\n')
                        code_index += 1
                    continue
            if not in_code:
                print(word, end=" ")
                time.sleep(len(word) / 14)
        print("\n")

def converse(start_message):
    messages = [{"role": "system", "content": start_message}]

    while True:
        # Prompt the user for the next message
        user_message = listen()
        print("\n")

        # Add the user message to the list of messages
        messages.append({"role": "user", "content": user_message})

        # Get the latest message from the API
        latest_message = get_latest_message(messages)

        speak_response = remove_code(latest_message)
        code = get_code(latest_message)

        # Print the latest message
        # print_message(latest_message)
        speak(latest_message, speak_response, code)

        # Check if the user wants to quit
        if user_message.lower() == "quit":
            break

def get_code(text):
        start = "```"
        results = []
        while start in text:
            start_index = text.find(start)
            end_index = text.find(start, start_index + len(start)) + len(start)
            result = text[start_index:end_index]
            results.append(result)
            text = text[end_index:]
        return results

def remove_code(text):
    start = "```"
    while start in text:
        start_index = text.find(start)
        end_index = text.find(start, start_index + len(start)) + len(start)
        text = text[:start_index] + text[end_index:]
    # print(text)
    text = text.replace("`", "'")
    return text

if __name__ == "__main__":
    start_message = input("Enter system instructions: ")
    converse(start_message)
