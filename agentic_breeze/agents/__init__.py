
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class ReasoningStep:
    """推理步驟的資料結構"""
    step_type: str  # "planning", "execution", "synthesis"
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    error: Optional[str] = None
    raw_tool_result: Optional[Any] = None

@dataclass
class ExecutionPlan:
    """執行計畫的資料結構"""
    plan_items: List[Dict[str, Any]]
    description: str = ""
