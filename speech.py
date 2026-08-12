import pyttsx3


def speak(text):
    if not text:
        return

    engine = None

    try:
        engine = pyttsx3.init()

        # Speech speed
        engine.setProperty("rate", 175)

        # Volume: 0.0 - 1.0
        engine.setProperty("volume", 1.0)

        engine.say(str(text))
        engine.runAndWait()

    finally:
        if engine is not None:
            try:
                engine.stop()
            except Exception:
                pass


if __name__ == "__main__":
    print("EV Voice Output Test")

    speak("Hello. EV voice output is online.")

    speak(
        "This is the second speech test. "
        "If you can hear this, repeated speech is working."
    )