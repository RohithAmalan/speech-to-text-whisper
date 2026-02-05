import os
import json
from openai import OpenAI

# Mock Data Removed - Using Database
# from . import database

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

def get_response(user_text):
    """
    Sends text to OpenRouter (using Llama 3 by default) and returns the response.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "I need an OpenRouter API key to think. Please set it in your .env file."

    client = OpenAI(
        base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=api_key,
    )
    
    # Get dynamic date and time (Local & UTC)
    now = datetime.datetime.now()
    local_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    day_of_week = now.strftime("%A")
    
    # UTC Time for World Clock calculations
    utc_now = datetime.datetime.now(pytz.utc)
    utc_time_str = utc_now.strftime("%H:%M")

    # Inject into context
    dynamic_system_prompt = f"{BASE_SYSTEM_PROMPT}\n"
    dynamic_system_prompt += f"Current Local Date and Time: {local_time_str} ({day_of_week}).\n"
    dynamic_system_prompt += f"Current UTC Time: {utc_time_str} (Use this to calculate time for other cities).\n"
    
    # Database check removed per user request
    # dynamic_system_prompt += f"You have access to this live employee database: {json.dumps(employees)}"
    
    try:
        completion = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "qwen/qwen-2.5-7b-instruct"),
            messages=[
                {"role": "system", "content": dynamic_system_prompt},
                {"role": "user", "content": user_text},
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Brain freeze! Error: {str(e)}"

if __name__ == "__main__":
    # Test
    # print(get_response("Who is employee 1223?"))
    print(get_response("What time is it in New York right now?"))
