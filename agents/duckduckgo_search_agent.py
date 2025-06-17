import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from autogen import ConversableAgent
from utils.keys import openai_key

class DuckDuckGoSearchAgent(ConversableAgent):
    def __init__(self, name, system_message="", llm_config=None, **kwargs):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            **kwargs
        )
        
        # Register the search function
        self.register_function(
            function_map={
                "search_and_summarize": self.search_and_summarize
            }
        )
    
    def search_duckduckgo(self, query: str, max_results: int = 3) -> list:
        """
        Search DuckDuckGo and return results
        """
        try:
            print(f"Starting DuckDuckGo search for: {query}")
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                print(f"Search completed. Found {len(results)} results")
            return results if results else []
        except Exception as e:
            print(f"Error during DuckDuckGo search: {str(e)}")
            return []

    def fetch_webpage_content(self, url: str) -> str:
        """
        Fetch and parse webpage content
        """
        try:
            print(f"Fetching content from: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            content_length = len(text[:4000])
            print(f"Successfully fetched and cleaned content. Length: {content_length}")
            return text[:4000]  # Limit content length
        except Exception as e:
            print(f"Error fetching webpage {url}: {str(e)}")
            # If it's a Bank of England URL that failed, try to extract info from the search result
            if "bankofengland.co.uk" in url and hasattr(self, '_current_result'):
                print("Extracting information from search result instead")
                return f"Title: {self._current_result.get('title', '')}\nSummary: {self._current_result.get('body', '')}"
            return ""

    def search_and_summarize(self, query: str) -> str:
        """
        Search DuckDuckGo, fetch webpage content, and return a summary
        """
        # Search DuckDuckGo
        search_results = self.search_duckduckgo(query)
        print(f"Got {len(search_results)} search results")
        
        if not search_results:
            return f"No results found for query: {query}"
        
        # Collect content from top results
        all_content = []
        for i, result in enumerate(search_results):
            print(f"\nProcessing result {i+1}/{len(search_results)}")
            # Store current result for potential fallback
            self._current_result = result
            link = result.get('href') or result.get('url')
            if link:
                print(f"Found link: {link}")
                content = self.fetch_webpage_content(link)
                if content:
                    # For Bank of England results, also include the search result summary
                    if "bankofengland.co.uk" in link:
                        content = f"Title: {result.get('title', '')}\nSummary: {result.get('body', '')}\n\nDetailed Content:\n{content}"
                    all_content.append(f"Source: {link}\n{content}")
            else:
                print(f"No link found in result: {result}")
                # If no link but we have title and body, use that
                if result.get('title') and result.get('body'):
                    content = f"Title: {result['title']}\nSummary: {result['body']}"
                    all_content.append(f"Source: Search Result\n{content}")
        
        if not all_content:
            print("No content could be fetched from any of the search results")
            return "Could not fetch content from search results."
        
        # Combine all content
        combined_content = "\n\n".join(all_content)
        print(f"Combined content length: {len(combined_content)}")
        
        # Use LLM to summarize content
        # summary_prompt = f"""Based on the following search results about '{query}', 
        # provide a clear and concise summary of the key information:
        
        # {combined_content}
        
        # Summary:"""
        
        # Create messages list for generate_reply
        messages = [{
            "role": "system",
            "content": """You are a precise and efficient summarizer. Extract and present key facts and figures from the search results.
            Focus on numerical data, dates, and concrete information. Present information in a clear, structured format."""
        }, {
            "role": "user",
            "content": f"""Summarize the key information from these search results about '{query}'.
            Focus on:
            1. Latest figures and statistics
            2. Recent dates and updates
            3. Official statements or policies
            4. Current trends or changes

            Search Results:
            {combined_content}"""
        }]
        
        try:
            # Get response from LLM
            response = self.generate_reply(messages=messages, sender=self)
            return response if isinstance(response, str) else response.get("content", "")
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            # Return the first search result as fallback
            if search_results:
                return f"Summary from first result: {search_results[0].get('body', 'No summary available')}"
            return "Could not generate summary."

def create_duckduckgo_search_agent(system_message="", llm_config=None):
    """
    Factory function to create a DuckDuckGoSearchAgent instance
    """
    if llm_config is None:
        llm_config = {
            "config_list": [
                {"model": "gpt-3.5-turbo", "api_key": openai_key},  # Primary model for summarization
                {"model": "gpt-4", "api_key": openai_key}  # Fallback for complex queries
            ]
        }
    
    agent = DuckDuckGoSearchAgent(
        name="DuckDuckGo_Search_Agent",
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER"
    )
    
    return agent 