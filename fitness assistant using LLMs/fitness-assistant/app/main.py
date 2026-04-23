from __future__ import annotations

from fastapi import FastAPI

from app.agent import respond
from app.memory import add_message, get_history
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Fitness Assistant API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    history = get_history(payload.session_id)
    add_message(payload.session_id, "user", payload.message)
    result = respond(payload.message, profile=payload.profile, history=history)
    add_message(payload.session_id, "assistant", result["reply"])
    return ChatResponse(
        session_id=payload.session_id,
        reply=result["reply"],
        intent=result["intent"],
        tool_used=result["tool_used"],
        tool_result=result["tool_result"],
    )
