import os

def speak(text):
    """
    Speaks the given text using the system's default TTS engine.
    """
    if not text:
        return
        
    print(f"🔊 Assistant: {text}")
    # Escape double quotes for shell command
    safe_text = text.replace('"', '\\"')
    os.system(f'say "{safe_text}"')

if __name__ == "__main__":
    speak("System ready.")
