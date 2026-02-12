
# 🧠 AI & RAG Architecture Documentation

This document explains the "Brain" of the voice assistant.

## Tech Stack

| Component          | Technology                      | Purpose                                                           |
| :----------------- | :------------------------------ | :---------------------------------------------------------------- |
| **Brain**          | **Ollama** (Llama 3 / Qwen 2.5) | The main reasoning engine. Runs locally on your CPU/GPU.          |
| **Knowledge Base** | **Scikit-Learn (TF-IDF)**       | Instant, lock-free local search for specific facts (RAG).         |
| **Remote Data**    | **MongoDB** (PyMongo)           | Stores live data and handles complex queries (sorting, counting). |
| **Hearing**        | **OpenAI Whisper**              | State-of-the-art Speech-to-Text processing.                       |
| **Voice**          | **Edge-TTS**                    | High-quality, natural-sounding Text-to-Speech (online).           |

## 🔄 How Hybrid RAG Works

The system uses a "Two-Pass" approach to answer questions:

1.  **Pass 1: Local Knowledge Retrieval (RAG)**
    - When you ask a question, the system first scans the local `knowledge_store/` folder.
    - It uses **TF-IDF Vectorization** to find the most relevant document chunks based on keywords.
    - *Example:* "Tell me about Client A" -> Matches "Client A" document -> Retrieves ID "CLI_001".
    - This happens in **milliseconds** and works offline.

2.  **Pass 2: LLM Reasoning**
    - The retrieved text is injected into the prompt sent to **Ollama**.
    - The LLM reads the context and formulates a natural language answer.

3.  **Pass 3: Live Database Queries (Tools)**
    - If the user asks a complex question that requires calculation (e.g., "Top 5 Clients"), RAG fails (keyword search can't count).
    - The LLM recognizes this and calls the **Database Tool**.
    - This connects to the remote MongoDB server to execute a precise aggregation query.

## 📁 Key Files

-   `assistant/brain.py`: The core logic. Initializes RAG, connects to Ollama, and handles tool calling.
-   `assistant/ingest.py`: Run this script to update the local knowledge base from the remote DB.
-   `assistant/database.py`: Helper functions for MongoDB connectivity.
-   `assistant/api.py`: The FastAPI server linking everything together.

## ⚠️ Known Limitations

-   **Live Data Latency:** Queries that require the live database ("Top 5") depend on your internet connection to the MongoDB server. If the server is down, these specific queries will fail.
-   **RAG Freshness:** The local knowledge base is a snapshot. You must run `python assistant/ingest.py` to refresh it with new data.
