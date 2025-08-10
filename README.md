# Hackathon
# 📘 ProfAI

**ProfAI** es un asistente educativo interactivo que combina **FastAPI** (backend) y **Streamlit** (frontend) para ofrecer explicaciones, resúmenes y audio generados con IA.  
Usa **Mistral AI** para la generación de texto, **NLTK** para el análisis de sentimiento y **ElevenLabs** para la conversión de texto a voz.

---

## 🚀 Características

- **Generación de resúmenes** claros y adaptados al estado emocional del usuario.
- **Análisis de sentimiento** para ajustar el tono y estilo de respuesta.
- **Conversión de texto a audio** con voz natural (ElevenLabs).
- **Interfaz interactiva** con diseño en columnas:
  - Entrada del usuario a la izquierda.
  - Respuesta de la IA a la derecha.
- **Backend robusto** con manejo avanzado de errores y reintentos.
- **Integración por API** con Mistral y ElevenLabs.

---

## 🛠️ Tecnologías utilizadas

- **Python 3.10+**
- **FastAPI** → API backend
- **Streamlit** → UI frontend
- **Mistral AI API** → Generación de texto
- **NLTK** → Análisis de sentimiento
- **ElevenLabs API** → Text-to-Speech
- **Requests** → Consumo de APIs externas
- **Pydantic** → Validación de datos

---

## 📂 Estructura del proyecto

📦 ProfAI
├── backend
│ ├── main.py # Lógica principal de la API (FastAPI)
│ ├── sentiment.py # Funciones de análisis de sentimiento con NLTK
│ └── requirements.txt # Dependencias backend
├── frontend
│ ├── app.py # Interfaz Streamlit
│ └── requirements.txt # Dependencias frontend
├── .env # Variables de entorno (API Keys, config)
└── README.md # Documentación del proyecto
