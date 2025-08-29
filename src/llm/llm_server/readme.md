# Breeze2 本地端部署

支援兩種 inference backend：Ollama 和 vLLM。請根據您的需求選擇合適的方案。

## 方案比較

| 特性 | Ollama | vLLM |
|------|--------|------|
| 支援作業系統 | macOS、Windows、Linux | Linux、macOS |
| 安裝難度 | 簡單 | 中等 |
| 預設端口 | 11434 | 6667 |

---

## 方案一：Ollama Server

### 系統需求
- 作業系統：macOS、Windows 或 Linux

### 安裝步驟

#### 1. 安裝 Ollama
請至 Ollama 官方網站下載並安裝：[https://ollama.com/download](https://ollama.com/download)

#### 2. 啟動 Ollama 服務
在終端機/命令提示字元中執行以下指令，啟動本地 Ollama server (預設port 11434)：
```bash
ollama serve
```

#### 3. 拉取 Llama-Breeze2-8B-Instruct 模型
開啟另一個終端機視窗，執行：
```bash
ollama pull willqiu/Llama-Breeze2-8B-Instruct
```

#### 4. 測試 API
執行範例 Python 腳本，確認本地模型能正常回應：
```bash
python invoke_api.py
```

---

## 方案二：vLLM Server

### 系統需求
- Python 3.12 (推薦)
- pip 或 uv package manager
- 作業系統：Linux 或 macOS

### 安裝步驟

#### 1. 安裝相依套件
```bash
# 如果沒有安裝 uv，可以移除指令中的 `uv`
uv pip install -r requirements.txt
uv pip install vllm --torch-backend=auto
```

#### 2. 下載模型
下載 Llama-Breeze2-8B-Instruct-text-only 模型：
1. 前往 [Hugging Face 模型頁面](https://huggingface.co/voidful/Llama-Breeze2-8B-Instruct-text-only)
2. 下載模型檔案
3. 將模型放置在 `Llama-Breeze2-8B-Instruct-text-only` 目錄中

#### 3. 啟動 vLLM 伺服器
您可以在腳本中調整端口號、tensor-parallel-size 和其他設定：
```bash
sh run_breeze_vllm_server.sh
```

#### 4. 測試 API
執行範例腳本測試 API：
```bash
python invoke_api.py
```

### 額外資訊
- 伺服器預設運行在 localhost:6667
- 如需自訂設定，請編輯 `run_breeze_vllm_server.sh` 腳本

