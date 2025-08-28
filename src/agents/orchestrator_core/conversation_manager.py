
from typing import List, Dict, Any, Optional

from ...llm.llm_client import LLMClient # Adjust import path

class ConversationManager:
    """
    對話管理器，專門處理多輪對話相關的邏輯，包括歷史清理、問題釐清和元對話判斷。
    """

    def __init__(self, llm_client: LLMClient):
        """
        初始化對話管理器。

        Args:
            llm_client: LLM 客戶端，用於問題釐清和元對話的回應生成。
        """
        if not isinstance(llm_client, LLMClient):
            raise TypeError("llm_client must be an instance of LLMClient")
        self.llm_client = llm_client

    def sanitize_history(self, history: List[Dict[str, str]], max_items: int = 10) -> List[Dict[str, str]]:
        """
        清理前端傳入的對話歷史，僅保留必要欄位並限制長度。
        - 僅保留 role in {user, assistant}
        - 轉字串、去除空白；空內容移除
        - 僅保留最後 max_items 筆
        """
        cleaned: List[Dict[str, str]] = []
        for m in history:
            role = str(m.get("role", "")).lower()
            content = str(m.get("content", "")).strip()
            if not content:
                continue
            role = "user" if role == "user" else "assistant"
            cleaned.append({"role": role, "content": content})
        if len(cleaned) > 20:
            cleaned = cleaned[-20:]
        return cleaned

    def clarify_question_with_history(self, question: str, 
                                     history: List[Dict[str, str]]) -> str:
        """
        基於對話歷史，釐清當前問題，使其更具體、適合工具查詢。
        """
        clarification_messages: List[Dict[str, str]] = []
        clarification_messages.extend(history)
        clarification_messages.append({"role": "user", "content": question.strip()})
        clarification_messages.append({
            "role": "assistant", 
            "content": """請分析使用者的最後問題是否為獨立的新問題，還是與之前對話相關的延續問題。

            如果是獨立的新問題（如：詢問不同目的地、完全不同的主題），請直接輸出該問題，不要結合歷史資訊。

            如果是延續性問題（如：「那住宿呢？」、「費用大概多少？」），則可以結合脈絡重寫。

            請將使用者的最後問題重寫成一個最清楚、最具體、適合工具查詢的一句話。只輸出那一句話，不要多餘解釋。"""
        })
        
        clarified_question = self.llm_client.generate_chat_response(clarification_messages).strip()
        return clarified_question or question.strip()
    
    def handle_meta_conversation(self, complex_question: str, history: List[Dict[str, str]]) -> str:
        """
        處理元對話問題，直接透過 LLM 生成回應。
        """
        meta_messages: List[Dict[str, str]] = []
        meta_messages.extend(history)
        meta_messages.append({"role": "user", "content": complex_question.strip()})
        final_answer = self.llm_client.generate_chat_response(meta_messages)
        return final_answer
