
import sys
import os

# Add the project root to sys.path so we can import 'whisper_app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    # Try importing as if running from project root
    import whisper_app.speech_to_text as module
    from whisper_app.speech_to_text import record_and_transcribe, transcribe_file
except ImportError:
    # Fallback if running directly inside the folder
    import speech_to_text as module
    from speech_to_text import record_and_transcribe, transcribe_file
import os


def run_tests():
    print("\n" + "="*40)
    print("PHASE 1 VERIFICATION TESTS")
    print("="*40)
    
    # Test 1: Microphone Recording
    print("\n[Test 1] Live Microphone Recording")
    print("You will control when to start and stop.")
    
    try:
        # mode="manual" handles the "Press ENTER to start/stop" logic internally
        text = record_and_transcribe(mode="manual")
        print(f"✓ Transcription: '{text}'")
        
        if len(text) > 0:
            print("✓ PASS: Non-empty output")
        else:
            print("❌ FAIL: Empty transcription")
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    # Test 2: File Transcription (if you have test files)
    print("\n[Test 2] Audio File Transcription")
    test_file = input("Path to test audio file (or press ENTER to skip): ").strip()
    
    if test_file:
        try:
            text = transcribe_file(test_file)
            print(f"✓ Transcription: '{text}'")
            print("✓ PASS: File transcription works")
        except Exception as e:
            print(f"❌ FAIL: {e}")
    else:
        print(" SKIPPED")
    
    # Test 3: Architecture Check
    print("\n[Test 3] Architecture Verification")
    # import speech_to_text as module (already imported)
    source = open(module.__file__).read()
    
    forbidden = ["openai", "openrouter", "anthropic", "gpt", "claude"]
    violations = [term for term in forbidden if term in source.lower() and term != "openai-whisper"]
    
    if violations:
        print(f"❌ FAIL: Found LLM references: {violations}")
    else:
        print(" PASS: No LLM/OpenRouter detected")
        print(" Whisper-only architecture confirmed")
    
   


if __name__ == "__main__":
    run_tests()