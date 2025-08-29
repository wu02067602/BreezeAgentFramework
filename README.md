### BreezeAgent 第一個繁體中文 Agent 輕量化工具包
[![status](https://img.shields.io/badge/status-WIP-orange.svg?style=flat-square)](README.md) [![python](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=flat-square)](README.md) [![license](https://img.shields.io/badge/license-TBD-lightgrey.svg?style=flat-square)](README.md)

### What is it? 它是什麼？
他是一個 Python 套件，提供快速部屬 Breeze2 以及靈活切換市面上常見模型的功能。他的目標在於讓 LLM 佈署與使用變得極度簡單，並且包含最新的 LLM 相關技術（如：函數調用、RAG、工具規劃與並發、外顯思維鏈）。

- 對齊 PRD，本框架預設支援以 vLLM 提供的 OpenAI 相容端點部署 Breeze 2（Llama-Breeze2-8B-Instruct），同時也可指向其他相容供應商或本地端點，只需調整 `.env` 的 `OPENAI_API_BASE_URL` 與 `MODEL_NAME`。
- 內部採用 `LLMConnector` 封裝 OpenAI 相容 `/v1/chat/completions` 呼叫，`Orchestrator` 串接規劃/工具/綜合等核心模組以形成可組裝的流程。

---

### 目錄
- [What is it? 它是什麼？](#what-is-it-它是什麼)
- [主要特色](#主要特色)
- [系統需求](#系統需求)
- [安裝](#安裝)
- [設定](#設定)
- [快速開始](#快速開始)
- [程式化使用](#程式化使用)
- [工具擴充與 Schema](#工具擴充與-schema)
- [專案結構](#專案結構)
- [Roadmap](#現況說明roadmap)
- [貢獻指南](#貢獻指南)
- [授權條款](#授權條款)

---

### 系統需求
- Python 3.10 以上（建議 3.13）
- Windows/macOS/Linux
- vLLM 服務（用於 Breeze 2 相容端點）

---

### 安裝
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

### 設定
於專案根目錄建立 `.env`：
```bash
# OpenAI 相容端點（官方或其他供應商）
LLM_API_KEY=你的金鑰
OPENAI_API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
```

---

### 快速開始
互動 CLI：
```bash
python -m src.app
```

---

### 程式化使用
範例：直接在程式中使用 `Orchestrator` 進行單輪與多輪查詢。
```python
import os
from dotenv import load_dotenv
load_dotenv()

from src.agents.orchestrator import Orchestrator
from src.llm.llm_client import LLMConnector
from src.prompts.prompt_manager import PromptManager
from src.agents.orchestrator_core.planning_manager import PlanningManager
from src.agents.orchestrator_core.tool_executor import ToolExecutor
from src.agents.orchestrator_core.query_rewriter import QueryRewriter
from src.agents.orchestrator_core.conversation_manager import ConversationManager
from src.agents.orchestrator_core.synthesis_generator import SynthesisGenerator
from src.registry.tool_registry import ToolRegistry

llm_connector = LLMConnector(
    api_key=os.getenv("LLM_API_KEY"),
    api_base_url=os.getenv("OPENAI_API_BASE_URL"),
    default_model=os.getenv("MODEL_NAME")
)
prompt_manager = PromptManager()
planning_manager = PlanningManager(
    llm_client=llm_connector,
    tool_registry=ToolRegistry(),
    prompt_manager=prompt_manager
)
tool_executor = ToolExecutor(
    tool_registry=ToolRegistry(),
)
query_rewriter = QueryRewriter(
    llm_client=llm_connector,
    prompt_manager=prompt_manager
)
conversation_manager = ConversationManager(
    llm_client=llm_connector
)
synthesis_generator = SynthesisGenerator(
    llm_client=llm_connector,
    prompt_manager=prompt_manager
)

orchestrator = Orchestrator(
    prompt_manager=prompt_manager,
    planning_manager=planning_manager,
    tool_executor=tool_executor,
    conversation_manager=conversation_manager,
    synthesis_generator=synthesis_generator,
    query_rewriter=query_rewriter
)

# 單輪
print(orchestrator.aquery("今天天氣如何？"))

# 多輪（含歷史）
history = []
answer = orchestrator.aquery_with_history("今天適合出門嗎？", history)
print(answer)
```

---

### 工具擴充與 Schema
請參考下方標準工具 schema，並於 `src/registry/tool_registry.py`：
- 實作 `get_llm_tool_schemas()` 回傳 tools（OpenAI function calling 格式）
- 實作 `execute_tool(tool_name, **kwargs)` 執行對應工具

### 主要特色
以下是 Agent 主要聚焦的幾個功能：

1. 提問意圖重寫  
   - 由 `QueryRewriter`（`src/agents/orchestrator_core/query_rewriter.py`）結合 `PromptManager` 與 `LLMConnector`，將使用者提問重寫為更清楚、可查詢的句子，以利後續工具規劃與執行。

2. 工具使用 (To be continued)
   - 以 OpenAI function calling（tools schema）驅動：`PlanningManager` 會根據 `ToolRegistry.get_llm_tool_schemas()` 產生計畫，`ToolExecutor` 並行執行各工具，結果交由綜合模組整合。

3. 工具內容統整 (To be continued) 
   - `SynthesisGenerator` 將多個工具的回傳內容與原始問題整合，產出結構清楚且可閱讀的最終答案。

4. 內建 Path RAG 工具 (To be continued)
   - PRD 規劃之檔案路徑型檢索（Path RAG）對應標準工具 `RetrivalData`（見下方工具 schema 範例）。可將本地資料夾建立為知識庫來源，實作檢索後返回前 K 筆內容，供綜合模組使用。

5. 內建 SQLite 操作工具 (To be continued)
   - PRD 規劃之資料查詢工具對應標準工具 `QuerySQL`，以唯讀 SQL（建議限制）查詢本地 SQLite，並返回 JSON 結果。

6. 內建 API request 呼叫工具 (To be continued)
   - 可新增泛用 HTTP 工具（建議命名 `HTTPRequest`）或使用 PRD 中的 `QueryAgent` 進行轉送。以工具 schema 暴露 `url`、`method`、`headers`、`body` 等參數，滿足外部 API 呼叫情境。

7. 外顯思維鏈 (To be continued)
   - PRD 要求提供可視化與可追蹤的推理過程（外顯 CoT）。目前程式已具備歷史處理與路由能力，後續將擴充結構化推理歷程與前端呈現。

8. 基本前端功能 (To be continued)
   - 依 PRD 可用 Gradio 建立極簡聊天介面（見下方範例），支援即時對話、Markdown 顯示與歷史查看。未來可擴充多 Agent 管理與 RAG 知識庫管理介面。

---

### 使用方式

1) 安裝必要套件（最小可用）
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) 設定環境變數（專案根目錄建立 `.env`）
```bash
# 連線官方相容端點（範例）
LLM_API_KEY=你的金鑰
OPENAI_API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini

# 連線 Breeze 2（vLLM，相容端點）
# 若你已用 vLLM 服務起一個 breeze 模型：
# vllm serve MediaTek-Research/Llama-Breeze2-8B-Instruct-v0_1 --served-model-name breeze --api-key YOUR_API_KEY
# 則 .env 可設：
# OPENAI_API_BASE_URL=http://localhost:8000/v1
# MODEL_NAME=breeze
# LLM_API_KEY=YOUR_API_KEY
```

3) 執行互動 CLI
```bash
python -m src.app
```
- 看到提示後直接輸入問題，輸入 `exit` 離開。
- 若遇到匯入錯誤，請從專案根目錄執行 `python -m src.app`（避免直接 `python src/app.py`）。

4) 工具啟用（可選） (To be continued)
- 將你的工具 schema 由 `ToolRegistry.get_llm_tool_schemas()` 暴露；並在 `ToolRegistry.execute_tool()` 實作實際邏輯。
- 範例最小工具（echo）
```python
# src/registry/tool_registry.py（示意）
from typing import List, Dict, Any, Callable

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Callable[..., str]] = {
            "echo": lambda text: f"echo: {text}",
        }
    def get_llm_tool_schemas(self) -> List[Dict[str, Any]]:
        return [{
            "type": "function",
            "function": {
                "name": "echo",
                "description": "回傳輸入文字（教學用範例）",
                "parameters": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"]
                }
            }
        }]
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        func = self._tools.get(tool_name)
        if not func:
            return f"[Tool '{tool_name}' 未註冊]"
        return func(**kwargs)
```

- PRD 標準工具 schema 範例（可依需求擴充）：
  - `QuerySQL`
```json
{
  "type": "function",
  "function": {
    "name": "QuerySQL",
    "description": "查詢指定資料表，回傳 JSON 結果",
    "parameters": {
      "type": "object",
      "properties": {
        "table_name": {"type": "string"},
        "command": {"type": "string", "description": "SQL 語句（限制讀取）"}
      },
      "required": ["table_name", "command"]
    }
  }
}
```
  - `RetrivalData`
```json
{
  "type": "function",
  "function": {
    "name": "RetrivalData",
    "description": "於指定知識庫進行檢索，回傳前 K 筆內容",
    "parameters": {
      "type": "object",
      "properties": {
        "knowledge_base": {"type": "string"},
        "query": {"type": "string"},
        "top_k": {"type": "integer", "default": 5, "minimum": 1, "maximum": 50}
      },
      "required": ["knowledge_base", "query"]
    }
  }
}
```
  - `QueryAgent` 或 `HTTPRequest`（外部服務呼叫）
```json
{
  "type": "function",
  "function": {
    "name": "HTTPRequest",
    "description": "發送 HTTP 請求，回傳文字/JSON 內容",
    "parameters": {
      "type": "object",
      "properties": {
        "url": {"type": "string"},
        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
        "headers": {"type": "object"},
        "body": {"type": "object"}
      },
      "required": ["url"]
    }
  }
}
```

5) 現況說明（Roadmap）
- 目前：多輪對話、意圖重寫、基本規劃/工具框架、結果綜合已可運作。
- 即將擴充：外顯 CoT、Path RAG/SQLite/API 工具的預設實作、Gradio 前端、RAG/Agent 設定與管理能力。
- 詳細請見 `_vibe/PRD.md`。

---

### 專案結構
```text
src/
  app.py
  agents/
    orchestrator.py
    orchestrator_core/
      planning_manager.py
      tool_executor.py
      query_rewriter.py
      conversation_manager.py
      synthesis_generator.py
  llm/llm_client.py
  prompts/
    prompt_manager.py
    prompt.json
  registry/
    tool_registry.py
```

---

### 貢獻指南
歡迎 Issue 與 PR！建議流程：
1. 建立 Issue 描述背景與需求
2. Fork 並建立功能分支
3. 開發與撰寫/更新對應文件
4. 使用 Conventional Commits 撰寫訊息（例如：`feat: 新增 SQLite 查詢工具`）
5. 建立 PR 並描述動機、設計與測試方式

---
### 授權條款
未標註授權，預設為專案作者保留所有權利。如需另行授權，請補充本段落或新增 `LICENSE`。
