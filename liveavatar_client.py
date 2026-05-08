import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.liveavatar.com/v1"


def clean_value(value):
    if not value:
        return ""

    value = value.strip()
    value = value.strip('"').strip("'")
    value = value.rstrip(",")
    value = re.sub(r"\s+", "", value)

    return value


def get_liveavatar_api_key():
    api_key = clean_value(os.getenv("LIVEAVATAR_API_KEY", ""))

    if not api_key:
        raise ValueError("Falta LIVEAVATAR_API_KEY en las variables de entorno")

    return api_key


def get_liveavatar_avatar_id():
    avatar_id = clean_value(os.getenv("LIVEAVATAR_AVATAR_ID", ""))

    if not avatar_id:
        raise ValueError("Falta LIVEAVATAR_AVATAR_ID en las variables de entorno")

    return avatar_id


def get_liveavatar_voice_id():
    voice_id = clean_value(os.getenv("LIVEAVATAR_VOICE_ID", ""))

    if not voice_id:
        raise ValueError("Falta LIVEAVATAR_VOICE_ID en las variables de entorno")

    return voice_id


def get_headers():
    return {
        "X-API-KEY": get_liveavatar_api_key(),
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def parse_response(response):
    try:
        data = response.json()
    except Exception:
        raise Exception(f"LiveAvatar devolvió una respuesta no JSON: {response.text}")

    if 200 <= response.status_code < 300:
        return data

    raise Exception(f"LiveAvatar error {response.status_code}: {data}")


def list_public_avatars():
    url = f"{BASE_URL}/avatars/public"

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=30
    )

    return parse_response(response)


def create_session_token_full_mode():
    """
    Test para crear un session token de LiveAvatar en FULL mode.

    FULL mode deja que LiveAvatar maneje el pipeline del avatar.
    """
    url = f"{BASE_URL}/sessions/token"

    payload = {
        "mode": "FULL",
        "avatar_id": get_liveavatar_avatar_id(),
        "avatar_persona": {
            "name": "Ava",
            "personality": "Warm, friendly, concise, and helpful AI assistant.",
            "language": "es"
        },
        "voice": {
            "voice_id": get_liveavatar_voice_id()
        }
    }

    response = requests.post(
        url,
        headers=get_headers(),
        json=payload,
        timeout=30
    )

    return parse_response(response)