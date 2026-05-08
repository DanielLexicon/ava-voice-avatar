import os
import uuid
import json
import urllib.request
import urllib.error

from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from heygen_client import get_streaming_token


load_dotenv()

app = Flask(__name__)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")


if not OPENAI_API_KEY:
    raise ValueError("Falta OPENAI_API_KEY en el archivo .env")

if not ELEVENLABS_API_KEY:
    raise ValueError("Falta ELEVENLABS_API_KEY en el archivo .env")

if not ELEVENLABS_VOICE_ID:
    raise ValueError("Falta ELEVENLABS_VOICE_ID en el archivo .env")


client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """
Tu nombre es Ava.
Eres una avatar experimental de IA con voz generada por ElevenLabs.
El usuario puede hablarte por micrófono y tus respuestas se convierten en audio.
No digas que no tienes voz o que no puedes hablar.
Responde de forma breve, natural, cálida y conversacional.
Si el usuario habla en español, responde en español.
Si el usuario habla en inglés, responde en inglés.
Si el usuario habla en sueco, responde en sueco.
No respondas con textos demasiado largos porque serán leídos en voz alta.
Recuerda el contexto de la conversación actual cuando el usuario haga preguntas de seguimiento.
"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/heygen-token", methods=["GET"])
def heygen_token():
    try:
        token = get_streaming_token()
        return jsonify({"token": token})
    except Exception as e:
        print("HEYGEN TOKEN ERROR:", e)
        return jsonify({
            "error": "No se pudo obtener token de HeyGen",
            "details": str(e)
        }), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    try:
        answer = generate_openai_response(user_message, history)
        audio_url = generate_elevenlabs_audio(answer)

        return jsonify({
            "answer": answer,
            "audio_url": audio_url
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "error": "Error generando respuesta o audio",
            "details": str(e)
        }), 500


def generate_openai_response(user_message, history):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    recent_history = history[-10:]

    for item in recent_history:
        role = item.get("role")
        content = item.get("content")

        if role in ["user", "assistant"] and content:
            messages.append({
                "role": role,
                "content": content
            })

    messages.append({
        "role": "user",
        "content": user_message
    })

    response = client.responses.create(
        model="gpt-4o-mini",
        input=messages
    )

    return response.output_text.strip()


def generate_elevenlabs_audio(text):
    audio_folder = os.path.join(app.root_path, "static", "audio")
    os.makedirs(audio_folder, exist_ok=True)

    audio_filename = f"{uuid.uuid4()}.mp3"
    audio_path = os.path.join(audio_folder, audio_filename)

    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/"
        f"{ELEVENLABS_VOICE_ID}?output_format=mp3_44100_128"
    )

    payload = {
        "text": text,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.75,
            "style": 0.35,
            "use_speaker_boost": True
        }
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            audio_data = response.read()

        with open(audio_path, "wb") as audio_file:
            audio_file.write(audio_data)

        return f"/static/audio/{audio_filename}"

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"ElevenLabs HTTP error {e.code}: {error_body}")

    except urllib.error.URLError as e:
        raise Exception(f"ElevenLabs connection error: {e}")


if __name__ == "__main__":
    app.run(debug=True, port=5050)