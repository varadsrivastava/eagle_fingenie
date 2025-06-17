import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import ConversableAgent
from utils.keys import openai_key, get_anthropic_key
from agents.relationship_manager import run_conversation_relationship_manager, create_relationship_manager
# from agents.customer_chatbot import run_conversation_customer_chatbot

# import macro economic analyst
from agents.macro_economic_analyst import run_conversation_macro_economic_analyst
from autogen import UserProxyAgent



def create_financial_advisor():

    financial_advisor_prompt = """You are a financial advisor. You will be provided with:
    1. The customer's profile
    2. The relationship manager's product recommendations
    3. A macro economic analysis of UK and global economic indicators
    
    Your role is to:
    1. Determine the risk appetite of the customer from the provided customer profile
    2. Examine the relationship manager's product recommendations for feasibility considering:
       - Customer's risk appetite
       - Bank financials
       - Current UK economic indicators (from macro analysis)
       - Global economic trends and their potential impact
    3. Recommend how to allocate the customer's savings among the final viable products
    4. Provide clear reasoning for your recommendations based on both customer profile and economic conditions
    """
    # Evaluates product viability and optimizes financial outcomes for the customer.



    # Define the customer chatbot agent
    financial_advisor = ConversableAgent(
        name="FinGenie_Financial_Advisor_Bot",
        system_message=financial_advisor_prompt,
        max_consecutive_auto_reply=1,
        human_input_mode="TERMINATE",
        # llm_config={
        #     "config_list": [{"model": "gpt-4o", "temperature": 0.7, "api_key": openai_key}]
        # },
        llm_config={
        "api_type": "anthropic",
        "model": "claude-3-5-sonnet-latest",
        "api_key": get_anthropic_key(),
        "temperature": 0.9,  # Adjust as needed
        # "max_tokens": 4096  # Adjust token limit
        },
        # terminate the conversation 
        # is_termination_msg=lambda x: x["content"].rfind("{") != -1
    )

    return financial_advisor

def run_conversation_financial_advisor():

    last_msg_summary = run_conversation_relationship_manager()

    macroeconomic_analysis = run_conversation_macro_economic_analyst()

    relationship_manager = create_relationship_manager()

    financial_advisor = create_financial_advisor()



    result = relationship_manager.initiate_chat(
        financial_advisor,
        message=last_msg_summary + "\n\n Following is the result from macroeconomic analyst: \n\n" + macroeconomic_analysis,
        summary_method="last_msg"
    )


    return result.summary


if __name__ == "__main__":
    
    result = run_conversation_financial_advisor()
    # use human-in-the-loop to check/correct the final summary and then show it to the customer
    
    # show final summary to the customer in the way it should be presented
    # run_conversation_customer_chatbot(message=result)

    
    print(result)
