
from typing import List, Dict, Any, Optional

from ..prompts.prompt_manager import PromptManager
from .orchestrator_core.planning_manager import PlanningManager
from .orchestrator_core.tool_executor import ToolExecutor
from .orchestrator_core.query_rewriter import QueryRewriter
from .orchestrator_core.conversation_manager import ConversationManager
from .orchestrator_core.synthesis_generator import SynthesisGenerator

class Orchestrator:
    """
    總指揮代理。
    
    這個類別負責初始化所有核心組件，並將外部請求委託給適當的管理器處理。
    """
    
    def __init__(self, 
                 prompt_manager: PromptManager, 
                 planning_manager: PlanningManager, 
                 tool_executor: ToolExecutor, 
                 conversation_manager: ConversationManager, 
                 synthesis_generator: SynthesisGenerator,
                 query_rewriter: QueryRewriter
                 ):
        """
        初始化總指揮代理。
        
        Args:
            prompt_manager: 提示管理器。
            planning_manager: 規劃管理器。
            tool_executor: 工具執行器。
            conversation_manager: 對話管理器。
            synthesis_generator: 綜合生成器。
            query_rewriter: 問句重寫器。
        """
        # 初始化各個核心組件
        self.prompt_manager = prompt_manager # 提示管理器
        self.planning_manager = planning_manager # 規劃管理器
        self.tool_executor = tool_executor # 工具執行器
        self.conversation_manager = conversation_manager # 對話管理器
        self.synthesis_generator = synthesis_generator # 綜合生成器
        self.query_rewriter = query_rewriter # 問句重寫器

    def aquery(self, complex_question: str) -> str:
        """
        處理複雜查詢，執行完整的推理循環。

        Args:
            complex_question: 複雜查詢。

        Returns:
            回答。

        Examples:
            >>> orchestrator = Orchestrator(prompt_manager, planning_manager, tool_executor, conversation_manager, synthesis_generator)
            >>> orchestrator.aquery("今天天氣如何？")
            "今天天氣晴朗，氣溫攝氏25度。"

        Exceptions:
            ValueError: 複雜查詢為空。
            RuntimeError: 推理過程出現錯誤。
        """
        if not isinstance(complex_question, str):
            raise ValueError("complex_question must be a string")
        
        # 重寫問句
        rewritten_question = self.query_rewriter.rewrite_query(complex_question)
        # 計畫執行時需要的工具
        tools = self.planning_manager.plan_tools(rewritten_question)
        # 執行工具
        results = self.tool_executor.execute_tools(tools)
        # 綜合結果
        synthesis = self.synthesis_generator.synthesize_result(results)
        # 回傳結果
        return synthesis
    
    def aquery_with_history(self, 
                            complex_question: str, 
                            history: Optional[List[Dict[str, str]]] = None
                            ) -> str:
        """
        支援多輪對話歷史的查詢入口。

        Args:
            complex_question: 複雜查詢。
            history: 對話歷史。

        Returns:
            回答。

        Examples:
            >>> orchestrator = Orchestrator(prompt_manager, planning_manager, tool_executor, conversation_manager, synthesis_generator)
            >>> orchestrator.aquery_with_history("今天適合出門嗎？", [{"role": "user", "content": "今天天氣如何？"}, {"role": "assistant", "content": "今天天氣晴朗，氣溫攝氏25度。"}])
            "今天適合出門，氣溫攝氏25度。"

        Exceptions:
            ValueError: 複雜查詢為空。
            RuntimeError: 推理過程出現錯誤。
        """
        if not isinstance(complex_question, str):
            raise ValueError("complex_question must be a string")
        
        # 重寫問句
        rewritten_question = self.query_rewriter.rewrite_query(complex_question)
        # 組合對話歷史
        combined_history = self.conversation_manager.combine_history(history)
        # 計畫執行時需要的工具
        tools = self.planning_manager.plan_tools(combined_history)
        # 執行工具
        results = self.tool_executor.execute_tools(tools)
        # 綜合結果
        synthesis = self.synthesis_generator.synthesize_result(results)
        return synthesis
    
    def get_reasoning_history(self):
        """
        獲取完整的推理歷史記錄。

        Returns:
            推理歷史記錄。

        Examples:
            >>> orchestrator = Orchestrator(prompt_manager, planning_manager, tool_executor, conversation_manager, synthesis_generator)
            >>> orchestrator.get_reasoning_history()
            [ReasoningStep(step_type="planning", result="釐清後問題：今天天氣如何？"), ReasoningStep(step_type="tool_execution", result="今天天氣晴朗，氣溫攝氏25度。")]
        """
        return self.conversation_manager.get_reasoning_history()
    
    def clear_reasoning_history(self) -> None:
        """
        清空推理歷史記錄。

        Examples:
            >>> orchestrator = Orchestrator(prompt_manager, planning_manager, tool_executor, conversation_manager, synthesis_generator)
            >>> orchestrator.clear_reasoning_history()
            None
        """
        self.conversation_manager.clear_reasoning_history()
