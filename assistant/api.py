import os
import time
import shutil
import whisper
import brain
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
import contextlib

# Configuration
RECORDINGS_DIR = "recordings"

# Global Model Variable
model = None

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    print("✓ Model ready")
    
    # Cleanup recordings on startup
    if os.path.exists(RECORDINGS_DIR):
        shutil.rmtree(RECORDINGS_DIR)
    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# CORS (Allow all for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.post("/chat")
async def chat_endpoint(audio: UploadFile = File(...)):
    try:
        # 1. Save uploaded audio
        files_dir = os.path.join(RECORDINGS_DIR, "inputs")
        os.makedirs(files_dir, exist_ok=True)
        timestamp = int(time.time())
        input_audio_path = os.path.join(files_dir, f"input_{timestamp}.webm")
        
        with open(input_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
        # 2. Transcribe
        print(f"Transcribing: {input_audio_path}")
        # Whisper handles webm/mp3/wav usually, but if issues arise we might need ffmpeg conversion
        # user has ffmpeg likely since they ran whisper before
        transcription_res = model.transcribe(input_audio_path, fp16=False)
        user_text = transcription_res["text"].strip()
        print(f"User said: {user_text}")
        
        if not user_text:
            return JSONResponse({"user_text": "", "ai_text": "I didn't hear anything.", "audio_url": None})

        # 3. Think (Brain)
        ai_text = brain.get_response(user_text)
        print(f"AI response: {ai_text}")
        
        # 4. Speak (TTS)
        output_dir = os.path.join(RECORDINGS_DIR, "outputs")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"reply_{timestamp}.mp3"
        output_audio_path = os.path.join(output_dir, output_filename)
        
        tts = gTTS(text=ai_text, lang='en')
        tts.save(output_audio_path)
        
        # Return URL relative to static mount
        audio_url = f"/recordings/outputs/{output_filename}"
        
        return JSONResponse({
            "user_text": user_text,
            "ai_text": ai_text,
            "audio_url": audio_url
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

# Mount Static Files
# Mount recordings to serve audio back
app.mount("/recordings", StaticFiles(directory=RECORDINGS_DIR), name="recordings")
# Mount the frontend (root will be added below)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
