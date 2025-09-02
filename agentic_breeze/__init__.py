"""
Breeze Agent Framework - Smart Assistant Framework

A framework for building intelligent agents with planning, execution, and synthesis capabilities.
"""

__version__ = "1.0.0"
__author__ = "Breeze Agent Team"

# Main components
from .agents.orchestrator import Orchestrator
from .llm.llm_client import LLMConnector
from .prompts.prompt_manager import PromptManager
from .registry.tool_registry import ToolRegistry

# Core components
from .agents.orchestrator_core.planning_manager import PlanningManager
from .agents.orchestrator_core.tool_executor import ToolExecutor
from .agents.orchestrator_core.query_rewriter import QueryRewriter
from .agents.orchestrator_core.conversation_manager import ConversationManager
from .agents.orchestrator_core.synthesis_generator import SynthesisGenerator

__all__ = [
    "Orchestrator",
    "LLMConnector", 
    "PromptManager",
    "ToolRegistry",
    "PlanningManager",
    "ToolExecutor",
    "QueryRewriter",
    "ConversationManager",
    "SynthesisGenerator"
]