import logging
from app.core.config import settings

log = logging.getLogger(__name__)

GENERATION_MODEL = "gemini-2.5-flash"
MAX_OUTPUT_TOKENS = 1024
TEMPERATURE = 0.3   # low temp — favor grounded, factual answers over creativity


def _get_model():
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel(
        GENERATION_MODEL,
        generation_config={
            "temperature": TEMPERATURE,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
        },
    )


def generate(prompt: str) -> str:
    """Non-streaming generation. Returns the full answer text."""
    model = _get_model()
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        log.error("Generation failed: %s", e)
        raise RuntimeError(f"Generation error: {e}") from e


def generate_stream(prompt: str):
    """
    Streaming generation. Yields text chunks as they arrive from Gemini.
    Used by the SSE endpoint for real-time answer display.
    """
    model = _get_model()
    try:
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        log.error("Streaming generation failed: %s", e)
        yield f"\n\n[Error: generation failed — {e}]"
