# 🌐 Ask-the-Web Agent

A production-ready, Perplexity-style AI agent utilizing Anthropic's Claude 3.5 Sonnet, FastAPI, and React. The agent implements a ReAct (Reasoning and Acting) loop to autonomously search the web, aggregate data, and provide cited answers.

## 🏗️ Architecture
- **Frontend**: React, TailwindCSS, Lucide Icons.
- **Backend**: Python, FastAPI.
- **Agent Orchestrator**: Anthropic API (`claude-3-5-sonnet`).
- **Tools Engine**: Tavily Search API.

## 🚀 Setup Instructions

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
