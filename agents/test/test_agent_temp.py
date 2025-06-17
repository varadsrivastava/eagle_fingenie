import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import UserProxyAgent
from duckduckgo_search_agent import create_duckduckgo_search_agent
from utils.keys import openai_key

def test_search_agent():
    # Create the search agent
    search_agent = create_duckduckgo_search_agent()
    
    # Create a user proxy agent for testing
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="ALWAYS",  # Changed to NEVER since we want automatic summarization
        max_consecutive_auto_reply=2,
        code_execution_config=False,
        llm_config={
            "config_list": [{"model": "gpt-4", "api_key": openai_key}]
        }
    )

    # Define search queries
    queries = [
        "Bank of England current interest rate",
        "UK inflation rate ONS latest",
        "UK unemployment rate ONS",
        "UK GDP growth rate latest",
        "Bank of England monetary policy update"
    ]
    
    # Collect search results
    print("Searching for economic indicators...")
    results = []
    for query in queries:
        print(f"\nSearching for: {query}")
        # First get raw search results
        raw_results = search_agent.search_duckduckgo(query)
        print(f"Found {len(raw_results)} raw results")
        if raw_results:
            print("First result:", raw_results[0] if raw_results else "No results")
        
        # Then get summarized results
        search_result = search_agent.search_and_summarize(query)
        print(f"Search result length: {len(search_result) if search_result else 0}")
        results.append(f"Results for {query}:\n{search_result}")
    
    if not results:
        print("No results were collected. Exiting...")
        return
    
    # Combine all results
    combined_results = "\n\n".join(results)
    print(f"\nTotal combined results length: {len(combined_results)}")
    
    # Create analysis prompt
    analysis_prompt = f"""Based on the following economic data, provide a comprehensive analysis 
    of the UK economic situation and its implications for banking products and investment decisions:

    {combined_results}

    Please structure your analysis with clear sections for:
    1. Current Economic Indicators
    2. Economic Outlook
    3. Implications for Banking Products
    4. Investment Recommendations
    """

    # Get final analysis through chat
    chat_result = user_proxy.initiate_chat(
        search_agent,
        message=analysis_prompt
    )

    print("\nFinal Economic Analysis:")
    print(chat_result.summary)

if __name__ == "__main__":
    test_search_agent()    