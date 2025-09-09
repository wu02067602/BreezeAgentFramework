from typing import Dict, Any, Optional
from .api_tool import APIRequestTool

import os
import logging

_logger = logging.getLogger(__name__)

class CWAWeatherTool:
    """
    一個專門用於查詢中央氣象署 (CWA) 天氣資訊的工具。
    它使用 APIRequestTool 內部發送 HTTP 請求。
    """
    def __init__(self, api_request_tool: APIRequestTool):
        """
        初始化 CWAWeatherTool。

        參數:
            - api_request_tool (APIRequestTool): 內部使用的 HTTP 請求工具。

        返回:
            - None

        使用範例:
            >>> from agentic_breeze.agents.orchestrator_core.tools.api_tool import APIRequestTool
            >>> weather = CWAWeatherTool(api_request_tool=APIRequestTool())

        可能觸發的錯誤:
            - 無（錯誤通常在請求時回傳於結果字典）
        """
        self.api_request_tool = api_request_tool
        self.base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
        # 從環境變數獲取 CWA API Key
        self.cwa_api_key = os.getenv("CWA_API_KEY")

    def get_national_forecast(self, dataset_id: str = "F-C0032-001", location_name: Optional[str] = None) -> Dict[str, Any]:
        """
        獲取中央氣象署 (CWA) 的全國天氣預報資料，可選擇篩選特定地點。

        參數:
            - dataset_id (str): CWA 資料集 ID，預設為 "F-C0032-001"（36 小時天氣預報）。
            - location_name (Optional[str]): 指定地點名稱（若提供，僅回傳該地點）。

        返回:
            - Dict[str, Any]:
              - status (str): "success" 或 "error"。
              - forecast (Optional[List|Dict]): 成功時的預報資料（陣列或單一地點字典）。
              - message/error (Optional[str]): 錯誤時的訊息（為了相容性保留 error 鍵）。

        使用範例:
            >>> weather = CWAWeatherTool(api_request_tool=APIRequestTool())
            >>> out = weather.get_national_forecast(location_name="臺北市")
            >>> out.get("status") in {"success", "error"}
            True

        可能觸發的錯誤:
            - 缺少 CWA_API_KEY（以 {"status":"error","message":...} 回傳）
            - 上游 HTTP 錯誤或資料格式異常（以 error 結構回傳）
        """
        if not self.cwa_api_key:
            msg = "Missing environment variable CWA_API_KEY"
            _logger.error(msg)
            return {"status": "error", "message": msg, "error": msg}
        endpoint = f"{self.base_url}/{dataset_id}"
        query_params = {
            "Authorization": self.cwa_api_key,
            "format": "JSON"
        }
        headers = {
            "accept": "application/json"
        }

        response_data = self.api_request_tool.execute_request(
            method="GET",
            url=endpoint,
            query_params=query_params,
            headers=headers
        )

        if response_data["error"]:
            err = f"Failed to retrieve CWA forecast: {response_data['error']}"
            return {"status": "error", "message": err, "error": err}
        
        # 假設 CWA API 的回應結構，並進行簡化
        response_body = response_data["response_body"]
        if response_body and isinstance(response_body, dict) and "records" in response_body:
            # 這裡可以根據實際需求，對 response_body 進行更詳細的解析和提取
            # 例如，提取每個縣市的預報資訊，但為了簡潔，先回傳部分數據
            location_data = response_body["records"].get("location", [])
            simplified_forecast = []
            for loc in location_data:
                current_location_name = loc.get("locationName")
                # 如果指定了地點名稱，則只處理匹配的地點
                if location_name and current_location_name != location_name:
                    continue

                weather_elements = loc.get("weatherElement", [])
                # 簡化提取部分天氣元素，例如「天氣現象」和「最低/最高溫度」
                wx = next((e for e in weather_elements if e.get("elementName") == "Wx"), None)
                min_t = next((e for e in weather_elements if e.get("elementName") == "MinT"), None)
                max_t = next((e for e in weather_elements if e.get("elementName") == "MaxT"), None)

                current_forecast = {"locationName": current_location_name}
                if wx and wx.get("time"):
                    current_forecast["weather_phenomenon"] = wx["time"][0].get("parameter", {}).get("parameterName")
                if min_t and min_t.get("time"):
                    current_forecast["min_temperature"] = min_t["time"][0].get("parameter", {}).get("parameterName")
                if max_t and max_t.get("time"):
                    current_forecast["max_temperature"] = max_t["time"][0].get("parameter", {}).get("parameterName")
                simplified_forecast.append(current_forecast)
            
            if location_name and not simplified_forecast:
                return {"status": "error", "message": f"Could not find weather forecast for location '{location_name}'."}
            elif location_name and simplified_forecast:
                return {"status": "success", "forecast": simplified_forecast[0]} # 如果指定地點，只回傳第一個匹配項
            else:
                return {"status": "success", "forecast": simplified_forecast}
        else:
            msg = "CWA forecast data not available or unexpected response format."
            return {"status": "error", "message": msg, "error": msg}
