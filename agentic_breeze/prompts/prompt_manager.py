
import json
from typing import List, Dict, Any
import os


class PromptManager:
    """
    提示詞管理器，統一管理各種提示詞模板。
    
    這個類別從原本的 PromptComposer 提取出來，
    專門負責提示詞的組合和管理，提供更清晰的職責分離。
    """
    
    def __init__(self, config_path: str = "prompt.json"):
        """
        初始化提示詞管理器。
        
        Args:
            config_path: str, 提示詞配置檔案的路徑，相對於 src/prompts 目錄。
        
        Exceptions:
            FileNotFoundError: 提示詞配置檔案不存在。
        """
        self.config_path = os.path.join(os.path.dirname(__file__), config_path)
        self._load_prompts()

    def _load_prompts(self):
        """
        從配置檔案載入提示詞。
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Prompt configuration file not found at {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        self.expert_prompts = config_data.get("expert_prompts", {})
        self.common_prompts = config_data.get("common_prompts", [])
    
    def build_planning_prompt(self, question: str, tool_schemas: List[Any]) -> str:
        """
        構建規劃階段的提示詞。
        
        Args:
            question: str, 使用者問題。
            tool_schemas: List[Any], 可用工具的 schema 列表。
            
        Returns:
            str: 規劃提示詞。
            
        Examples:
            >>> prompt_manager = PromptManager()
            >>> prompt = prompt_manager.build_planning_prompt("今天天氣如何？", tool_schemas)
            >>> print(prompt)
            "你是AI助理，負責分析使用者問題並選擇最合適的工具組合..."
        """
        tools_description = "\n".join([
            f"- {schema['function']['name']}: {schema['function']['description']}"
            for schema in tool_schemas
        ])

        prompt = f"""
        你是AI助理，負責分析使用者問題並選擇最合適的工具組合。

        === 可用工具 ===
        {tools_description}

        === 使用者問題 ===
        {question}

        === 工具呼叫規則 ===
        依據使用者問題判斷，如果需要調用多個工具，使用 planner規劃方式，planner非工具名稱，而是會回傳一個包含工具名稱和參數的列表： 
        
        planner(plan=[
            {{"tool_name": "第1個工具", "parameters": {{參數}}}},
            {{"tool_name": "第2個工具", "parameters": {{參數}}}}
        ])
        """

        return prompt
    
    def build_query_rewriter_prompt(self, history: List[Dict[str, str]], query: str) -> str:
        """
        構建查詢重寫的提示詞。
        
        Args:
            history: List[Dict[str, str]], 對話歷史。
            query: str, 原始查詢。
            
        Returns:
            str: 查詢重寫提示詞。
            
        Examples:
            >>> prompt_manager = PromptManager()
            >>> history = [{"role": "user", "content": "今天天氣如何？"}]
            >>> prompt = prompt_manager.build_query_rewriter_prompt(history, "那明天呢？")
            >>> print(prompt)
            "你是一位專業的問句重寫助理..."
        """
        history_text = self._history_to_text(history) if history else "無對話歷史"
        
        prompt = f"""你是一位專業的問句重寫助理。請根據對話歷史，將使用者的問句重寫得更清楚、更具體。

        對話歷史：
        {history_text}

        原始問句：{query}

        請重寫這個問句，使其：
        1. 更加清楚明確
        2. 包含必要的背景資訊
        3. 適合進行查詢和工具呼叫
        4. 保持原意不變

        只輸出重寫後的問句，不要加任何解釋："""
        return prompt
    
    def build_synthesis_prompt(self, 
                               original_question: str, 
                               execution_results: List[str],
                               used_tools: List[str] = None) -> str:
        """
        構建綜合階段的提示詞。
        
        Args:
            original_question: str, 原始問題。
            execution_results: List[str], 工具執行結果列表。
            used_tools: List[str], 實際執行過的工具名稱列表 (用於組合專業提示詞)。
            
        Returns:
            str: 綜合階段提示詞。
            
        Examples:
            >>> prompt_manager = PromptManager()
            >>> results = ["台北市晴朗，25°C"]
            >>> prompt = prompt_manager.build_synthesis_prompt("今天天氣如何？", results)
            >>> print(prompt)
            "你是AI助理，負責根據提供的資訊綜合回答使用者問題..."
            
            >>> prompt_manager = PromptManager()# 多工具整合範例
            >>> results = ["高鐵票價700元", "台中晴朗23-28°C"]
            >>> prompt = prompt_manager.build_synthesis_prompt("台中旅遊規劃", results)
        """
        if used_tools is None:
            used_tools = []

        # 組合執行結果
        results_text = "\n".join([
            f"{i+1}. {result}"
            for i, result in enumerate(execution_results)
        ])
        
        # 組合專業提示詞
        expert_synthesis_instructions = self._compose_expert_synthesis_prompt(used_tools)
        
        return f"""
        {expert_synthesis_instructions}

        原始問題：{original_question}

        背景資料：
        {results_text}

        請根據以上背景資料，生成一個完整、親切的答案。
        """
    
    def _compose_expert_synthesis_prompt(self, used_tools: List[str]) -> str:
        """
        通用提示詞組合專業綜合提示詞。
        
        Args:
            used_tools: List[str], 實際執行過的工具名稱列表
            
        Returns:
            str: 組合後的專業提示詞。
        """
        prompt_parts = []
        prompt_parts.extend(self.common_prompts)
        
        if len(used_tools) > 1:
            prompt_parts.append("你需要整合多個工具的資訊，提供一個完整、親切的完整回答。")
            prompt_parts.append("")
            
        for tool in used_tools:
            if tool in self.expert_prompts:
                prompt_parts.append(self.expert_prompts[tool])
                prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def _history_to_text(self, history: List[Dict[str, str]]) -> str:
        """
        將對話歷史轉換為文字格式。
        
        Args:
            history: List[Dict[str, str]], 對話歷史記錄。
            
        Returns:
            str: 格式化的對話歷史文字。
            
        Examples:
            >>> prompt_manager = PromptManager()
            >>> history = [{"role": "user", "content": "你好"}, {"role": "assistant", "content": "您好"}]
            >>> text = prompt_manager._history_to_text(history)
            >>> print(text)
            "使用者: 你好\\n助理: 您好"
        """
        lines: List[str] = []
        role_map = {"user": "使用者", "assistant": "助理"}
        for m in history:
            role = role_map.get(m.get("role", ""), "助理")
            content = m.get("content", "").strip()
            if content:
                lines.append(f"{role}: {content}")
        return "\n".join(lines)
