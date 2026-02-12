import os
import json
from openai import OpenAI

# Mock Data Removed - Using Database
# Mock Data Removed - Using Database
from . import database

# Base System Prompt
BASE_SYSTEM_PROMPT = """
You are a smart and friendly AI Voice Assistant.
- You can help with general questions, coding, creative writing, or just chatting.
- Keep your answers concise (1-3 sentences) because you are speaking them out loud.
"""

from dotenv import load_dotenv

load_dotenv()

import datetime
import pytz

import numpy as np
import json
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# RAG DEPENDENCIES (TF-IDF Implementation)
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge_store")
    VECTORIZER_PATH = os.path.join(KNOWLEDGE_DIR, "tfidf_vectorizer.pkl")
    MATRIX_PATH = os.path.join(KNOWLEDGE_DIR, "tfidf_matrix.pkl")
    DOCS_PATH = os.path.join(KNOWLEDGE_DIR, "documents.json")
    
    # Load Model Globally
    if os.path.exists(VECTORIZER_PATH) and os.path.exists(DOCS_PATH):
        print("🧠 Loading Knowledge Base (TF-IDF)...")
        with open(VECTORIZER_PATH, "rb") as f:
            rag_vectorizer = pickle.load(f)
        with open(MATRIX_PATH, "rb") as f:
            rag_matrix = pickle.load(f)
        with open(DOCS_PATH, "r") as f:
            rag_documents = json.load(f)
        RAG_ENABLED = True
        print(f"✅ RAG Loaded: {len(rag_documents)} docs")
    else:
        print("⚠️ RAG Not initialized. Run 'python assistant/ingest.py' first.")
        RAG_ENABLED = False

except Exception as e:
    print(f"⚠️ RAG Init Error: {e}")
    RAG_ENABLED = False

def search_knowledge_base(query, n_results=3):
    """
    Searches the local TF-IDF store for relevant context.
    """
    if not RAG_ENABLED:
        return ""
        
    try:
        # Transform Query
        query_vec = rag_vectorizer.transform([query])
        
        # Compute Cosine Similarity
        cosine_similarities = cosine_similarity(query_vec, rag_matrix).flatten()
        
        # Get Top K Indices
        top_indices = cosine_similarities.argsort()[-n_results:][::-1]
        
        results = []
        for idx in top_indices:
            if cosine_similarities[idx] > 0.1: # Threshold to avoid pure noise
                results.append(rag_documents[idx]['text'])
            
        if not results:
            return ""
            
        context_str = "\\n---\\n".join(results)
        return context_str
    except Exception as e:
        print(f"RAG Search Error: {e}")
        return ""

