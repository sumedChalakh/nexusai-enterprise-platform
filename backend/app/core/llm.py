from app.services.generation_service import generate


def gemini_generate(prompt: str) -> str:
    return generate(prompt)
