# Customer Support RAG Chatbot

A customer support chatbot built with Retrieval-Augmented Generation (RAG), prompt engineering, Claude Sonnet 4.6, and a persistent vector database.

## Features
- Document upload
- PDF, DOCX, TXT, MD, and image support
- Chunking and embedding pipeline
- Vector search with ChromaDB
- Claude Sonnet 4.6 answer generation
- Guardrails and source-based answers
- React chat UI

## Tech Stack
- Backend: FastAPI
- Frontend: React + Vite
- Vector DB: ChromaDB
- Embeddings: Sentence Transformers
- LLM: Claude Sonnet 4.6
- Image understanding: BLIP captioning

## Setup
1. Configure `backend/.env`
2. Start backend on port 8000
3. Start frontend on port 5173

## Flow
Upload documents → parse/chunk/index → retrieve relevant context → expand query → generate answer with Claude → return sources.

## Notes
This project is built for support knowledge bases and can be extended with:
- better chunking
- metadata filters
- hybrid retrieval
- answer evaluation
- feedback loop


## Diagram:

* Indexing process: document parsing, chunking, text/image indexing
* Retrieval: embedding query + nearest neighbor search
* Generation: prompt engineering + LLM + output guardrails
