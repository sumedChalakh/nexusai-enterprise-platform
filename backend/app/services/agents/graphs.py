from langgraph.graph import StateGraph, START, END

from app.services.agents.state import AgentState
from app.services.agents.nodes import retrieve_node, rerank_node, generate_node, pdf_retrieve_node
from app.services.agents.sql_agent import run_sql_agent
from app.services.agents.web_agent import run_web_agent
from app.services.agents.router_agent import router_node, pick_route
from app.services.agents.multi_agent import (
    combo_router_node,
    docs_branch_node,
    web_branch_node,
    synthesize_node,
)


# 1. RAG Graph (Day 15)
def build_rag_graph():
    g = StateGraph(AgentState)
    g.add_node("retrieve", retrieve_node)
    g.add_node("rerank", rerank_node)
    g.add_node("generate", generate_node)

    g.add_edge(START, "retrieve")
    g.add_edge("retrieve", "rerank")
    g.add_edge("rerank", "generate")
    g.add_edge("generate", END)

    return g.compile()


rag_graph = build_rag_graph()


def run_rag(user_id: str, question: str, chat_history: list[dict] | None = None) -> dict:
    init: AgentState = {
        "question": question,
        "user_id": user_id,
        "chat_history": chat_history or [],
        "retrieved": [],
        "reranked": [],
        "answer": None,
        "sources": [],
        "error": None,
        "doc_id": None,
        "route": None,
        "answer_candidates": [],
    }
    return rag_graph.invoke(init)


# 2. PDF Graph (Day 16)
def build_pdf_graph():
    g = StateGraph(AgentState)
    g.add_node("pdf_retrieve", pdf_retrieve_node)
    g.add_node("rerank", rerank_node)
    g.add_node("generate", generate_node)

    g.add_edge(START, "pdf_retrieve")
    g.add_edge("pdf_retrieve", "rerank")
    g.add_edge("rerank", "generate")
    g.add_edge("generate", END)

    return g.compile()


pdf_graph = build_pdf_graph()


def run_pdf_agent(user_id: str, doc_id: str, question: str, chat_history: list[dict] | None = None) -> dict:
    init: AgentState = {
        "question": question,
        "user_id": user_id,
        "doc_id": doc_id,
        "route": None,
        "chat_history": chat_history or [],
        "retrieved": [],
        "reranked": [],
        "answer": None,
        "sources": [],
        "error": None,
        "answer_candidates": [],
    }
    return pdf_graph.invoke(init)


# 3. Master Graph (Day 19)
def sql_node(state: dict) -> dict:
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        out = run_sql_agent(db, state["user_id"], state["question"])
    finally:
        db.close()
    return {"answer": out["answer"], "sources": out["sources"]}


def web_node(state: dict) -> dict:
    out = run_web_agent(state["question"])
    return {"answer": out["answer"], "sources": out["sources"]}


def build_master_graph():
    g = StateGraph(AgentState)

    g.add_node("router", router_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("pdf_retrieve", pdf_retrieve_node)
    g.add_node("rerank", rerank_node)
    g.add_node("generate", generate_node)
    g.add_node("sql_node", sql_node)
    g.add_node("web_node", web_node)

    g.add_edge(START, "router")
    g.add_conditional_edges("router", pick_route, {
        "rag": "retrieve",
        "pdf": "pdf_retrieve",
        "sql": "sql_node",
        "web": "web_node",
    })

    g.add_edge("retrieve", "rerank")
    g.add_edge("pdf_retrieve", "rerank")
    g.add_edge("rerank", "generate")
    g.add_edge("generate", END)
    g.add_edge("sql_node", END)
    g.add_edge("web_node", END)

    return g.compile()


master_graph = build_master_graph()


def run_master(user_id: str, question: str, doc_id: str | None = None, chat_history: list[dict] | None = None) -> dict:
    init: AgentState = {
        "question": question,
        "user_id": user_id,
        "doc_id": doc_id,
        "route": None,
        "chat_history": chat_history or [],
        "retrieved": [],
        "reranked": [],
        "answer": None,
        "sources": [],
        "error": None,
        "answer_candidates": [],
    }
    return master_graph.invoke(init)


# 4. Multi-Agent Graph (Day 20)
def pick_branches(state: dict) -> list[str]:
    route = state["route"]
    if route == "both":
        return ["docs_branch", "web_branch"]
    if route == "web":
        return ["web_branch"]
    return ["docs_branch"]


def build_multi_agent_graph():
    g = StateGraph(AgentState)

    g.add_node("router", combo_router_node)
    g.add_node("docs_branch", docs_branch_node)
    g.add_node("web_branch", web_branch_node)
    g.add_node("synthesize", synthesize_node)

    g.add_edge(START, "router")
    g.add_conditional_edges("router", pick_branches, ["docs_branch", "web_branch"])
    g.add_edge("docs_branch", "synthesize")
    g.add_edge("web_branch", "synthesize")
    g.add_edge("synthesize", END)

    return g.compile()


multi_agent_graph = build_multi_agent_graph()


def run_multi_agent(user_id: str, question: str, chat_history: list[dict] | None = None) -> dict:
    init: AgentState = {
        "question": question,
        "user_id": user_id,
        "doc_id": None,
        "route": None,
        "chat_history": chat_history or [],
        "retrieved": [],
        "reranked": [],
        "answer": None,
        "sources": [],
        "error": None,
        "answer_candidates": [],
    }
    return multi_agent_graph.invoke(init)
