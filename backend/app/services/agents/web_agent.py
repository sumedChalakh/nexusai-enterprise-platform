import os
import re

from app.core.llm import gemini_generate

WEB_PROMPT = """Answer the question using ONLY the web results below. Cite with [n].
If the results don't answer it, say so.

Results:
{ctx}

Question: {q}
Answer:"""


def default_provider(query: str) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        # Fallback mock results when API key is missing
        return [
            {
                "title": f"Search results for: {query}",
                "url": "https://example.com/search",
                "snippet": "This is a mock search snippet since TAVILY_API_KEY is not configured in environment variables."
            }
        ]
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        res = client.search(query, max_results=5)
        return [{"title": r["title"], "url": r["url"], "snippet": r["content"]} for r in res["results"]]
    except Exception as e:
        return [{"title": "Search Error", "url": "https://error", "snippet": f"Failed to fetch search results: {str(e)}"}]


def build_web_context(results: list[dict]) -> str:
    lines = [f"[{i}] {r['title']} - {r['snippet']} ({r['url']})" for i, r in enumerate(results, start=1)]
    return "\n".join(lines)


def run_web_agent(question: str, provider=default_provider) -> dict:
    results = provider(question)
    if not results:
        return {"answer": "No web results found for that.", "sources": []}

    ctx = build_web_context(results)
    answer = gemini_generate(WEB_PROMPT.format(ctx=ctx, q=question))

    used = sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer)})
    sources = [{"marker": n, "title": results[n - 1]["title"], "url": results[n - 1]["url"]}
               for n in used if 1 <= n <= len(results)]

    return {"answer": answer, "sources": sources}


def web_agent_node(state: dict, provider=default_provider) -> dict:
    out = run_web_agent(state["question"], provider=provider)
    return {"answer": out["answer"], "sources": out["sources"]}
