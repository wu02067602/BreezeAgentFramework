from typing import List, Dict, Any
from pydantic import BaseModel, Field

class PlannerArgs(BaseModel):
    """多工具規劃器參數"""
    plan: List[Dict[str, Any]] = Field(..., description="多工具執行計畫，包含多個工具調用。格式：[{'tool_name': '工具名', 'parameters': {參數}}]")

class PlannerTool:
    """多工具規劃器 - 用於統一調度多個工具"""

    def __init__(self):
        self.name: str = "planner"
        self.description: str = "多工具規劃器，用於同時調用多個工具以提供綜合性的回答。適用於需要多種資訊的複合查詢。"
        self.args_schema = PlannerArgs.model_json_schema()

    def run(self, **kwargs) -> str:
        """規劃器不直接執行，只負責提供 plan 參數"""
        return "Planner tool should not be executed directly. Plan should be extracted by _parse_execution_plan."