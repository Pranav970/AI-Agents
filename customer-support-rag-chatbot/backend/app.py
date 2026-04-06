import os
import shutil
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_service import ingest_file, retrieve, generate_answer, reset_collection

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "data" / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(title="Customer Support RAG Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        save_path = UPLOAD_DIR / file.filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        result = ingest_file(str(save_path))
        results.append(result)
    return {"message": "Files processed", "results": results}


@app.post("/chat")
def chat(payload: ChatRequest):
    retrieved = retrieve(payload.question, top_k=payload.top_k)
    output = generate_answer(payload.question, retrieved)
    return output


@app.post("/reset")
def reset():
    reset_collection()
    return {"message": "Vector store cleared"}