def get_response(user_text):
    """
    Sends text to OpenRouter (using Llama 3 by default) and returns the response.
    """
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "I need an API key (LLM_API_KEY or OPENROUTER_API_KEY) to think. Please set it in your .env file."

    client = OpenAI(
        base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=api_key,
    )
    print(f"DEBUG: Connecting to {client.base_url}, Model: {os.getenv('LLM_MODEL')}")
    
    # Get dynamic date and time (Local & UTC)
    now = datetime.datetime.now()
    local_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    day_of_week = now.strftime("%A")
    utc_time_str = datetime.datetime.now(pytz.utc).strftime("%H:%M")

    # Dynamic Database Injection (Schema Summary Only)
    try:
        schema = database.get_database_schema(mode="summary")
        schema_json = json.dumps(schema, indent=2)
    except Exception:
        schema_json = "{}"

    # RAG Retrieval
    rag_context = search_knowledge_base(user_text)
    context_injection = ""
    if rag_context:
        print(f"🧠 RAG Retrieved Context: {len(rag_context)} chars")
        context_injection = f"\\n## RELEVANT KNOWLEDGE BASE CONTEXT:\\n{rag_context}\\n"

    # Augmented System Prompt
    system_prompt = f"""{BASE_SYSTEM_PROMPT}

Current Date/Time: {local_time_str} ({day_of_week})
UTC Time: {utc_time_str}

{context_injection}

## DATABASE ACCESS
You have access to a MongoDB database.
AVAILABLE COLLECTIONS:
{schema_json}

## HOW TO USE TOOLS
You have two tools. Output a JSON object ONLY.

1. GET SCHEMA (Use if unsure about collection name)
{{ "tool": "get_schema", "collection": "collection_name" }}

2. SEARCH (Query the database)
{{ "tool": "search", "collection": "collection_name", "query": {{ ... }} }}

EXAMPLES:
- User: "List the first 3 clients"
  You: {{ "tool": "search", "collection": "clients", "query": {{}}, "limit": 3 }}

- User: "Find order #123"
  You: {{ "tool": "search", "collection": "orders", "query": {{ "order_id": 123 }} }}

- User: "Show me the top 10 items"
  You: {{ "tool": "search", "collection": "items", "query": {{}}, "limit": 10 }}

IMPORTANT: 
- The "query" object is a MongoDB Filter. Do NOT use keys like "top", "sort", "clean", or "latest" inside "query".
- Use "limit" correctly as a separate field.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
    ]

    try:
        # 1. First Pass: Ask the LLM
        completion = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "qwen/qwen-2.5-7b-instruct"),
            messages=messages
        )
        response_content = completion.choices[0].message.content.strip()

        # 2. Check for Tool Call (Robust JSON Extraction)
        import re
        json_match = re.search(r'\{.*"tool":.*\}', response_content.replace('\n', ' '), re.DOTALL)
        
        if not json_match:
             clean_content = response_content.replace("```json", "").replace("```", "").strip()
             if clean_content.startswith("{") and '"tool":' in clean_content:
                 json_match = True 

        if json_match or (response_content.strip().startswith("{") and '"tool":' in response_content):
            try:
                print(f"🕵️‍♀️ Tool Call Detected: {response_content}")
                
                 # Parse JSON
                try:
                    if hasattr(json_match, 'group'):
                        tool_data = json.loads(json_match.group(0))
                    else:
                        clean_content = response_content.replace("```json", "").replace("```", "").strip()
                        tool_data = json.loads(clean_content)
                except:
                    start = response_content.find("{")
                    end = response_content.rfind("}") + 1
                    tool_data = json.loads(response_content[start:end])

                tool_type = tool_data.get("tool")
                result_data = {}
                
                if tool_type == "get_schema":
                    col = tool_data.get("collection")
                    result_data = database.get_database_schema(mode="detail", collection_name=col)
                    print(f" Fetched schema for: {col}")
                    
                elif tool_type == "search":
                    col = tool_data.get("collection")
                    query = tool_data.get("query", {})
                    limit = tool_data.get("limit", 10) 
                    results = database.find_documents(col, query, limit=limit)
                    result_data = results
                    print(f"✅ Found {len(results)} results (Limit: {limit})")
                    if len(results) > 0:
                        print(f"📄 Sample: {str(results[0])[:150]}...")

                # 3. Second Pass: Feed results back
                messages.append({"role": "assistant", "content": response_content})
                results_str = json.dumps(result_data, default=str) 
                messages.append({"role": "system", "content": f"TOOL RESULTS: {results_str}"})
                
                final_completion = client.chat.completions.create(
                    model=os.getenv("LLM_MODEL", "qwen/qwen-2.5-7b-instruct"),
                    messages=messages
                )
                return final_completion.choices[0].message.content
            except Exception as e:
                print(f"Tool Error: {e}")
                return f"I tried to use the database tool but it failed: {str(e)}"
        
        # No tool call, just return initial response
        return response_content

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Brain freeze! Error: {str(e)}"

if __name__ == "__main__":
    # Test
    # print(get_response("Who is employee 1223?"))
    print(get_response("What time is it in New York right now?"))
