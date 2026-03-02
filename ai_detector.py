import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DETECT_API_URL = os.getenv("DETECT_API_URL")
ANON_KEY = os.getenv("SUPABASE_ANON_KEY")


def detect_ai(text: str):
    """
    Calls Lovable edge function to detect AI-generated text.
    Returns: (ai_copied: 0|1, ai_score: 0-100)
    """

    if not text or len(text.strip()) < 50:
        return 0, 0  # Not enough text to analyze

    headers = {
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(
            DETECT_API_URL,
            json={"text": text},
            headers=headers,
            timeout=60
        )

        if resp.status_code != 200:
            print(f"Detection API error: {resp.status_code} - {resp.text}")
            return 0, 0

        result = resp.json()

        verdict = result.get("verdict", "human")
        confidence = int(result.get("confidence", 0))

        if verdict in ["ai", "mixed"]:
            return 1, confidence
        else:
            return 0, 100 - confidence

    except requests.Timeout:
        print("Detection API timeout")
        return 0, 0
    except Exception as e:
        print(f"AI detection error: {e}")
        return 0, 0


# ---------------- TEST ----------------
if __name__ == "__main__":
    sample_text = """
    Artificial intelligence systems analyze large datasets and automatically
    generate predictions without explicit programming by humans.
    """
    print(detect_ai(sample_text))
