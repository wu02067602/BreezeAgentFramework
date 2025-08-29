#!/bin/bash

# 設置模型路徑
MODEL_PATH="./Llama-Breeze2-8B-Instruct-text-only"

# 啟動 vLLM 服務
# 使用 --max-model-len 參數設置為小於 41968 的值
# 使用 --gpu-memory-utilization 參數增加 GPU 記憶體利用率
vllm serve $MODEL_PATH \
  --dtype auto \
  --api-key token-abc123 \
  --port 6667 \
  --max-model-len 40000 \
  --gpu-memory-utilization 0.9 \

# 如果需要更多參數，可以在上面的命令中添加
# 例如：--tensor-parallel-size 1