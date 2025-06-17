import sys
import os
from utils.keys import openai_key
from autogen import GroupChat, GroupChatManager
from agents.customer_chatbot import create_customer_chatbot, create_human_proxy
from agents.relationship_manager import create_relationship_manager, create_rm_junior_analyst
from agents.financial_advisor import create_financial_advisor
from agents.boss_manager import create_boss_human_loop
from agents.macro_economic_analyst import create_macro_economic_analyst

def create_sequential_group_chat():
    # Create agents
    human_proxy = create_human_proxy()
    customer_chatbot = create_customer_chatbot()
    relationship_manager = create_relationship_manager()
    macro_analyst = create_macro_economic_analyst()
    financial_advisor = create_financial_advisor()
    boss_manager = create_boss_human_loop()

    # Custom speaker selection function to enforce sequence and handle context
    def select_next_speaker(
        current_speaker,
        messages,
        agent_states,
        **kwargs
    ):
        # Store context in agent_states
        if current_speaker and current_speaker.name == "FinGenie_Customer_Bot":
            # Get customer profile summary from the last message
            customer_summary = messages[-1]["content"]
            agent_states["customer_summary"] = customer_summary
            
            # Create junior analyst with the context
            analyst_to_rm_prompt = """Hi, I am the Relationship Manager's analyst. I will be providing you with the customer's profile, financial information and information of some products that might be relevant to the customer.

            User's profile provided by the customer chatbot: {reflection_summary1}

            Information of some products that might be relevant to the customer along with their sources: {input_context}
            """
            
            rm_junior_analyst = create_rm_junior_analyst(
                analyst_to_rm_prompt=analyst_to_rm_prompt,
                update_embeddings=False
            )
            
            # Retrieve relevant products
            input_context = rm_junior_analyst.retrieve_docs(
                problem=customer_summary,
                n_results=10,
                search_string=""
            )
            
            # Format the retrieved context
            product_info = []
            for doc, metadata in zip(input_context["documents"][0], input_context["metadatas"][0]):
                product_entry = f"""Information from {metadata}:
                {doc}
                """
                product_info.append(product_entry)
            formatted_products = "\n\n".join(product_info)
            
            # Store the formatted message for relationship manager
            agent_states["rm_context"] = analyst_to_rm_prompt.format(
                reflection_summary1=customer_summary,
                input_context=formatted_products
            )
            
            return rm_junior_analyst
        
        # Define the conversation flow
        flow = {
            "human_proxy": "FinGenie_Customer_Bot",
            "FinGenie_Customer_Bot": "Relationship_Manager",
            "Relationship_Manager": "FinGenie_Macro_Analyst",
            "FinGenie_Macro_Analyst": "FinGenie_Financial_Advisor_Bot",
            "FinGenie_Financial_Advisor_Bot": "FinGenie_Boss_Manager",
            "FinGenie_Boss_Manager": None
        }
        
        # Get the next speaker from the flow
        if current_speaker is None:
            return "human_proxy"
        
        next_speaker = flow.get(current_speaker.name)
        if next_speaker is None:
            return None
        
        # Find the agent with the matching name
        for agent in group_chat.agents:
            if agent.name == next_speaker:
                # If transitioning to RM, provide the context
                if next_speaker == "Relationship_Manager":
                    messages.append({
                        "role": "user",
                        "content": agent_states.get("rm_context", "")
                    })
                return agent
        
        return None

    # Define the group chat
    group_chat = GroupChat(
        agents=[human_proxy, customer_chatbot, relationship_manager, 
                macro_analyst, financial_advisor, boss_manager],
        messages=[],
        max_round=10,
        send_introductions=True,
        speaker_selection_method=select_next_speaker
    )

    # Create manager with custom speaker selection
    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config={"config_list": [{"model": "gpt-4", "api_key": openai_key}]},
    )

    # Start the conversation
    chat_result = customer_chatbot.initiate_chat(manager,
        message="""Hello! I'm here to help you with your financial goals. 
        Please tell me about your income, savings, and financial objectives.""",
        summary_method="reflection_with_llm",
        summary_prompt="""Provide a comprehensive summary of:
        1. Customer profile and requirements
        2. Product recommendations from the relationship manager
        3. Financial advisor's review
        4. Final approved recommendations and portfolio allocation
        """
    )

    return chat_result.summary

if __name__ == "__main__":
    final_summary = create_sequential_group_chat()
    print("\nFinal Summary of Recommendations:")
    print(final_summary)



# allowed_transitions = []

# chat_result = customer_chatbot.initiate_chat(
#         group_chat_manager,
#         summary_prompt="Summarize the details of the customer's profile including information about 
#         their income, savings, and goals. Do not add any introductory phrases.",
#         message="Hello, I'm here to help you with your financial goals and recommend you products that 
#         may suit you best."
#         )