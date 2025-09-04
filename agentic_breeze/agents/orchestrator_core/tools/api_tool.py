import httpx
from typing import Dict, Any, Optional, Literal, Union
import json

class APIRequestTool:
    """
    一個可重複使用的 API 請求工具，用於 AI Agent 發送 HTTP 請求。
    支援 GET, POST, PUT, DELETE 方法，並處理查詢參數、標頭和多種請求主體類型。
    """
    def __init__(self, timeout: int = 30):
        """
        初始化 APIRequestTool。

        Args:
            timeout (int): 請求的超時時間（秒）。
        """
        self.client = httpx.Client(timeout=timeout, verify=False)

    def _send_request(self,
                             method: Literal["GET", "POST", "PUT", "DELETE"],
                             url: str,
                             query_params: Optional[Dict[str, Any]] = None,
                             headers: Optional[Dict[str, str]] = None,
                             json_data: Optional[Dict[str, Any]] = None,
                             form_data: Optional[Dict[str, Any]] = None,
                             raw_text: Optional[str] = None) -> httpx.Response:
        """
        內部方法：根據提供的參數準備並發送 HTTP 請求。
        處理不同的 Body Payload 類型 (JSON, form-data, raw text)。
        """
        request_kwargs = {
            "method": method,
            "url": url,
            "params": query_params,
            "headers": headers,
            "json": None,       # 預設為 None
            "data": None,       # 預設為 None
            "content": None     # 預設為 None
        }

        if json_data:
            request_kwargs["json"] = json_data
        elif form_data:
            request_kwargs["data"] = form_data
        elif raw_text:
            request_kwargs["content"] = raw_text

        response = self.client.request(**request_kwargs)
        return response

    def execute_request(self,
                              method: Literal["GET", "POST", "PUT", "DELETE"],
                              url: str,
                              query_params: Optional[Dict[str, Any]] = None,
                              headers: Optional[Dict[str, str]] = None,
                              json_data: Optional[Dict[str, Any]] = None,
                              form_data: Optional[Dict[str, Any]] = None,
                              raw_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Agent 調用的主要方法，用於發送 API 請求並處理回應。

        Args:
            method (Literal["GET", "POST", "PUT", "DELETE"]): HTTP 請求方法。
            url (str): 請求的 URL。
            query_params (Optional[Dict[str, Any]]): 查詢參數字典。
            headers (Optional[Dict[str, str]]): 請求標頭字典。
            json_data (Optional[Dict[str, Any]]): JSON 格式的請求主體。
            form_data (Optional[Dict[str, Any]]): Form-data 格式的請求主體。
            raw_text (Optional[str]): 原始文字格式的請求主體。

        Returns:
            Dict[str, Any]: 包含狀態碼、回應主體和潛在錯誤訊息的字典。
                            範例: {"status_code": 200, "response_body": {...}, "error": None}
                                  {"status_code": 404, "response_body": "Not Found", "error": "API request failed: 404 Not Found"}
        """
        try:
            response = self._send_request(method, url, query_params, headers, json_data, form_data, raw_text)
            response.raise_for_status() # 對於 4xx/5xx 狀態碼會拋出 httpx.HTTPStatusError

            # 回應處理
            try:
                response_body = response.json()
            except (json.JSONDecodeError, ValueError): # 如果不是 JSON 格式或有其他 ValueError，則回傳原始文字
                response_body = response.text

            return {
                "status_code": response.status_code,
                "response_body": response_body,
                "error": None
            }

        except httpx.TimeoutException as e:
            return {
                "status_code": None,
                "response_body": None,
                "error": f"API request timed out: {e}"
            }
        except httpx.HTTPStatusError as e:
            return {
                "status_code": e.response.status_code,
                "response_body": e.response.text,
                "error": f"API request failed: {e.response.status_code} {e.response.reason_phrase}"
            }
        except httpx.RequestError as e:
            return {
                "status_code": None,
                "response_body": None,
                "error": f"An error occurred while requesting {e.request.url!r}: {e}"
            }
        except Exception as e:
            return {
                "status_code": None,
                "response_body": None,
                "error": f"An unexpected error occurred: {e}"
            }
