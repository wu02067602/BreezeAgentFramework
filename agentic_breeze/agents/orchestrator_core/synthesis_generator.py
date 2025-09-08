from typing import List, Optional

from ...llm.llm_client import LLMConnector
from ...prompts.prompt_manager import PromptManager


class SynthesisGenerator:
    """
    綜合生成器，負責整合工具執行結果並生成最終回答。
    
    這個類別專門處理多個工具執行結果的整合和綜合，
    使用 LLM 生成符合使用者期望的完整回答。
    """
    
    def __init__(self, llm_client: LLMConnector, prompt_manager: PromptManager):
        """
        初始化綜合生成器。
        
        Args:
            llm_client: LLM 客戶端，用於生成綜合回答
            prompt_manager: 提示詞管理器，用於構建綜合提示詞
            
        Raises:
            TypeError: 如果參數類型不正確
        """
        if not isinstance(llm_client, LLMConnector):
            raise TypeError("llm_client must be an instance of LLMConnector")
        if not isinstance(prompt_manager, PromptManager):
            raise TypeError("prompt_manager must be an instance of PromptManager")
        
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
    
    def synthesize_result(self, 
                         original_question: str,
                         execution_results: List[str],
                         used_tools: Optional[List[str]] = None) -> str:
        """
        綜合工具執行結果並生成最終回答。
        
        Args:
            original_question: str, 原始使用者問題
            execution_results: List[str], 工具執行結果列表
            used_tools: Optional[List[str]], 實際執行過的工具名稱列表 (用於組合專業提示詞)。
            
        Returns:
            str: 綜合後的最終回答
            
        Raises:
            ValueError: 如果問題為空或結果列表為空
            RuntimeError: 如果綜合過程出現錯誤
            
        Examples:
            >>> generator = SynthesisGenerator(llm_client, prompt_manager)
            >>> results = ["台北市晴朗，氣溫25°C", "濕度60%"]
            >>> answer = generator.synthesize_result("今天天氣如何？", results, ["weather_tool"])
            >>> print(answer)
            "今天台北市天氣晴朗，氣溫25°C，濕度60%，是個舒適的好天氣。"
        """
        if not isinstance(original_question, str) or not original_question.strip():
            raise ValueError("original_question must be a non-empty string")
        
        if not isinstance(execution_results, list):
            raise ValueError("execution_results must be a list")
        
        # 建構綜合提示詞
        synthesis_prompt = self.prompt_manager.build_synthesis_prompt(
            original_question=original_question,
            execution_results=execution_results,
            used_tools=used_tools
        )
        
        final_answer = self.llm_client.single_query(synthesis_prompt)
        return final_answer

    def synthesize_result_stream(self, 
                                original_question: str,
                                execution_results: List[str],
                                used_tools: Optional[List[str]] = None):
        """
        綜合工具執行結果並生成串流回答。
        
        Args:
            original_question: str, 原始使用者問題
            execution_results: List[str], 工具執行結果列表
            used_tools: Optional[List[str]], 實際執行過的工具名稱列表 (用於組合專業提示詞)。
            
        Yields:
            串流回應內容
            
        Raises:
            ValueError: 如果問題為空或結果列表為空
            RuntimeError: 如果綜合過程出現錯誤
        """
        if not isinstance(original_question, str) or not original_question.strip():
            raise ValueError("original_question must be a non-empty string")
        
        if not isinstance(execution_results, list):
            raise ValueError("execution_results must be a list")
        
        # 建構綜合提示詞
        synthesis_prompt = self.prompt_manager.build_synthesis_prompt(
            original_question=original_question,
            execution_results=execution_results,
            used_tools=used_tools
        )
        
        # 使用串流方法
        stream = self.llm_client.single_query_stream(synthesis_prompt)
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            
