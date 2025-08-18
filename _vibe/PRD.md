
# BreezeAgentFramework - 產品需求文件 (PRD)

## 1. 產品概述

BreezeAgentFramework 是一個基於 Llama-Breeze2-8B-Instruct 模型的智能代理框架，旨在提供具備推理能力、記憶功能和工具整合的 AI 助手平台。該框架採用聯發科技研究院開發的 Breeze 2 模型作為核心引擎，專為繁體中文優化，並具備函數調用能力。框架使用 vLLM 進行高效模型部署和推理服務，致力於創建能夠進行複雜思考、保持長期記憶並與外部系統互動的智能代理。

## 2. 產品目標

### 2.1 主要目標
- 建立基於 Breeze 2 模型的可擴展智能代理框架
- 充分發揮 Breeze 模型的繁體中文優化能力
- 整合 Breeze 模型的函數調用功能
- 透過 vLLM 提供高效的模型推理服務
- 提供透明且可追蹤的推理過程
- 實現持久化的知識記憶和學習能力
- 整合多種外部工具和服務
- 優化上下文管理和資源利用效率

## 3. 核心功能需求

### 3.1 外顯CoT (Chain of Thought)
**功能描述**: 提供可視化的思考鏈，讓用戶能夠理解 AI 的推理過程

**詳細需求**:
- 即時顯示推理步驟
- 支援推理分支和回溯功能
- 提供推理過程的可視化介面
- 記錄推理歷史和決策點
- 支援推理過程的編輯和調整

**技術需求**:
- 結構化的思考鏈資料格式
- 即時推理狀態更新機制
- 可擴展的可視化元件


### 3.2 工具使用
**功能描述**: 整合多種外部工具，擴展代理的操作能力

**詳細需求**:
- **QuerySQL**: 特定資料庫查詢和資料檢索，interface: `data: json object = QuerySQL(table_name: str, command: str)`
- **RetrivalData**: RAG 檢索，interface: `data: json object = RetrivalData(knowledge_base: str, query: str, top_k: int = 5)`
- **QueryAgent**: 特定 Agent 使用來回應，interface: `response: str = QueryAgent(agent_name: str, query: str)`

**技術需求**:
- 插件式工具架構設計
- 統一的工具調用介面
- 工具結果驗證和格式化
- 並發工具調用支援
- 工具錯誤處理和重試機制

### 3.3 快速 Agent 定制功能
**功能描述**: 提供簡單易用的介面讓使用者快速建立自定義 Agent

**詳細需求**:
- Agent 模板選擇 (如客服助手、技術支援、內容創作等)
- 角色設定和性格定義
- 專業知識領域配置
- 回應風格和語調調整
- Agent 能力範圍限制設定
- 自定義指令和範例對話
- Agent 測試和預覽功能
- Agent 配置匯出/匯入

**技術需求**:
- Agent 配置檔案格式 (JSON/YAML)
- 動態 prompt 模板系統
- Agent 配置驗證機制
- 配置版本控制和回滾
- Agent 效能監控和優化建議

### 3.4 快速 RAG 系統建置
**功能描述**: 提供便捷的 RAG (檢索增強生成) 系統建立功能

**詳細需求**:
- 多格式文件上傳支援 (PDF, DOCX, TXT, MD, HTML)
- 文件自動切分和預處理
- 向量資料庫整合 (支援多種向量資料庫)
- 嵌入模型 API 整合 (OpenAI, Cohere, 本地模型等)
- 檢索策略配置 (相似度閾值、返回數量等)
- RAG 知識庫管理和更新
- 檢索結果品質評估
- 知識庫搜尋和瀏覽功能

**技術需求**:
- 文件解析和分塊演算法
- 嵌入 API 抽象層設計
- 向量資料庫連接器
- 檢索演算法優化
- 快取機制和效能優化
- 知識庫索引和元資料管理

### 3.5 Gradio 前端介面
**功能描述**: 提供簡潔易用的網頁聊天介面

**詳細需求**:
- 即時聊天對話介面
- 支援 Markdown 格式顯示
- 聊天歷史記錄功能
- 清除對話功能
- 響應式設計 (支援桌面和行動裝置)
- 簡潔直觀的使用者體驗
- Agent 切換和選擇功能
- RAG 知識庫管理介面

