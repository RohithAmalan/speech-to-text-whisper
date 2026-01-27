"""Speech-to-Text System: Fixed, Manual & Auto-Stop Recording"""
import whisper, sounddevice as sd, numpy as np, scipy.io.wavfile as wav, os, time
from threading import Event

class Config:
    SAMPLE_RATE = 16000
    CHANNELS = 1
    MODEL_TYPE = "base"
    SILENCE_THRESHOLD = 0.01
    SILENCE_DURATION = 2.0
    MAX_RECORD_DURATION = 60
    DEFAULT_DURATION = 5
    CHUNK_DURATION = 0.5  # For manual/auto loops

# Configuration
RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

print(f"Loading Whisper model ({Config.MODEL_TYPE})...")
model = whisper.load_model(Config.MODEL_TYPE)
print("✓ Model ready")

def save_and_transcribe(audio, fs=Config.SAMPLE_RATE):
    if len(audio) == 0 or np.max(np.abs(audio)) < Config.SILENCE_THRESHOLD: 
        print("⚠️  Audio too quiet/empty")
        return None
    
    path = os.path.join(RECORDINGS_DIR, f"rec_{int(time.time())}.wav")
    wav.write(path, fs, audio)
    print(f"✓ Saved: {path}\nTranscribing...")
    
    res = model.transcribe(path, fp16=False)
    print(f"Language: {res['language']}")
    return res["text"].strip()

def record_stream(stop_condition_func, **kwargs):
    q = []
    def cb(indata, f, t, s): q.append(indata.copy())
    
    with sd.InputStream(samplerate=Config.SAMPLE_RATE, channels=Config.CHANNELS, callback=cb):
        stop_condition_func(q, **kwargs)
        
    return np.concatenate(q) if q else np.array([])

def record_fixed(duration=Config.DEFAULT_DURATION):
    print(f"🎤 Recording {duration}s...")
    rec = sd.rec(int(duration * Config.SAMPLE_RATE), 
                 samplerate=Config.SAMPLE_RATE, 
                 channels=Config.CHANNELS)
    sd.wait()
    return rec

def record_manual():
    print("🎤 Press ENTER to start, thence ENTER to stop...")
    input()
    print("Recording... (ENTER to stop)")
    return record_stream(lambda q, **k: input())

def record_auto(silence_dur=Config.SILENCE_DURATION, 
                threshold=Config.SILENCE_THRESHOLD, 
                max_dur=Config.MAX_RECORD_DURATION):
    
    print(f"🎤 Speak now! (Auto-stop after {silence_dur}s silence)")
    
    def wait_silence(q, **k):
        start, silent_start = time.time(), None
        while time.time() - start < max_dur:
            if q and np.mean(np.abs(q[-1])) < threshold:
                if not silent_start: silent_start = time.time()
                elif time.time() - silent_start > silence_dur: break
            else: silent_start = None
            time.sleep(0.1)
            
    return record_stream(wait_silence)

def record_and_transcribe(duration=Config.DEFAULT_DURATION, mode="fixed", **kwargs):
    try:
        if mode == "fixed": audio = record_fixed(duration)
        elif mode == "manual": audio = record_manual()
        elif mode == "auto": audio = record_auto(**kwargs)
        return save_and_transcribe(audio)
    except KeyboardInterrupt:
        raise  # Re-raise to let main.py handle exit
    except Exception as e: return f"Error: {e}"

def transcribe_file(path):
    if not os.path.exists(path): raise FileNotFoundError(f"Missing: {path}")
    print(f"Transcribing: {path}")
    res = model.transcribe(path, fp16=False)
    return res["text"].strip()

def main():
    while True:
        print(f"\n{'='*40}\n1. Fixed\n2. Manual (Start/Stop)\n3. Auto-Stop\n4. File\n5. Exit")
        c = input("Choice: ").strip()
        if c == "5": break
        try:
            if c == "1": 
                dur = int(input(f"Secs ({Config.DEFAULT_DURATION}): ") or Config.DEFAULT_DURATION)
                print(record_and_transcribe(dur, "fixed"))
            elif c == "2": print(record_and_transcribe(mode="manual"))
            elif c == "3": print(record_and_transcribe(mode="auto"))
            elif c == "4": print(transcribe_file(input("Path: ").strip()))
        except Exception as e: print(f"❌ {e}")

if __name__ == "__main__": main()