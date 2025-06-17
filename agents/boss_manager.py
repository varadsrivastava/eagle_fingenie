# define boss manager human-in-the-loop as human proxy agent
from autogen import ConversableAgent

def create_boss_human_loop():
    human_proxy = ConversableAgent(
        "FinGenie_Boss_Manager",
        llm_config=False,  # no LLM used for human proxy
        human_input_mode="ALWAYS",  # always ask for human input
        is_termination_msg = lambda msg: msg["content"].lower() in ['quit', 'exit', 'bye']
    )

    return human_proxy