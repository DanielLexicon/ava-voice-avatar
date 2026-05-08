import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.liveavatar.com/v1"


def clean_api_key(value):
    if not value:
        return ""

    value = value.strip()
    value = value.strip('"').strip("'")
    value = value.rstrip(",")
    value = re.sub(r"\s+", "", value)

    return value


def get_liveavatar_api_key():
    raw_key = os.getenv("LIVEAVATAR_API_KEY", "")
    api_key = clean_api_key(raw_key)

    if not api_key:
        raise ValueError("Falta LIVEAVATAR_API_KEY en las variables de entorno")

    return api_key


def get_headers():
    return {
        "X-API-KEY": get_liveavatar_api_key(),
        "Content-Type": "application/json"
    }


def list_public_avatars():
    url = f"{BASE_URL}/avatars/public"

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=30
    )

    try:
        data = response.json()
    except Exception:
        raise Exception(f"LiveAvatar devolvió una respuesta no JSON: {response.text}")

    if response.status_code == 200:
        return data

    raise Exception(f"LiveAvatar error {response.status_code}: {data}")