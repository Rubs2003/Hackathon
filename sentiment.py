from __future__ import annotations
from typing import Literal, Tuple

# NLTK VADER (inglés) — funciona "suficientemente" como demo.
# Si tus textos son mayormente en español y quieres mayor precisión,
# te recomiendo cambiar a un modelo multilingüe de Transformers (ver notas abajo).
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

_analyzer: SentimentIntensityAnalyzer | None = None

def _get_analyzer() -> SentimentIntensityAnalyzer:
    global _analyzer
    if _analyzer is None:
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon')
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer

SentimentLabel = Literal["negative", "neutral", "positive"]

def analyze_sentiment(text: str) -> Tuple[SentimentLabel, float]:
    """
    Retorna (label, compound_score).
    Regla VADER:
      - compound >= 0.05: positive
      - compound <= -0.05: negative
      - otherwise: neutral
    """
    if not text or not text.strip():
        return "neutral", 0.0
    sia = _get_analyzer()
    scores = sia.polarity_scores(text)
    compound = scores.get("compound", 0.0)
    if compound >= 0.05:
        return "positive", compound
    elif compound <= -0.05:
        return "negative", compound
    else:
        return "neutral", compound

def style_instructions_for(label: SentimentLabel) -> str:
    """
    Devuelve instrucciones de estilo en español para guiar al LLM
    según el sentimiento detectado.
    """
    if label == "negative":
        return (
            "Adopta un tono empático y motivador. Valida la posible frustración, "
            "explica con pasos cortos y muy claros, usa ejemplos simples, refuerza logros, "
            "evita jerga innecesaria y ofrece consejos prácticos para avanzar poco a poco."
        )
    elif label == "positive":
        return (
            "Adopta un tono entusiasta y proactivo. Profundiza un poco más, añade retos opcionales, "
            "incluye ideas para experimentar y conexiones con temas avanzados. Mantén claridad."
        )
    else:
        return (
            "Usa un tono claro, directo y didáctico. Estructura la explicación en pasos, "
            "con ejemplos prácticos y resúmenes breves por sección."
        )