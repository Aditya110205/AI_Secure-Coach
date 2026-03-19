import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def _call_gemini(prompt: str) -> str:
    # TEMP: remove this block once quota resets
    return "I hear you. As your AI coach, I want you to know that what you're feeling is valid. Can you tell me more about what's been weighing on you?"

def _call_gemini(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text
        except ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait = 30 * (attempt + 1)  # 30s, 60s, 90s
                print(f"Rate limited. Waiting {wait}s before retry {attempt+1}/3...")
                time.sleep(wait)
            else:
                raise e
    return "I'm currently unavailable due to rate limits. Please try again in a minute."


def get_ai_response(message: str, history: list = []) -> str:
    if history:
        context = "\n".join([
            f"User: {h['user']}\nCoach: {h['ai']}" for h in history[-5:]
        ])
        prompt = f"""You are a professional AI life coach. Be empathetic, supportive, and solution-focused.

Previous conversation:
{context}

User: {message}
Coach:"""
    else:
        prompt = f"""You are a professional AI life coach. Be empathetic, supportive, and solution-focused.

User: {message}
Coach:"""

    return _call_gemini(prompt)


def get_mood_score(message: str) -> int:
    prompt = f"""Analyze the emotional tone of this message and return ONLY a single integer from 1 to 10.
1 = very distressed/negative, 10 = very positive/happy. No explanation, just the number.

Message: "{message}"
Score:"""

    try:
        result = _call_gemini(prompt)
        return int(result.strip())
    except:
        return 5
    

####################################
    
