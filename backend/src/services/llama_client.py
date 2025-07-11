import requests
import os
from dotenv import load_dotenv
load_dotenv()

LLAMA_ENDPOINT = os.getenv("LLAMA_API_URL")  # Set this in your .env

def ask_llama(question: str) -> str:
    if not LLAMA_ENDPOINT:
        raise ValueError("LLAMA_API_URL not set")

    payload = {"inputs": question}

    try:
        response = requests.post(LLAMA_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        # The model usually returns {"generated_text": "..."}
        return result.get("generated_text", "").strip()

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"LLaMA API call failed: {e}")
