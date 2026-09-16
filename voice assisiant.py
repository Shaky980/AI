import speech_recognition as sr
import pyttsx3
from datetime import datetime
import random
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)
user_name = ""
def speak(text):
    engine.say(text)
    engine.runAndWait()
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("???? Speak now...")
        audio = r.listen(source)
        try:
            command = r.recognize_google(audio)
            print(f" You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print(" Could not understand.")
            speak("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            print(f" API Error: {e}")
            speak("There was a network issue.")
    return ""
def respond_to_command(command):
    global user_name
    if "hello" in command:
        if user_name:
            speak(f"Hi {user_name}, how can I help you?")
        else:
            speak("Hi there! How can I help you today?")
    elif "your name" in command:
        speak("I am your smart Python assistant.")
    elif "time" in command:
        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
    elif "date" in command:
        today = datetime.now().strftime("%B %d, %Y")
        speak(f"Today is {today}")
    elif "my name is" in command:
        user_name = command.split("my name is")[-1].strip().capitalize()
        speak(f"Nice to meet you, {user_name}!")
    elif "fact" in command:
        facts = [
            "Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs!",
            "Octopuses have three hearts.",
            "Bananas are berries, but strawberries aren’t.",
            "The Eiffel Tower can grow taller in summer.",
            "Water can boil and freeze at the same time in a vacuum."
        ]
        speak(random.choice(facts))
    elif "use male voice" in command:
        engine.setProperty('voice', voices[0].id)
        speak("Switched to male voice.")
    elif "use female voice" in command:
        engine.setProperty('voice', voices[1].id)
        speak("Switched to female voice.")
    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        return False
    else:
        speak("I'm not sure how to help with that.")
    return True
def main():
    speak("Voice assistant activated. Say something!")
    while True:
        command = get_audio()
        if command and not respond_to_command(command):
            break
if __name__ == "__main__":
    main()
