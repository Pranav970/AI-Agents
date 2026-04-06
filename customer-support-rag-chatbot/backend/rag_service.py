import os
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any

import fitz
from docx import Document
from dotenv import load_dotenv
from PIL import Image
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import chromadb
from anthropic import Anthropic

from prompts import SYSTEM_PROMPT, QUERY_REWRITE_PROMPT

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "data" / "uploads")))
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", str(BASE_DIR / "data" / "chroma")))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
IMAGE_MODEL_NAME = "Salesforce/blip-image-captioning-base"
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

embedding_model = SentenceTransformer(EMBED_MODEL_NAME)
image_captioner = pipeline("image-to-text", model=IMAGE_MODEL_NAME)

chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = chroma_client.get_or_create_collection(
    name="support_kb",
    metadata={"hnsw:space": "cosine"}
)

anthropic_client = None
if os.getenv("ANTHROPIC_API_KEY"):
    anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    text = clean_text(text)
    if not text:
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(0, end - overlap)
    return chunks


def extract_text_from_pdf(path: Path) -> str:
    doc = fitz.open(str(path))
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    return "\n".join(pages)


def extract_text_from_docx(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join([p.text for p in doc.paragraphs])


def extract_text_from_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def caption_image(path: Path) -> str:
    image = Image.open(str(path)).convert("RGB")
    result = image_captioner(image)
    if isinstance(result, list) and result:
        return result[0].get("generated_text", "").strip()
    return ""


def extract_text(path: Path) -> Dict[str, Any]:
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return {"type": "pdf", "text": extract_text_from_pdf(path)}
    if suffix in {".docx"}:
        return {"type": "docx", "text": extract_text_from_docx(path)}
    if suffix in {".txt", ".md", ".markdown"}:
        return {"type": "text", "text": extract_text_from_txt(path)}
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        caption = caption_image(path)
        return {"type": "image", "text": f"Image caption: {caption}"}

    return {"type": "unknown", "text": ""}


def embed_text(text: str):
    return embedding_model.encode([text], normalize_embeddings=True)[0].tolist()


def upsert_chunks(source_name: str, source_type: str, chunks: List[str]) -> int:
    if not chunks:
        return 0

    ids = []
    docs = []
    embs = []
    metas = []

    for i, chunk in enumerate(chunks):
        chunk_id = str(uuid.uuid4())
        ids.append(chunk_id)
        docs.append(chunk)
        embs.append(embed_text(chunk))
        metas.append({
            "source": source_name,
            "source_type": source_type,
            "chunk_index": i
        })

    collection.upsert(
        ids=ids,
        documents=docs,
        embeddings=embs,
        metadatas=metas
    )
    return len(chunks)


def ingest_file(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    extracted = extract_text(path)
    text = extracted["text"]
    source_type = extracted["type"]

    if not text.strip():
        return {
            "file": path.name,
            "status": "skipped",
            "chunks_indexed": 0,
            "reason": "No extractable text found"
        }

    chunks = chunk_text(text)
    indexed = upsert_chunks(path.name, source_type, chunks)

    return {
        "file": path.name,
        "status": "indexed",
        "chunks_indexed": indexed,
        "source_type": source_type
    }


def rewrite_query(question: str) -> str:
    if not anthropic_client:
        return question.strip()

    try:
        resp = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=80,
            temperature=0.2,
            system=QUERY_REWRITE_PROMPT,
            messages=[{"role": "user", "content": question}]
        )
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        return clean_text(text) or question.strip()
    except Exception:
        return question.strip()


def retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    rewritten = rewrite_query(query)
    q_emb = embed_text(rewritten)

    result = collection.query(
        query_embeddings=[q_emb],
        n_results=top_k
    )

    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    items = []
    for doc, meta, dist in zip(docs, metas, distances):
        items.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "source_type": meta.get("source_type", "unknown"),
            "chunk_index": meta.get("chunk_index", -1),
            "distance": float(dist)
        })
    return items


def build_context(retrieved: List[Dict[str, Any]]) -> str:
    blocks = []
    for i, item in enumerate(retrieved, start=1):
        blocks.append(
            f"[Source {i}] File: {item['source']} | Type: {item['source_type']} | Chunk: {item['chunk_index']}\n"
            f"{item['text']}"
        )
    return "\n\n".join(blocks)


def generate_answer(question: str, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
    context = build_context(retrieved)

    if not anthropic_client:
        return {
            "answer": "ANTHROPIC_API_KEY is missing. Add it to backend/.env and restart the server.",
            "sources": retrieved
        }

    user_prompt = f"""
Question:
{question}

Context:
{context}

Instructions:
- Use the context above to answer.
- If the context is insufficient, say exactly what is missing.
- Cite the source numbers in a simple way like [Source 1], [Source 2].
- Keep the answer concise and support-style.
"""

    try:
        resp = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=600,
            temperature=0.2,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )
        answer = "".join(block.text for block in resp.content if hasattr(block, "text")).strip()
        return {"answer": answer, "sources": retrieved}
    except Exception as e:
        return {
            "answer": f"Generation failed: {str(e)}",
            "sources": retrieved
        }


def reset_collection() -> None:
    try:
        chroma_client.delete_collection("support_kb")
    except Exception:
        pass

    global collection
    collection = chroma_client.get_or_create_collection(
        name="support_kb",
        metadata={"hnsw:space": "cosine"}
    )
