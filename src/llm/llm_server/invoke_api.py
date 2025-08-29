from openai import OpenAI
from mtkresearch.llm.prompt import MRPromptV3

# --- 1. 初始化 OpenAI 客戶端，指向您的本地服務 ---
client = OpenAI(
    base_url="http://localhost:6667/v1",
    api_key="token-abc123",
)

# --- 2. 準備對話內容 (與 client.chat.completions.create 的 messages 格式相同) ---
conversations = [
    {"role": "system", "content": "You are a helpful AI assistant built by MediaTek Research. The user you are helping speaks Traditional Chinese and comes from Taiwan."},
    {"role": "user", "content": "請問什麼是深度學習？"}
]

# --- 3. 使用 MRPromptV3 將對話內容轉換成模型預期的單一 prompt 字串 ---
prompt_engine = MRPromptV3()
final_prompt = prompt_engine.get_prompt(conversations)

# (可選) 印出轉換後的 prompt，以確認格式是否正確
print("--- Generated Prompt for /v1/completions ---")
print(repr(final_prompt)) # 使用 repr() 可以更清楚地看到特殊字符，如 \n
print("------------------------------------------\n")


# --- 4. 呼叫 /v1/completions API ---
# 使用 client.completions.create 並傳入格式化後的 final_prompt
completion = client.completions.create(
  model="./Llama-Breeze2-8B-Instruct-text-only",
  prompt=final_prompt,
  max_tokens=1024,     
  temperature=0.01,      
  stop=["<|eot_id|>"] # 告知模型在生成到下一個指令或結束時停止，可以提高穩定性
)

# --- 5. 印出結果 ---
# completions API 的結果在 choices[0].text 中
print("--- Model Response ---")
print(completion.choices[0].text.strip())
