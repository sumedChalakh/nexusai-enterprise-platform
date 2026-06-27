from typing import TypedDict, Optional, Annotated
import operator


class AgentState(TypedDict):
    question: str
    user_id: str
    doc_id: Optional[str]
    route: Optional[str]
    chat_history: list[dict]   # [{"role": "user"/"assistant", "content": str}]
    retrieved: list[dict]      # raw hybrid search hits
    reranked: list[dict]       # top-n after cross-encoder rerank
    answer: Optional[str]
    sources: list[dict]
    error: Optional[str]
    answer_candidates: Annotated[list, operator.add]
