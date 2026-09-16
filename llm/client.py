import hashlib
import json
import os
from dotenv import load_dotenv

load_dotenv()

CACHE_PATH = os.path.join(os.path.dirname(__file__), ".llm_cache.json")


def _load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except OSError:
        pass


def _cache_key(prompt: str, max_tokens: int) -> str:
    raw = f"{max_tokens}|{prompt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def call_llm(prompt: str, max_tokens: int = 1024) -> str:
    cache = _load_cache()
    key = _cache_key(prompt, max_tokens)

    if key in cache:
        return cache[key]

    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    # 1. Try Google Gemini if available
    if gemini_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                )
            )
            text = response.text.strip()
            if text:
                cache[key] = text
                _save_cache(cache)
                return text
        except Exception as e:
            print(f"[DEBUG] Gemini call failed: {e}, attempting other providers...")

    # 2. Try Groq if available
    if groq_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=max_tokens,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content
            if text:
                cache[key] = text
                _save_cache(cache)
                return text
        except Exception as e:
            print(f"[DEBUG] Groq call failed: {e}")

    # 3. Try standard OpenAI if available
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=max_tokens,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content
            if text:
                cache[key] = text
                _save_cache(cache)
                return text
        except Exception as e:
            print(f"[DEBUG] OpenAI call failed: {e}")

    # Graceful Fallback if no LLM key configured or offline
    fallback_response = json.dumps({
        "contextual_flags": [],
        "overall_impression": "Deterministic rule assessment completed. Add GEMINI_API_KEY or GROQ_API_KEY to .env for AI explainability.",
        "llm_certainty": "medium"
    })
    return fallback_response