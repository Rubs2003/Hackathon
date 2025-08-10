import streamlit as st 
import requests
from streamlit_extras.add_vertical_space import add_vertical_space

# ================================
# CONFIGURACIÓN GENERAL
# ================================
st.set_page_config(
    page_title="ProfAI",
    layout="wide",
    page_icon="📘"
)

# ================================
# CSS PERSONALIZADO
# ================================
st.markdown("""
    <style>
        /* Animación del fondo */
        @keyframes gradientAnimation {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        @keyframes pulseBrightness {
            0% { filter: brightness(1); }
            50% { filter: brightness(1.15); }
            100% { filter: brightness(1); }
        }
        .stApp {
            background: radial-gradient(circle, #ff6ec4, #7873f5, #00d2ff, #ff9a8b, #f6d365);
            background-size: 400% 400%;
            animation: gradientAnimation 18s ease infinite, pulseBrightness 6s ease-in-out infinite;
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Encabezados */
        h1, h2, h3 {
            color: #ffffff !important;
            text-shadow: 1px 1px 6px rgba(0,0,0,0.6);
            animation: fadeIn 1s ease-in-out;
        }

        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(-10px);}
            to {opacity: 1; transform: translateY(0);}
        }

        /* Caja de entrada */
        .stTextInput input {
            background: rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 12px;
            font-size: 16px;
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
        }
        .stTextInput input:focus {
            border: 1px solid #ffeb3b;
            outline: none;
        }

        /* Botones */
        .stButton>button {
            background: linear-gradient(45deg, #ffeb3b, #ffc107);
            color: black;
            border-radius: 25px;
            font-size: 16px;
            padding: 12px 25px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
            font-weight: bold;
        }
        .stButton>button:hover {
            transform: scale(1.08) rotate(-1deg);
            background: linear-gradient(45deg, #ffc107, #ffeb3b);
            box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
        }

        /* Área de texto */
        textarea {
            background: rgba(255,255,255,0.95) !important;
            color: #000 !important;
            border-radius: 15px;
            padding: 15px;
            font-size: 15px;
        }

        /* Spinner */
        .stSpinner > div {
            border-top-color: #ffeb3b !important;
        }
    </style>
""", unsafe_allow_html=True)

# ================================
# FUNCIÓN PARA DETECTAR TONO Y EMOJIS
# ================================
def detectar_tono_y_emojis(texto):
    texto_lower = texto.lower()
    if any(p in texto_lower for p in ["feliz", "excelente", "maravilloso", "increíble", "positivo", "genial"]):
        return "😄✨🌟"
    elif any(p in texto_lower for p in ["triste", "malo", "preocupante", "negativo", "difícil"]):
        return "😢💔"
    elif any(p in texto_lower for p in ["motivación", "lograr", "puedes", "alcanzar", "éxito", "meta"]):
        return "🚀🔥💪"
    elif any(p in texto_lower for p in ["investigación", "universidad", "profesor", "estudio", "teoría"]):
        return "📚🧠✏️"
    elif any(p in texto_lower for p in ["reflexión", "pensar", "filosofía", "considerar"]):
        return "🤔💭📜"
    else:
        return "🙂"

# ================================
# FORMATEO DEL TEXTO
# ================================
def formatear_texto(texto):
    # Quita asteriscos y hashtags, deja saltos de línea y negritas limpias
    texto = texto.replace("*", "").replace("#", "")
    # Puedes agregar más reglas de formato aquí si el texto viene crudo
    return texto

# ================================
# ENCABEZADO
# ================================
st.markdown("<h1 style='text-align:center;'>📘 ProfAI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Your AI Professor for Summaries, Text & Audio 📚🔊</h3>", unsafe_allow_html=True)
add_vertical_space(1)

# ================================
# ESTADO
# ================================
if "full_text" not in st.session_state:
    st.session_state.full_text = ""

# ================================
# LAYOUT
# ================================
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("📚 **Topic you want to learn:**")
    topic = st.text_input("", value="MIT")

    if st.button("✨ Create summary"):
        with st.spinner("🧠 Thinking and writing your summary..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/generate-text",
                    json={"topic": topic}
                )
                if response.status_code == 200:
                    result = response.json()
                    texto = formatear_texto(result["text"])
                    emojis = detectar_tono_y_emojis(texto)
                    st.session_state.full_text = f"{texto}\n\n{emojis}"
                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")

with col2:
    if st.session_state.full_text:
        st.markdown("🧠 **Summary created:**")
        st.text_area("", value=st.session_state.full_text, height=500)

        add_vertical_space(1)

        if st.button("🔊 Create audio"):
            with st.spinner("🎤 Creating audio..."):
                try:
                    audio_response = requests.post(
                        "http://127.0.0.1:8000/generate-audio",
                        json={"text": st.session_state.full_text}
                    )
                    if audio_response.status_code == 200:
                        audio_data = audio_response.json().get("audio_base64", "")
                        if audio_data:
                            st.audio(f"data:audio/mp3;base64,{audio_data}", format="audio/mp3")
                        else:
                            st.error("⚠️ No valid audio received.")
                    else:
                        st.error(f"❌ Error generating audio: {audio_response.text}")
                except Exception as e:
                    st.error(f"⚠️ Error generating audio: {e}")
