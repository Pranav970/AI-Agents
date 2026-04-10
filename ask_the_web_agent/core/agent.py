import os
from google import genai
from google.genai import types
from tools.web_search import search_web

class AskTheWebAgent:
    def __init__(self, model_id: str = 'gemini-2.5-flash'):
        """Initializes the Agent with the necessary LLM client and tools."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
            
        self.client = genai.Client()
        self.model_id = model_id
        
        # System instructions define the agent's persona and constraints
        system_instruction = (
            "You are an advanced 'Ask-the-Web' research agent, similar to Perplexity. "
            "Always use the `search_web` tool to gather the most current and accurate "
            "information before answering a user's prompt. Synthesize the raw search "
            "results into a well-structured, easy-to-read response. Cite your sources "
            "using the URLs provided in the search results."
        )
        
        # Configure the tool calling capabilities
        self.config = types.GenerateContentConfig(
            tools=[search_web],
            temperature=0.3, # Low temperature for factual consistency
            system_instruction=system_instruction
        )
        
        # Start a persistent chat session to maintain conversation history
        self.chat_session = self.client.chats.create(
            model=self.model_id,
            config=self.config
        )

    def process_query(self, user_query: str) -> str:
        """Sends the user query to the agent and returns the synthesized response."""
        try:
            response = self.chat_session.send_message(user_query)
            return response.text
        except Exception as e:
            return f"An error occurred during processing: {e}"
