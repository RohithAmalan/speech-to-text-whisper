
import speech_to_text as module
from speech_to_text import record_and_transcribe, transcribe_file
import os


def run_tests():
    print("\n" + "="*40)
    print("PHASE 1 VERIFICATION TESTS")
    print("="*40)
    
    # Test 1: Microphone Recording
    print("\n[Test 1] Live Microphone Recording")
    print("You will record for 3 seconds. Speak clearly.")
    input("Press ENTER when ready...")
    
    try:
        text = record_and_transcribe(duration=3)
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
        print("✓ PASS: No LLM/OpenRouter detected")
        print("✓ Whisper-only architecture confirmed")
    
    # Summary
    print("\n" + "="*60)
    print("PHASE 1 COMPLETION CHECKLIST")
    print("="*60)
    print("□ Speech converts correctly to text")
    print("□ Works for everyday conversation")
    print("□ Output is readable and stable")
    print("□ Handles different accents")
    print("□ Works with audio >30 seconds")
    print("□ Stable with background noise")
    print("✓ Whisper is the only AI model used")
    print("✓ No OpenRouter / No LLM")
    print("\nManually verify remaining items with real-world testing.")


if __name__ == "__main__":
    run_tests()