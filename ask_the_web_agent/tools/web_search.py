from duckduckgo_search import DDGS

def search_web(query: str) -> str:
    """
    Searches the web for up-to-date information, news, or facts.
    
    Args:
        query: The search query string.
        
    Returns:
        A string containing a summary of the top search results, 
        including the source URLs and snippets of content.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
        if not results:
            return "Search executed but no relevant results were found."
            
        formatted_results = []
        for r in results:
            formatted_results.append(f"Source: {r.get('href')}\nSnippet: {r.get('body')}\n")
            
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error executing web search: {str(e)}"
