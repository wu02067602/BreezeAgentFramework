import os
from dotenv import load_dotenv
load_dotenv()

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
synthesis_generator = SynthesisGenerator()

orchestrator = Orchestrator(
    prompt_manager=prompt_manager,
    planning_manager=planning_manager,
    tool_executor=tool_executor,
    conversation_manager=conversation_manager,
    synthesis_generator=synthesis_generator,
    query_rewriter=query_rewriter
)

orchestrator.aquery("請問台灣的總統是誰？")

print(orchestrator.get_reasoning_history())

orchestrator.clear_reasoning_history()

print(orchestrator.get_reasoning_history())