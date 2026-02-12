
# 🎙️ Local AI Voice Assistant (with Hybrid RAG)

A powerful, low-latency voice assistant that runs primarily on your local machine using **Ollama (Llama 3)**, **Whisper (Speech-to-Text)**, and a **Custom TF-IDF Vector Store** for instant knowledge retrieval.

## 🚀 Features
- **Local Intelligence:** Uses Ollama + Llama 3 for 100% privacy and speed.
- **Hybrid RAG:** 
    - **Instant:** Queries local docs using TF-IDF (e.g., "Tell me about Client A").
    - **Smart:** Queries remote MongoDB for complex math (e.g., "Top 5 Clients").
- **Voice I/O:** Whisper for hearing, Edge-TTS for speaking.
- **Reliable:** Falls back to local knowledge if the internet/database is down.

## 📦 Installation

1.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Ollama:**
    - Download from [ollama.com](https://ollama.com).
    - Pull the model: `ollama pull llama3.1`

3.  **Setup Environment:**
    - Create a `.env` file in `assistant/.env`:
    ```ini
    MONGO_URI="mongodb://..."
    LLM_BASE_URL="http://localhost:11434/v1"
    LLM_API_KEY="ollama"
    LLM_MODEL="llama3.1"
    ```

## 🧠 Knowledge Base (RAG) Setup

Before running the assistant, you must "teach" it your data. Run this script whenever your database changes significantly:

```bash
python3 assistant/ingest.py
```
*This fetches data from MongoDB and saves a specialized, fast search index to your disk.*

## ▶️ Running the Assistant

Simply run the startup script:

```bash
./run.sh
```

**Commands to Try:**
- *"Tell me about Client A"* (Uses Local RAG - Instant)
- *"What is invoice #1005?"* (Uses Local RAG - Instant)
- *"Who are my top 5 clients?"* (Uses Live DB - Requires Internet)
- *"What time is it?"* (General Knowledge)

## 🛠️ Troubleshooting

**"Connection Refused" Error:**
- This means the remote MongoDB server is down or blocking your IP.
- **Solution:** You can still use the assistant! RAG queries (specific facts) will still work perfectly using the cached local data. Only "Live" queries (counting/sorting) will fail.

**"Brain Freeze":**
- If the assistant goes silent, check `ollama serve` is running in another tab.