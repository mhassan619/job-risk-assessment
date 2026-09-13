import os
import json
import hashlib
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-120b"

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
    raw = f"{MODEL}|{max_tokens}|{prompt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def call_llm(prompt: str, max_tokens: int = 1024) -> str:
    cache = _load_cache()
    key = _cache_key(prompt, max_tokens)

    if key in cache:
        return cache[key]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0,
            reasoning_effort="low",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content

        if not text or not text.strip():
            raise ValueError("LLM returned empty content")

        cache[key] = text
        _save_cache(cache)
        return text

    except Exception as e:
        print(f"\n[DEBUG] LLM call failed with: {type(e).__name__}: {e}\n")
        return f'{{"error": "LLM call failed", "detail": "{str(e)}"}}'