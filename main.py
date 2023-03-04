import os
import requests
import json

from rich.console import Console
from rich.markdown import Markdown

from google.cloud import texttospeech
import speech_recognition as sr
import keyboard

# Initialize the recognizer
r = sr.Recognizer()

# Hide pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

console = Console()

api_key = os.environ['OPENAI_API_KEY']

# Instantiates a client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceAccount.json'
client = texttospeech.TextToSpeechClient()

def speak(speak_response):
    synthesis_input = texttospeech.SynthesisInput(text=speak_response)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB", 
        name='en-GB-Neural2-D',
        # ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        pitch = -4.40,
        speaking_rate = 1.05
    )
    response_audio = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open("response.mp3", "wb") as out:
        out.write(response_audio.audio_content)
    play_tts_audio("response.mp3")

def play_tts_audio(filename):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(filename)

    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.quit()

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

        # Print the latest message
        print_message(latest_message)
        speak(latest_message)

        # Check if the user wants to quit
        if user_message.lower() == "quit":
            break

if __name__ == "__main__":
    start_message = input("System instructions: ")
    converse(start_message)
