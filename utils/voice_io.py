import speech_recognition as sr
import pyttsx3
import threading

_tts_lock = threading.Lock()

def speak(text):
    """
    Speak text using pyttsx3.
    A fresh engine is created for each call to avoid
    'run loop already started' errors in Streamlit.
    """

    if not text:
        return

    print("Assistant:", text)

    with _tts_lock:

        engine = pyttsx3.init()
        engine.setProperty("rate", 180)

        try:
            engine.say(str(text))
            engine.runAndWait()

        except RuntimeError as e:
            print("TTS error:", e)

        finally:
            try:
                engine.stop()
            except Exception:
                pass


def listen():
    """
    Listen through the microphone and convert speech to text.
    """

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print("Listening...")

            # Shorter adjustment is better for UI interaction
            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=15
            )

    except sr.WaitTimeoutError:

        print("Listening timed out.")
        return ""

    except Exception as e:

        print("Microphone error:", e)
        return ""

    try:

        command = recognizer.recognize_google(
            audio
        )

        print("You:", command)

        return command.lower().strip()

    except sr.UnknownValueError:

        # IMPORTANT:
        # Do not call speak() here.
        # Streamlit will handle the failed recognition state.
        print("Speech not understood.")

        return ""

    except sr.RequestError as e:

        print(
            "Speech recognition service error:",
            e
        )

        return ""

    except Exception as e:

        print(
            "Speech recognition error:",
            e
        )
        return ""