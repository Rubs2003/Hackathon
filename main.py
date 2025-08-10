# main.py — Versión optimizada, legible y sin duplicados
import os
import logging
import requests
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentiment import analyze_sentiment, style_instructions_for

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Inicializar la app
app = FastAPI()

# =========================
# Configuración desde variables de entorno
# =========================
# Configuración de Mistral
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-small-latest"
MISTRAL_API_KEY = "bGmkYXph34w8C0xQQjUGiBS7W5Jf0gfP"

# Configuración de ElevenLabs
ELEVENLABS_API_KEY = "sk_2ea192c50ae68635de787c28f38d39d902b39f6a646401c6"
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Advertencias si faltan claves
if not MISTRAL_API_KEY:
    logging.warning("⚠ MISTRAL_API_KEY no está configurada.")
if not ELEVENLABS_API_KEY:
    logging.warning("⚠ ELEVENLABS_API_KEY no está configurada.")

# Historial de conversación (demo, para producción usar almacenamiento persistente)
conversation_history = []

# =========================
# Modelos de request
# =========================
class TopicRequest(BaseModel):
    topic: str

class TextRequest(BaseModel):
    text: str

# =========================
# Funciones auxiliares
# =========================
def _call_mistral(payload: dict, timeout: int = 15) -> dict:
    """Llamada a la API de Mistral con manejo de errores detallado."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }
    try:
        res = requests.post(MISTRAL_URL, headers=headers, json=payload, timeout=timeout)
    except requests.exceptions.RequestException as e:
        logging.exception("Error de red al contactar Mistral")
        raise HTTPException(status_code=502, detail=f"Network error contacting Mistral: {e}")

    if res.status_code != 200:
        try:
            err = res.json()
        except Exception:
            err = res.text
        logging.error("Mistral responded with status %s: %s", res.status_code, err)
        error_detail = {
            "provider": "mistral",
            "status_code": res.status_code,
            "response": err
        }
        if res.status_code in (401, 403):
            error_detail["error"] = "Unauthorized. Check MISTRAL_API_KEY and account access."
        raise HTTPException(status_code=502, detail=error_detail)

    return res.json()

def _format_text_with_ssml(text: str) -> str:
    """Convierte texto en SSML con pausas para ElevenLabs."""
    paragraphs = text.strip().split("\n")
    ssml = "<speak>"
    for para in paragraphs:
        if para.strip():
            ssml += f"<p>{para.strip()}</p><break time='500ms'/>"
    ssml += "</speak>"
    return ssml

# =========================
# Rutas
# =========================
@app.post("/generate-text")
async def generate_text(req: TopicRequest):
    user_text = req.topic.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Falta el campo 'topic'.")

    # Analizar sentimiento y ajustar estilo
    label, score = analyze_sentiment(user_text)
    style_instr = style_instructions_for(label)

    system_prompt = (
        "You are ProfAI – an emotionally intelligent AI professor. "
        "Adapt to the user's emotional state, explain clearly, and give actionable examples. "
        "Always provide a concise summary at the end. " + style_instr
    )
    user_prompt = (
        f"El usuario ha dicho: '{user_text}'. Responde como un profesor interactivo, "
        "explicando paso a paso, con ejemplos y consejos prácticos. Termina con un resumen breve."
    )

    # Mantener historial limitado
    conversation_history.append({"role": "user", "content": user_text})
    if len(conversation_history) > 12:
        conversation_history[:] = conversation_history[-12:]

    payload = {
        "model": MISTRAL_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + conversation_history + [{"role": "user", "content": user_prompt}],
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 1
    }

    data = _call_mistral(payload)

    try:
        ai_text = data["choices"][0]["message"]["content"].replace("*", "")  # quitar negritas Markdown
    except Exception:
        logging.error("Formato inesperado en la respuesta de Mistral: %s", data)
        raise HTTPException(status_code=502, detail={"provider": "mistral", "error": "unexpected response format", "raw": data})

    conversation_history.append({"role": "assistant", "content": ai_text})
    return {"text": ai_text, "sentiment": {"label": label, "score": score}}

@app.post("/generate-audio")
async def generate_audio(req: TextRequest):
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY no configurada.")

    ssml_text = _format_text_with_ssml(req.text)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": ssml_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        "text_type": "ssml"
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.exceptions.RequestException as e:
        logging.exception("Error de red al contactar ElevenLabs")
        raise HTTPException(status_code=502, detail=f"Network error contacting ElevenLabs: {e}")

    if res.status_code != 200:
        try:
            err = res.json()
        except Exception:
            err = res.text
        logging.error("ElevenLabs error %s: %s", res.status_code, err)
        error_detail = {"provider": "elevenlabs", "status_code": res.status_code, "response": err}
        if res.status_code in (401, 403):
            error_detail["error"] = "Unauthorized. Check ELEVENLABS_API_KEY and voice permissions."
        raise HTTPException(status_code=502, detail=error_detail)

    audio_base64 = base64.b64encode(res.content).decode("utf-8")
    return {"audio_base64": audio_base64}
