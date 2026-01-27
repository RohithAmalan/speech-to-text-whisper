import os
import json
from openai import OpenAI

# Mock Data
EMPLOYEES = [
    {"id": "1223", "name": "John Doe", "role": "Senior Engineer", "department": "AI Research"},
    {"id": "1224", "name": "Jane Smith", "role": "Product Manager", "department": "Design"},
    {"id": "1225", "name": "Bob Wilson", "role": "Intern", "department": "Coffee Operations"},
]

# System Prompt
SYSTEM_PROMPT = f"""
You are a helpful voice assistant. Keep answers concise (1-2 sentences) for speech synthesis.
You have access to this employee data: {json.dumps(EMPLOYEES)}
If asked about an employee, lookup their ID and provide details.
"""

def get_response(user_text):
    """
    Sends text to OpenRouter (Mistral) and returns the response.
    """
    api_key = "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"
    if not api_key:
        return "I need an OpenRouter API key to think. Please set it in your environment."

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct", # Llama 3 8B Instruct (Fast & Concise)
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Brain freeze! Error: {str(e)}"

if __name__ == "__main__":
    # Test
    print(get_response("Who is employee 1223?"))