**技術需求**:
- Gradio ChatInterface 元件
- 與後端 API 的即時通訊
- 前端狀態管理
- 錯誤處理和重試機制
- 多 Agent 管理介面
- 檔案上傳和處理元件



## 4. 技術架構需求

### 4.1 Breeze 模型整合架構
- **模型規格**: Llama-Breeze2-8B-Instruct-v0_1
- **核心能力**: 
  - 繁體中文指令跟隨
  - 函數調用 (Function Calling)
- **部署技術棧**:
  - vLLM 推理引擎
  - OpenAI 相容 API
  - FastAPI 服務框架
- **部署要求**:
  - GPU 記憶體需求: 16GB+ (8B 參數模型)
  - 支援 CUDA 加速
  - vLLM 推理優化 (PagedAttention, 連續批次處理)
- **API 規格**:
  - OpenAI 相容的 /v1/chat/completions 端點
  - 支援 streaming 和 non-streaming 回應
  - 函數調用格式相容

### 4.2 系統架構
- 微服務架構設計
- 容器化部署支援 (Docker/Kubernetes)
- vLLM 服務水平擴展能力
- 高可用性保證
- Gradio 前端服務獨立部署

### 4.2.1 前端架構
- **Gradio 框架**: 基於 Python 的快速 UI 開發
- **部署方式**: 獨立 Web 服務
- **API 連接**: 透過 HTTP 與後端 vLLM 服務通訊
- **狀態管理**: Gradio 內建 session 管理

### 4.3 Agent 管理架構
- **Agent 註冊中心**: 統一管理所有 Agent 配置
- **動態 Agent 載入**: 支援 runtime 動態建立和載入 Agent
- **Agent 配置存儲**: 持久化 Agent 配置和版本管理
- **Agent 效能監控**: 監控 Agent 回應時間和品質指標

### 4.4 RAG 系統架構
- **文件處理管線**: 文件上傳、解析、分塊、嵌入的完整流程
- **向量資料庫抽象層**: 支援 Chroma、Pinecone、Weaviate 等多種向量資料庫
- **嵌入服務抽象**: 統一的嵌入 API 介面，支援多種嵌入模型
- **檢索引擎**: 高效的相似度搜尋和結果排序
- **快取層**: 嵌入結果和檢索結果的快取機制




## 5. Breeze 模型使用規範

詳見 `@_vibe/Breeze_manual.md` 文件，包含：

### 5.1 安裝要求
```bash
# vLLM 和模型相關
pip install vllm
pip install openai  # for API client

# Gradio 前端
pip install gradio
pip install requests

# RAG 和向量資料庫
pip install chromadb  # 向量資料庫
pip install sentence-transformers  # 本地嵌入模型 (optional)
pip install langchain  # 文件處理
pip install pypdf2  # PDF 處理
pip install python-docx  # Word 文件處理

# Agent 管理
pip install pydantic  # 配置驗證
pip install pyyaml  # YAML 配置支援
```

### 5.2 基本使用模式
- **指令跟隨**: 透過 vLLM 的 OpenAI 相容 API
- **函數調用**: 結構化的工具調用介面
- **前端介面**: Gradio ChatInterface 提供簡潔聊天體驗

### 5.2.1 Gradio 前端快速啟動
```python
import gradio as gr
import openai

# 設定 vLLM API 端點
client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="YOUR_API_KEY"
)

def chat_function(message, history):
    # 呼叫 vLLM API
    response = client.chat.completions.create(
        model="breeze",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content

# 啟動 Gradio 介面
iface = gr.ChatInterface(
    fn=chat_function,
    title="BreezeAgentFramework",
    description="基於 Breeze 模型的智慧助手"
)
iface.launch()
```

### 5.3 關鍵配置參數
- 模型 ID: `MediaTek-Research/Llama-Breeze2-8B-Instruct-v0_1`
- vLLM 啟動參數: `--model MediaTek-Research/Llama-Breeze2-8B-Instruct-v0_1 --served-model-name breeze --api-key YOUR_API_KEY`
- 推理配置: temperature=0.01, top_p=0.01, max_tokens=2048
- 數據類型: auto (vLLM 自動優化)
- Gradio 配置: `share=False, server_port=7860, inbrowser=True`
