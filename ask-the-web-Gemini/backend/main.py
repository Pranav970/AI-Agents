from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    # In a real app, you'd pass a session_id to fetch history from a DB

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    result = run_agent(request.query)
    return {"answer": result["answer"]}
