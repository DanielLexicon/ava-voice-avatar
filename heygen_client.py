import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.heygen.com"


def clean_api_key(value):
    """
    Limpia espacios, saltos de línea, tabs, comillas y coma final.
    """
    if not value:
        return ""

    value = value.strip()
    value = value.strip('"').strip("'")
    value = value.rstrip(",")

    # Elimina cualquier espacio, salto de línea o tab dentro del valor
    value = re.sub(r"\s+", "", value)

    return value


def get_heygen_api_key():
    raw_key = os.getenv("HEYGEN_API_KEY", "")
    api_key = clean_api_key(raw_key)

    if not api_key:
        raise ValueError("Falta HEYGEN_API_KEY en las variables de entorno")

    return api_key


def get_headers():
    return {
        "X-Api-Key": get_heygen_api_key(),
        "Content-Type": "application/json"
    }


def get_streaming_token():
    """
    Pide a HeyGen un token temporal para usar el Streaming Avatar SDK en el frontend.
    """
    url = f"{BASE_URL}/v1/streaming.create_token"

    response = requests.post(
        url,
        headers=get_headers(),
        timeout=30
    )

    try:
        data = response.json()
    except Exception:
        raise Exception(f"HeyGen devolvió una respuesta no JSON: {response.text}")

    if response.status_code == 200:
        return data["data"]["token"]

    raise Exception(f"Error HeyGen {response.status_code}: {data}")