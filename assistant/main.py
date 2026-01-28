import sys
import os
import time

# Add project root to path so we can import 'whisper' module
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from whisper_app import speech_to_text
import brain
import speaker

def main():
    print("\n" + "="*50)
    print("🎙️  VOICE ASSISTANT ACTIVATED")
    print("="*50)
    print("Listening... (Press Ctrl+C to exit)\n")

    # API Key check removed (handled in brain.py)
    
    try:
        while True:
            # 1. EAR: Listen
            # We use "auto" mode for natural conversation
            print("\n------------------------------------------------")
            print("👂 Listening for speech...")
            user_text = speech_to_text.record_and_transcribe(mode="manual")
            
            if not user_text:
                continue
                
            print(f"\n👤 You said: {user_text}")
            
            # 2. BRAIN: Think
            print("🧠 Thinking...")
            response = brain.get_response(user_text)
            print(f"🤖 AI: {response}")
            
            # 3. MOUTH: Speak
            speaker.speak(response)
            
            # Small pause to avoid loop spam
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
