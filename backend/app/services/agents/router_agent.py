from app.core.llm import gemini_generate

VALID_ROUTES = {"rag", "pdf", "sql", "web"}

ROUTE_PROMPT = """Classify this question into exactly one route. Reply with ONLY the word, nothing else.

- rag: general question that should search across the user's uploaded documents
- pdf: question explicitly about one specific, already-open document (only valid if a doc_id is in context)
- sql: question about metadata - counts, statuses, "how many", "list my documents"
- web: question that has nothing to do with the user's documents (general knowledge, current events)

Question: {q}
Route:"""


def classify_route(question: str, has_doc_id: bool) -> str:
    raw = gemini_generate(ROUTE_PROMPT.format(q=question))
    route = raw.strip().lower()

    if route not in VALID_ROUTES:
        return "rag"
    if route == "pdf" and not has_doc_id:
        return "rag"  # can't run the pdf agent without a doc_id, fall back

    return route


def router_node(state: dict) -> dict:
    route = classify_route(state["question"], has_doc_id=bool(state.get("doc_id")))
    return {"route": route}


def pick_route(state: dict) -> str:
    return state["route"]
