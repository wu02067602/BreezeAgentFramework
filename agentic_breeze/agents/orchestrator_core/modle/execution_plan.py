from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class PlanItem:
    """
    執行計畫的單一步驟。

    屬性:
        - tool_name (str): 工具名稱。
        - arguments (Dict[str, Any]): 工具的參數。

    使用範例:
        >>> PlanItem(tool_name="weather", arguments={"location":"臺北市"})
    """
    tool_name: str
    arguments: Dict[str, Any]

@dataclass
class ExecutionPlan:
    """
    執行計畫。用於記錄並描述多個步驟的序列。

    屬性:
        - plan_items (List[PlanItem]): 執行計畫的步驟。
        - description (str): 執行計畫的描述。

    使用範例:
        >>> steps = [PlanItem(tool_name="wiki", arguments={"query":"台灣"})]
        >>> ExecutionPlan(plan_items=steps, description="資訊檢索與彙整")
    """
    plan_items: List[PlanItem]
    description: str
