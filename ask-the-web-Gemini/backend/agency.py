import os
import anthropic
from tools import WEB_SEARCH_TOOL, execute_web_search

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert research agent. Your goal is to provide accurate, comprehensive answers.
If you do not know the answer, use the web_search tool. 
ALWAYS cite your sources using bracketed numbers like [1], [2] at the end of relevant sentences.
Think step-by-step. If the initial search results are insufficient, reflect and search again with a different query.
"""

def run_agent(user_query: str, chat_history: list = None) -> dict:
    if chat_history is None:
        chat_history = []
        
    messages = chat_history + [{"role": "user", "content": user_query}]
    
    # ReAct Loop (Max 3 iterations to prevent infinite loops)
    for step in range(3):
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=[WEB_SEARCH_TOOL]
        )
        
        # Add Claude's response (which might include a tool call) to history
        messages.append({"role": "assistant", "content": response.content})
        
        # Check if Claude decided to stop and return text
        if response.stop_reason == "end_turn":
            # Extract final text block
            final_text = next((block.text for block in response.content if block.type == "text"), "")
            return {"answer": final_text, "history": messages}
            
        # Check if Claude decided to use a tool
        elif response.stop_reason == "tool_use":
            tool_call = next((block for block in response.content if block.type == "tool_use"), None)
            
            if tool_call and tool_call.name == "web_search":
                search_query = tool_call.input["query"]
                print(f"Agent Action: Searching for -> {search_query}")
                
                # Execute tool
                observation = execute_web_search(search_query)
                
                # Feed observation back into Claude
                messages.append({
                    "role": "user", 
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": observation
                    }]
                })
    
    return {"answer": "Agent reached max iterations without finalizing.", "history": messages}
