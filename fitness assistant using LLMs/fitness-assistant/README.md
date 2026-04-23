# Fitness Assistant with LLM Agent

A local-ready fitness assistant that can chat with users, calculate health metrics, generate workout plans, estimate calories/macros, and optionally use an LLM via **OpenAI** or **Ollama**.

## Tech stack

- **Backend:** FastAPI
- **Agent layer:** Lightweight Python agent with tool routing
- **UI:** Streamlit
- **LLM options:** OpenAI, Ollama, or offline fallback
- **Storage:** SQLite for chat history
- **Tests:** Pytest

## Project structure

```text
fitness-assistant/
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   ├── llm.py
│   ├── main.py
│   ├── memory.py
│   ├── prompts.py
│   ├── schemas.py
│   └── tools.py
├── data/
├── tests/
│   └── test_tools.py
├── ui/
│   └── streamlit_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## What the assistant can do

- Compute **BMI**, **BMR**, and **TDEE**
- Suggest calorie targets for **fat loss**, **maintenance**, or **muscle gain**
- Generate structured **workout plans**
- Provide **macro splits** and hydration guidance
- Answer general fitness questions
- Use an LLM when configured, or fall back to a reliable offline mode

## Setup

### 1) Create a virtual environment

```bash
python -m venv .venv
```

### 2) Activate it

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment

Copy `.env.example` to `.env` and fill the model settings if needed.

### 5) Run the Streamlit app

```bash
streamlit run ui/streamlit_app.py
```

### 6) Run the FastAPI server

```bash
uvicorn app.main:app --reload
```

## API example

POST `/chat`

```json
{
  "session_id": "demo",
  "message": "Make me a 4-day workout plan for fat loss. I am 25 years old, 78 kg, 175 cm, male."
}
```

## Notes

- The offline mode works without any API key.
- Ollama is the easiest local LLM option if you want a fully local model.
- This project is designed to be easy to extend into LangGraph, CrewAI, or tool-based multi-agent setups later.
