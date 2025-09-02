from typing import List, Dict, Any, Callable
import json

# 錯誤訊息前綴，提供一致且可辨識的錯誤格式。
ERROR_PREFIX = "[ToolError]"


class ToolRegistry:
    """
    工具註冊表（Tool Registry）。

    本類別提供工具的註冊、查詢與執行功能，並可輸出符合 OpenAI
    function calling（tools schema）之工具定義，以供上層模組（例如
    `PlanningManager` 與 `LLMConnector`）進行規劃與推理。

    使用情境：
        - `PlanningManager` 透過 `get_llm_tool_schemas()` 取得可用工具 schema，
          交給 LLM 作為可呼叫之函式定義。
        - `ToolExecutor` 透過 `execute_tool()` 依計畫項目執行對應工具。

    使用範例：
        1) 註冊自訂工具並輸出 tools schema：
            >>> registry = ToolRegistry()
            >>> registry.register_tool(
            ...     name="add",
            ...     description="加總兩個整數並回傳字串結果",
            ...     parameters={
            ...         "type": "object",
            ...         "properties": {
            ...             "a": {"type": "integer"},
            ...             "b": {"type": "integer"}
            ...         },
            ...         "required": ["a", "b"],
            ...         "additionalProperties": False,
            ...     },
            ...     handler=lambda a, b: str(a + b),
            ... )
            >>> tools = registry.get_llm_tool_schemas()
            >>> isinstance(tools, list) and tools[0]["type"] == "function"
            True

        2) 直接執行已註冊工具：
            >>> registry.execute_tool("add", a=1, b=2)
            '3'

    內部資料結構：
        self._registry: Dict[str, Dict[str, Any]]
            - key：工具名稱（str）
            - value：包含下列鍵值
                - "schema": Dict[str, Any]
                    符合 OpenAI tools 規範之函式定義
                - "handler": Callable[..., Any]
                    實際執行該工具的函式

        結構範例（示意）：
            {
                "echo": {
                    "schema": {
                        "type": "function",
                        "function": {
                            "name": "echo",
                            "description": "回傳輸入文字（教學用範例）",
                            "parameters": {
                                "type": "object",
                                "properties": {"text": {"type": "string"}},
                                "required": ["text"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "handler": <callable>
                },
                "add": {
                    "schema": { ... },
                    "handler": <callable>
                }
            }

    內建示例工具：
        （無內建示例工具。請於系統啟動時或模組載入時主動註冊所需工具。）
    """

    def __init__(self) -> None:
        self._registry: Dict[str, Dict[str, Any]] = {}

    def register_tool(
        self,
        *,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        """
        註冊工具。

        於登錄表中新增一個可供 LLM 呼叫與系統執行的工具定義。工具名稱
        應具唯一性；若同名將覆蓋原有設定。

        參數：
            name：工具名稱（唯一）。
            description：工具用途與行為的說明，供 LLM 判斷何時調用。
            parameters：JSON Schema 物件，對應 OpenAI function calling 的
                `parameters` 欄位，用於描述參數型態與必填欄位。
            handler：實際執行函式，呼叫簽名為 `handler(**kwargs)`，需與
                `parameters` 定義相容。

        例外：
            ValueError：當 name 為空或 handler 不可呼叫時拋出。
        """
        if not name or not isinstance(name, str):
            raise ValueError("tool name 不可為空，且需為字串。")
        if not callable(handler):
            raise ValueError("handler 必須可呼叫。")

        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        }

        self._registry[name] = {"schema": schema, "handler": handler}

    def get_llm_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        取得工具 schema 列表。

        回傳符合 OpenAI function calling 規格之工具定義，用以作為 LLM 的
        `tools` 參數。每一個元素皆為 `{"type": "function", "function": {...}}`。

        傳回：
            List[Dict[str, Any]]：可用工具的 schema 清單。
        """
        return [entry["schema"] for entry in self._registry.values()]

    # 設計說明（參數位置/關鍵字限制）：
    # - '/'：將 tool_name 設為「位置限定參數」，避免與工具本身參數同名而混淆，並提升可讀性（第一個位置就是工具名）。
    # - '*'：其後僅允許「關鍵字限定參數」；框架旗標（如 raise_on_error）需以名稱傳遞。
    #   工具的實際參數一律收在 **kwargs，原樣轉交 handler，明確區分框架層與工具層參數。
    def execute_tool(self, tool_name: str, /, *, raise_on_error: bool = False, **kwargs: Any) -> str:
        """
        執行工具。

        依據工具名稱查找對應處理函式，並以關鍵字參數方式傳入執行。若執行
        成功且回傳值為非字串，將嘗試以 JSON 進行序列化；失敗時回傳具固定
        前綴之錯誤訊息，或於嚴格模式下拋出例外。

        參數：
            tool_name：工具名稱。
            raise_on_error：為 True 時，遇到錯誤即拋出例外；為 False 時回傳
                具固定前綴之錯誤字串（預設 False，以維持相容）。
            **kwargs：傳遞給工具處理函式的參數，應符合工具 schema 定義。

        傳回：
            str：工具回傳內容之字串表示。

        注意事項：
            - 本實作著重於最小可用，未內建 JSON Schema 驗證。如需嚴格驗證，
              可於未來引入 `jsonschema` 或 Pydantic。
            - 保留最後一道通用例外攔截，目的在於提供穩定回傳格式與防止流程
              中斷；必要時可透過 raise_on_error 開啟嚴格模式。
        """
        entry = self._registry.get(tool_name)
        if not entry:
            msg = f"{ERROR_PREFIX} 未註冊的工具: {tool_name}"
            if raise_on_error:
                raise KeyError(msg)
            return msg

        handler: Callable[..., Any] = entry["handler"]
        try:
            result = handler(**kwargs)
        except TypeError as e:
            # 常見於參數不符或缺少必填參數
            msg = f"{ERROR_PREFIX} 使用工具 '{tool_name}' 時參數錯誤: {e}"
            if raise_on_error:
                raise
            return msg
        except ValueError as e:
            # 若未來加入參數驗證（JSON Schema/Pydantic）
            msg = f"{ERROR_PREFIX} 使用工具 '{tool_name}' 時參數驗證失敗: {e}"
            if raise_on_error:
                raise
            return msg
        except Exception as e:
            # 最後保險攔截：提供穩定錯誤格式並避免流程中斷
            msg = f"{ERROR_PREFIX} 使用工具 '{tool_name}' 時執行例外: {e}"
            if raise_on_error:
                raise msg
            return msg

        if isinstance(result, str):
            return result

        try:
            if isinstance(result, (dict, list, int, float, bool)) or result is None:
                return json.dumps(result, ensure_ascii=False)
            # 對於非常規型別，改以 str() 以避免洩漏內部資訊
            return str(result)
        except Exception:
            # 序列化出錯時退回 str()，保證回傳文字格式
            return str(result)