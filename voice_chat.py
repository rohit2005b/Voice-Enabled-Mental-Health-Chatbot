import speech_recognition as sr
import pyttsx3
from chatbot import get_response

recognizer = sr.Recognizer()
engine = pyttsx3.init()

print("Say something...")

while True:
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5)
            user_input = recognizer.recognize_google(audio)
            print("You said:", user_input)

            tag, bot_response = get_response(user_input)
            print("Bot:", bot_response)

            engine.say(bot_response)
            engine.runAndWait()

        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError:
            print("Network error.")
        except KeyboardInterrupt:
            break
