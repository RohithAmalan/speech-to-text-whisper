# 🎤 Voice-to-Voice Assistant
**Phase 2: Intelligent Assistant**

This project has evolved into a full Voice-to-Voice assistant that listens, thinks (using Mistral AI), and speaks back to you.

## 🚀 Quick Start (Voice Assistant)

### 1. Prerequisites
You need an **OpenRouter API Key** to power the brain.
1.  Get a key from [OpenRouter](https://openrouter.ai/).
2.  Export it in your terminal:
    ```bash
    export OPENROUTER_API_KEY="sk-or-your-key-here"
    ```

### 2. Install Requirements
If you haven't already:
```bash
pip install -r requirements.txt
```

### 3. Run the Assistant
```bash
python3 assistant/main.py
```

## 🏗️ Architecture (3-Module)

The assistant is split into three clean modules in the `assistant/` directory:

1.  **`brain.py`** 🧠
    -   **Role**: Intelligence.
    -   **Tech**: OpenRouter (Mistral Small) via `openai` client.
    -   **Context**: Knows specific employee data (mock database).

2.  **`speaker.py`** 🔊
    -   **Role**: Speech Synthesis (TTS).
    -   **Tech**: Native macOS `say` command (offline, zero-latency).

3.  **`main.py`** 🎼
    -   **Role**: Orchestrator.
    -   **Loop**: Listens (Whisper) -> Thinks (Brain) -> Speaks (Speaker).

## 🔮 Capabilities
- **Chat**: Talk normally to the AI.
- **Data Lookup**: Ask about employees (e.g., *"Who is employee 1223?"*).
- **Voice Interaction**: Entirely hands-free loop.

---

## 🎤 Sspeech-to-text-foundation/
├── whisper_app/speech_to_text.py      # Core ASR implementation
├── whisper_app/test_transcription.py  # Verification suite
Convert human speech to accurate plain text using Whisper ASR.

### 🎯 Project Goals
- ✅ Solid Automatic Speech Recognition (ASR)
- ✅ Microphone input support
- ✅ Audio file transcription (WAV, MP3)

### 🚀 Quick Start (ASR Tool Only)
To run just the transcription tool without the AI assistant:
```bash
python3 whisper/speech_to_text.py
```
