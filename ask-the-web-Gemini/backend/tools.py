import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

WEB_SEARCH_TOOL = {
    "name": "web_search",
    "description": "Searches the web for up-to-date information. Use this when you need facts, news, or data you don't know.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query."
            }
        },
        "required": ["query"]
    }
}

def execute_web_search(query: str) -> str:
    """Executes search and formats results with URLs for citations."""
    try:
        response = tavily_client.search(query=query, search_depth="basic", max_results=3)
        results = response.get("results", [])
        formatted_results = []
        for i, res in enumerate(results):
            # Returning URL and content allows the agent to cite sources
            formatted_results.append(f"[{i+1}] Source: {res['url']}\nContent: {res['content']}\n")
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error executing search: {str(e)}"
