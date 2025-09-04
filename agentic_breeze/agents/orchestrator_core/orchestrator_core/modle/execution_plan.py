from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class PlanItem:
    """
    執行計畫的步驟。

    Attributes:
        - tool_name: str, 工具名稱。
        - arguments: Dict[str, Any], 工具的參數。 
    """
    tool_name: str
    arguments: Dict[str, Any]

@dataclass
class ExecutionPlan:
    """
    執行計畫。用於記錄執行計畫的步驟。

    Attributes:
        - plan_items: List[Dict[str, Any]], 執行計畫的步驟。
        - description: str, 執行計畫的描述。
    """
    plan_items: List[PlanItem]
    description: str
