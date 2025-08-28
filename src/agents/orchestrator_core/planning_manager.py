
from typing import List, Dict, Any, Optional

from ...llm.llm_client import LLMConnector
from ...registry.tool_registry import ToolRegistry
from ...prompts.prompt_manager import PromptManager

from .modle.execution_plan import ExecutionPlan, PlanItem


class PlanningManager:
    """
    規劃管理器，負責分析問題並制定執行計畫。
    
    這個類別專門處理複雜查詢的分析和工具選擇邏輯，
    與實際執行解耦，提供清晰的職責分離。
    """
    
    def __init__(self, llm_client: LLMConnector, tool_registry: ToolRegistry, prompt_manager: PromptManager):
        """
        初始化規劃管理器。
        
        Args:
            llm_client: LLM 客戶端，用於問題分析和計畫制定
            tool_registry: 工具註冊表，用於獲取可用工具列表
            prompt_manager: 提示詞管理器，用於構建提示詞
        """
        if not isinstance(llm_client, LLMConnector):
            raise TypeError("llm_client must be an instance of LLMClient")
        if not isinstance(tool_registry, ToolRegistry):
            raise TypeError("tool_registry must be an instance of ToolRegistry")
        if not isinstance(prompt_manager, PromptManager):
            raise TypeError("prompt_manager must be an instance of PromptManager")
        
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.prompt_manager = prompt_manager
    
    def plan_question(self, question: str, history: Optional[List[Dict[str, str]]] = None) -> ExecutionPlan:
        """
        分析問題並制定執行計畫。
        
        Args:
            question: 要分析的問題
            history: 對話歷史記錄
            
        Returns:
            ExecutionPlan: 包含工具調用列表的執行計畫
            
        Raises:
            ValueError: 如果問題為空或無效
            RuntimeError: 如果規劃過程出現錯誤
        """
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string")
        
        # 獲取可用的工具 schema
        tool_schemas = self.tool_registry.get_llm_tool_schemas()
        
        if not tool_schemas:
            # 如果沒有可用工具，返回空
            return ExecutionPlan(
                plan_items=[],
                description="沒有可用工具"
            )
        
        # 構建規劃提示詞
        planning_prompt = self.prompt_manager.build_planning_prompt(question, tool_schemas)
        
        # 構建訊息列表
        messages = [{"role": "system", "content": planning_prompt}]
        
        # 如果有歷史記錄，將其加入訊息
        if history:
            history_text = self.prompt_manager._history_to_text(history)
            messages.append({
                "role": "user", 
                "content": f"對話歷史：{history_text}\n\n注意：請仔細判斷當前問題是否為獨立問題。如果問題涉及完全不同的目的地或主題，請忽略歷史資訊，只根據當前問題選擇工具。\n\n當前問題：{question}"
            })
        else:
            messages.append({"role": "user", "content": f"注意：請仔細判斷當前問題是否為獨立問題。如果問題涉及完全不同的目的地或主題，請忽略歷史資訊，只根據當前問題選擇工具。\n\n當前問題：{question}"})
        
        # 使用 tool_assisted_query 制定執行計畫
        result = self.llm_client.tool_assisted_query(
            messages=messages,
            tools=tool_schemas
        )
        
        # 解析執行計畫
        plan_items = self._parse_execution_plan(result)
        
        return ExecutionPlan(
            plan_items=plan_items,
            description=f"制定了包含 {len(plan_items)} 個工具調用的執行計畫"
        )
    
    def _parse_execution_plan(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析 LLM 回應的執行計畫。
        
        Args:
            result: tool_assisted_query 的回應結果
            
        Returns:
            List[Dict[str, Any]]: 解析後的計畫項目列表
        """
        plan_items = []
        
        # 檢查是否有工具調用
        tool_calls = result.get("tool_calls")
        if tool_calls and isinstance(tool_calls, list):
            for tool_call in tool_calls:
                if hasattr(tool_call, 'function'):
                    plan_items.append(PlanItem(
                        tool_name=tool_call.function.name,
                        arguments=tool_call.function.arguments
                    ))
        
        return plan_items
    
