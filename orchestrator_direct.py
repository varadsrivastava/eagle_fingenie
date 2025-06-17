from agents.financial_advisor import run_conversation_financial_advisor
from agents.relationship_manager import create_relationship_manager
from agents.boss_manager import create_boss_human_loop
from agents.customer_chatbot import run_conversation_customer_chatbot

def run_conversation_boss_manager(result_summary):

    boss_manager = create_boss_human_loop()

    relationship_manager = create_relationship_manager()

    result = relationship_manager.initiate_chat(
        boss_manager,
        message=result_summary
    )

    return result



if __name__ == "__main__":

    result_summary = run_conversation_financial_advisor()
    # use human-in-the-loop to check/correct the final summary and then show it to the customer
    
    result = run_conversation_boss_manager(result_summary)

    # show final summary to the customer in the way it should be presented
    run_conversation_customer_chatbot(message=result.summary)