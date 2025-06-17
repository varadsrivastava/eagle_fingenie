import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import ConversableAgent
from utils.keys import openai_key
from agents.relationship_manager import run_conversation_relationship_manager, create_relationship_manager
from autogen.agentchat.contrib.web_surfer import WebSurferAgent
# from agents.customer_chatbot import run_conversation_customer_chatbot




def create_financial_advisor():
    financial_advisor_prompt = """You are a financial advisor. You will be provided with the customer's profile and the relationship manager's product recommendations. 
    Your role is to:
    1. Determine the risk appetite of the customer from the provided customer profile.
    2. Examine the relationship manager's product recommendations for feasibility considering the customer's risk appetite, bank financials and global as well as UK specific economic trends. 
    3. Recommend how to allocate the customer's savings among the final viable products.
    """
    # Evaluates product viability and optimizes financial outcomes for the customer.



    # Define the customer chatbot agent
    financial_advisor = ConversableAgent(
        name="FinGenie_Financial_Advisor_Bot",
        system_message=financial_advisor_prompt,
        max_consecutive_auto_reply=1,
        human_input_mode="TERMINATE",
        llm_config={
            "config_list": [{"model": "gpt-4", "temperature": 0.7, "api_key": openai_key}]
        },
        # terminate the conversation 
        # is_termination_msg=lambda x: x["content"].rfind("{") != -1
    )

    return financial_advisor

def run_conversation_financial_advisor():

    last_msg_summary = run_conversation_relationship_manager()

    relationship_manager = create_relationship_manager()

    financial_advisor = create_financial_advisor()

    result = relationship_manager.initiate_chat(
        financial_advisor,
        message=last_msg_summary,
        summary_method="last_msg"
    )

    return result.summary


if __name__ == "__main__":
    
    result = run_conversation_financial_advisor()
    # use human-in-the-loop to check/correct the final summary and then show it to the customer
    
    # show final summary to the customer in the way it should be presented
    # run_conversation_customer_chatbot(message=result)

    
    print(result)
