# Use autogen to create a customer chatbot that handles user queries to gather income, savings, and life goals.

from autogen import ConversableAgent
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# openai_key = os.environ.get("OPENAI_API_KEY")
from utils.keys import openai_key, get_anthropic_key


# define human proxy agent
def create_human_proxy():
    class CustomHumanProxy(ConversableAgent):
        def get_human_input(self, prompt: str) -> str:
            # Get the last message from the conversation history
            if hasattr(self, 'chat_history') and self.chat_history:
                last_message = self.chat_history[-1]
                if last_message['role'] == 'assistant':
                    prompt = f"{last_message['content']}\n\n{prompt}"
            return super().get_human_input(prompt)

    human_proxy = CustomHumanProxy(
        name="human_proxy",
        llm_config=False,  # no LLM used for human proxy
        human_input_mode="ALWAYS",  # always ask for human input
        is_termination_msg=lambda msg: msg["content"].lower() in ['quit', 'exit', 'bye']
    )

    return human_proxy


# Define the customer chatbot agent
def create_customer_chatbot():
    customer_chatbot = ConversableAgent(
    name="FinGenie_Customer_Bot",
    system_message="""You are a friendly customer chatbot. Your goal is to gather information about the user's:
    - Annual income
    - Current savings
    - Life goals and financial objectives
    - Any other information that is relevant to the customer's profile like their age, marital status, or existing bank accounts or investments.
    
    Ask questions one at a time and be empathetic in your responses. 
    After gathering all information, say: 
    Thank you for your time. I will now pass this information to my relationship manager to suggest you some products.""",
    # llm_config={
    #     "config_list": [{"model": "gpt-4o", "temperature": 0.9, "api_key": openai_key}]
    # },
        llm_config={
        "api_type": "anthropic",
        "model": "claude-3-5-sonnet-latest",
        "api_key": get_anthropic_key(),
        "temperature": 0.9,  # Adjust as needed
        # "max_tokens": 4096  # Adjust token limit
    },
    is_termination_msg = lambda msg: "relationship manager" in msg["content"].lower()
    )

    return customer_chatbot


def run_conversation_customer_chatbot(message="Hello, I'm here to help you with your financial goals and recommend you products that may suit you best."):
    customer_chatbot = create_customer_chatbot()
    human_proxy = create_human_proxy()
    result = customer_chatbot.initiate_chat(
        human_proxy,
        summary_prompt="Summarize the details of the customer's profile including information about their income, savings, and goals. Do not add any introductory phrases.",
        summary_method="reflection_with_llm",
        message=message
    )

    print(result.summary["content"])
    return result.summary["content"]




if __name__ == "__main__":

    result = run_conversation_customer_chatbot()
    print(result)

