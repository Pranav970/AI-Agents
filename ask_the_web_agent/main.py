from dotenv import load_dotenv
from core.agent import AskTheWebAgent

def main():
    # Load environment variables from the .env file
    load_dotenv()
    
    print("==============================================")
    print("🤖 Starting Ask-the-Web Agent...")
    print("   Type 'exit' or 'quit' to end the session.")
    print("==============================================\n")
    
    try:
        agent = AskTheWebAgent()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("Shutting down agent. Goodbye!")
            break
            
        if not user_input.strip():
            continue
            
        print("\nAgent is thinking and searching the web...")
        
        # The agent will automatically call the web_search tool if needed
        response = agent.process_query(user_input)
        
        print("\n==============================================")
        print(f"Agent:\n{response}")
        print("==============================================\n")

if __name__ == "__main__":
    main()
