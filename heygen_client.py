import os
import requests
from dotenv import load_dotenv

load_dotenv()

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")

BASE_URL = "https://api.heygen.com"

HEADERS = {
    "X-Api-Key": HEYGEN_API_KEY,
    "Content-Type": "application/json"
}


def get_streaming_token():
    """
    Pide a HeyGen un token temporal para usar el Streaming Avatar SDK en el frontend.
    """
    if not HEYGEN_API_KEY:
        raise ValueError("Falta HEYGEN_API_KEY en el archivo .env")

    url = f"{BASE_URL}/v1/streaming.create_token"

    response = requests.post(url, headers=HEADERS, timeout=30)

    try:
        data = response.json()
    except Exception:
        raise Exception(f"HeyGen devolvió una respuesta no JSON: {response.text}")

    if response.status_code == 200:
        return data["data"]["token"]

    raise Exception(f"Error HeyGen {response.status_code}: {data}")