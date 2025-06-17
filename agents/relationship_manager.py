# Define the relationship manager agent as a RAG agent which assesses the customer's financial situation, 
# eligibility and immediate life goals and suggest relevant Barclays UK banking products.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from autogen import ConversableAgent
import os
from utils.keys import openai_key
from utils import rm_data_preprocessing 
from agents.rm_junior_analyst import MyRetrieveUserProxyAgent
from agents.customer_chatbot import run_conversation_customer_chatbot


def create_relationship_manager():
    rm_system_prompt = """You are a Barclays UK Relationship Manager. Your role is to:
    1. Analyze provided customer profile, financial information, goals and other information to assess customer's eligiblity for banking products as well as recommend suitable banking products.
    2. Provide relevant details of the rates, fees and other relevant information for the recommended products.
    3. Provide clear explanations for your recommendations.
    
This information will be further fed into a Financial Advisor Agent to generate a financial plan 
and ensure that the relationship manager's recommendations align with the customer's financial 
health and broader macro-economic conditions of the UK.
"""

       
    relationship_manager = ConversableAgent(
            name="Relationship_Manager",
            system_message=rm_system_prompt,
            llm_config={
                "config_list": [{"model": "gpt-4o", "temperature": 0.7, "api_key": openai_key}]
            }
            # Alternative: Use Anthropic's Claude (uncomment and set ANTHROPIC_API_KEY)
            # llm_config={
            # "api_type": "anthropic",
            # "model": "claude-3-5-sonnet-latest",
            # "api_key": get_anthropic_key(),
            # "temperature": 0.9,
            # },
        )
    
    return relationship_manager 





def create_rm_junior_analyst(analyst_to_rm_prompt: str, update_embeddings: bool = False):

    # Update embedding space if True
    if update_embeddings:
        # run main of rm_data_preprocessing.py to update the database
        rm_data_preprocessing.main()
        # docs_paths = scraper.get_site_structure()

    # Then create the RAG agent with the same configuration
    rag_agent = MyRetrieveUserProxyAgent(
        name="FinGenie_Junior_Analyst_Agent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3,
        retrieve_config={
            "task": "banking_products",
            "customized_prompt":analyst_to_rm_prompt,
            "chunk_token_size": 2000,
            "model": "gpt-4o",
            # "vector_db": "chroma",
            # "client": None,
            # "db_path": "F:/xx/xx/fingenie/data/chromadb",
            # "collection_name": "barclays_products",
            # "embedding_function": embedding_function,
            # "get_or_create": True
        },
        code_execution_config={"use_docker": False}
    )

    return rag_agent

# Non-RAG agent for comparison
# nonrag_agent = ConversableAgent(
#             name="Barclays_NonRAG_Agent",
#             # system_message=instruction,
#             llm_config={
#                 "config_list": [{"model": "gpt-4", "temperature": 0.7, "api_key": openai_key}]
#             }
#         )


def define_input_msg_to_relationship_manager(reflection_summary1: str, query_to_analyst: str):

    analyst_to_rm_prompt = """Hi, I am the Relationship Manager's analyst. I will be providing you with the customer's profile, financial information and information of some products that might be relevant to the customer.

    User's profile provided by the customer chatbot:\n {reflection_summary1}

    Information of some products that might be relevant to the customer along with their sources:\n {input_context}
    """

    rm_junior_analyst = create_rm_junior_analyst(analyst_to_rm_prompt)

    # Retrieve products information
    input_context = rm_junior_analyst.retrieve_docs(
                    problem=query_to_analyst, 
                    n_results=10, 
                    search_string=""
                   )
    
    # print(input_context.keys())
    # print(input_context["ids"][0][0])
    # print(input_context["documents"][0][0][:100])
    # print(input_context["metadatas"][0][0])

    # loop through the metadata and corresponding document in input_context to generate the analyst_to_rm_prompt
    # Initialize an empty list to store formatted product information
    product_info = []

    # Loop through each document and its metadata
    for doc, metadata in zip(input_context["documents"][0], input_context["metadatas"][0]):
        # Format the product information with metadata source
        product_entry = f"""Information from {metadata}:
    {doc}
    """
        product_info.append(product_entry)

    # Join all product information with line breaks
    formatted_products = "\n\n".join(product_info)

    # Create the analyst to RM prompt template
    analyst_to_rm_prompt = analyst_to_rm_prompt.format(reflection_summary1=reflection_summary1, input_context=formatted_products)


    return analyst_to_rm_prompt, rm_junior_analyst


def run_conversation_relationship_manager():

    # get the customer profile from the customer chatbot
    reflection_summary1 = run_conversation_customer_chatbot()

    # reset the assistant. Always reset the assistant before starting a new conversation.
    relationship_manager = create_relationship_manager()

    # convert the reflection_summary1 to a proper query that can be used by the RAG agent
    # create proxy chat with a user which gives as input the reflection_summary1
    human_proxy = ConversableAgent(
        "Relationship_Manager_Mind",
        llm_config=False,  # no LLM used for human proxy
        human_input_mode="ALWAYS",
        is_termination_msg = lambda msg: msg["content"].lower() in ['quit', 'exit', 'bye']
    )
    chat_result = human_proxy.initiate_chat(
        relationship_manager,
        message="""From the below provided summary of the customer profile, output only the below:
        1. Customer's goals and objectives (whether short term or long term)
        2. Assess the high level product requirements of the customer (like mortgage, savings account, credit card, insurance, investment account, loan, pension, wealth management etc.).
        Your output as it is will be sent to the RAG agent to extract specific products that are relevant to the customer. Do not add any other text or comments.
        Reflection summary from customer chatbot: \n""" + reflection_summary1
    )

    query_to_analyst = chat_result.summary
    print("Query to analyst: ", query_to_analyst)


    # get the analyst_to_rm_prompt and rm_junior_analyst
    analyst_to_rm_prompt, rm_junior_analyst = define_input_msg_to_relationship_manager(reflection_summary1, query_to_analyst)

    chat_result =rm_junior_analyst.initiate_chat(
        relationship_manager,
        # problem=cust_profile,
        # message=rag_agent.message_generator,
        message=analyst_to_rm_prompt,
        summary_method="last_msg",
        # search_string="banking products financial advice"
        silent=True
    )

    return chat_result.summary



if __name__ == "__main__":
    result = run_conversation_relationship_manager()
    print(result)



