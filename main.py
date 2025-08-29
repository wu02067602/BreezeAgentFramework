import os
from dotenv import load_dotenv
load_dotenv()

import gradio as gr

from src.agents.orchestrator import Orchestrator
from src.llm.llm_client import LLMConnector
from src.prompts.prompt_manager import PromptManager
from src.agents.orchestrator_core.planning_manager import PlanningManager
from src.agents.orchestrator_core.tool_executor import ToolExecutor
from src.agents.orchestrator_core.query_rewriter import QueryRewriter
from src.agents.orchestrator_core.conversation_manager import ConversationManager
from src.agents.orchestrator_core.synthesis_generator import SynthesisGenerator
from src.registry.tool_registry import ToolRegistry

llm_connector = LLMConnector(
    api_key=os.getenv("LLM_API_KEY"),
    api_base_url=os.getenv("OPENAI_API_BASE_URL"),
    default_model=os.getenv("MODEL_NAME")
)
prompt_manager = PromptManager()
planning_manager = PlanningManager(
    llm_client=llm_connector,
    tool_registry=ToolRegistry(),
    prompt_manager=prompt_manager
)
tool_executor = ToolExecutor(
    tool_registry=ToolRegistry(),
)
query_rewriter = QueryRewriter(
    llm_client=llm_connector,
    prompt_manager=prompt_manager
)
conversation_manager = ConversationManager(
    llm_client=llm_connector
)
synthesis_generator = SynthesisGenerator(
    llm_client=llm_connector,
    prompt_manager=prompt_manager
)

orchestrator = Orchestrator(
    prompt_manager=prompt_manager,
    planning_manager=planning_manager,
    tool_executor=tool_executor,
    conversation_manager=conversation_manager,
    synthesis_generator=synthesis_generator,
    query_rewriter=query_rewriter
)

if __name__ == "__main__":
    def chat_interface(user_message, history):
        if not history:
            history = []
        
        # Gradio history format is List[List[str, str]] where inner list is [user_message, bot_message]
        # Our orchestrator expects List[Dict[str, str]]
        formatted_history = []
        for human, assistant in history:
            formatted_history.append({"role": "user", "content": human})
            formatted_history.append({"role": "assistant", "content": assistant})

        reply = orchestrator.aquery_with_history(user_message, formatted_history)
        
        # Return the bot reply and updated history in Gradio format
        return reply

    print("=== 啟動 Gradio 介面 ===")
    
    gr.ChatInterface(
        chat_interface,
        title="Breeze 智慧助理",
        description="與您的 Breeze 助理對話。輸入 'exit' 或 'quit' 結束對話。",
        examples=[
            ["推薦台灣珍珠奶茶手搖店三間"],
            ["台北夜市知名小吃"],
            ["規劃宜蘭週末旅行"],
        ]
    ).launch()
