
# Llama-Breeze2-8B-Instruct-v0_1

【[Paper](https://arxiv.org/abs/2501.13921)】◇【[Kaggle Demo](https://www.kaggle.com/code/ycckaggle/demo-breeze-2-8b)】◇【[Collection](https://huggingface.co/collections/MediaTek-Research/llama-breeze2-67863158443a06a72dd29900)】 

**The Breeze 2 Herd of Models: Traditional Chinese LLMs Based on LLaMA with Vision-Aware and Function-Calling Capabilities**

Llama Breeze 2 is a suite of advanced multi-modal language models, available in 3B and 8B parameter configurations, specifically designed to enhance Traditional Chinese language representation. 
Building upon the [LLaMA 3.2](https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/), Breeze 2 continues pretraining on an extensive corpus to enhance the linguistic and cultural heritage of Traditional Chinese. 
It incorporates vision-aware capabilities through a visual encoder and a bridge module, and supports function-calling via prompt templates and post-training on function-calling data.

*Llama 3.2 is licensed under the Llama 3.2 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved.*  

*We list all contributors in alphabetical order of their first names, as follows: Chan-Jan Hsu (許湛然), Chia-Sheng Liu (劉佳昇), Meng-Hsi Chen (陳孟羲), Muxi Chen (陳沐希), Po-Chun Hsu (許博竣), Yi-Chang Chen (陳宜昌), and the supervisor Da-Shan Shiu (許大山).*

## Installation

```
pip3 install transformers==4.47.0
pip3 install -U mtkresearch
```

```python
from transformers import AutoModel, AutoTokenizer
from transformers import GenerationConfig
import torch
from mtkresearch.llm.prompt import MRPromptV3

model_id = 'MediaTek-Research/Llama-Breeze2-8B-Instruct-v0_1'
model = AutoModel.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True,
    device_map='auto',
    img_context_token_id=128212
).eval()

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True, use_fast=False)

generation_config = GenerationConfig(
  max_new_tokens=2048,
  do_sample=True,
  temperature=0.01,
  top_p=0.01,
  repetition_penalty=1.1,
  eos_token_id=128009
)

prompt_engine = MRPromptV3()

sys_prompt = 'You are a helpful AI assistant built by MediaTek Research. The user you are helping speaks Traditional Chinese and comes from Taiwan.'

def _inference(tokenizer, model, generation_config, prompt, pixel_values=None):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    if pixel_values is None:
        output_tensors = model.generate(**inputs, generation_config=generation_config)
    else:
        output_tensors = model.generate(**inputs, generation_config=generation_config, pixel_values=pixel_values.to(model.device, dtype=model.dtype))
    output_str = tokenizer.decode(output_tensors[0])
    return output_str
```

## Feature: Instruction Following

```python
conversations = [
    {"role": "system", "content": sys_prompt},
    {"role": "user", "content": "請問什麼是深度學習？"},
]

prompt = prompt_engine.get_prompt(conversations)
output_str = _inference(tokenizer, model, generation_config, prompt)
result = prompt_engine.parse_generated_str(output_str)
print(result)
# {'role': 'assistant', 'content': '深度學習是一種人工智慧技術，主要是透過模仿生物神經網路的結構和功能來實現。它利用大量數據進行訓練，以建立複雜的模型並使其能夠自主學習、預測或分類輸入資料。\n\n在深度學習中，通常使用多層的神經網路，每一層都包含許多相互連接的節點（稱為神經元）。這些神經元可以處理不同特徵的輸入資料，並將結果傳遞給下一層的神經元。隨著資料流向更高層次，這個過程逐漸捕捉到更抽象的概念或模式。\n\n深度學習已被廣泛應用於各種領域，如圖像識別、自然語言處理、語音識別以及遊戲等。它提供了比傳統機器學習方法更好的表現，因為它能夠從複雜且非線性的數據中提取出有用的資訊。'}
```

## Feature: Visual Instruction Following

Example Image:

![img_example](misc/test_big_data.png)

```python
conversations = [
    {"role": "system", "content": sys_prompt},
    {"role": "user", "content": [
        {
            "type": "image",
            "image_path": /path/to/example-image,
        },
        {
            "type": "text",
            "text": "請問前三名總共可獲得多少錢？"
        },
    ]},
]

prompt, pixel_values = prompt_engine.get_prompt(conversations)
output_str = _inference(tokenizer, model, generation_config, prompt, pixel_values=pixel_values)
result = prompt_engine.parse_generated_str(output_str)
print(result)
# {'role': 'assistant', 'content': '第一名可獲得30萬元，第二名可獲得20萬元，第三名可獲得15萬元。前三名總共可獲得65萬元。'}
```


## Feature: Function Calling

```python
import json

functions = [
    {
      "name": "get_current_weather",
      "description": "Get the current weather in a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          },
          "unit": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"]
          }
        },
        "required": ["location"]
      }
    }
]

def fake_get_current_weather(location, unit=None):
    return {'temperature': 30}

mapping = {
    'get_current_weather': fake_get_current_weather
}

# stage 1: query
conversations = [
    {"role": "user", "content": "請問台北目前溫度是攝氏幾度？"},
]

prompt = prompt_engine.get_prompt(conversations, functions=functions)

output_str = _inference(tokenizer, model, generation_config, prompt)
result = prompt_engine.parse_generated_str(output_str)

print(result)
# {'role': 'assistant', 'tool_calls': [{'id': 'call_0bcY2wePCVTg14Q6Xor93fHz', 'type': 'function', 'function': {'name': 'get_current_weather', 'arguments': '{"location": "台北", "unit": "celsius"}'}}]}
```


```python
# stage 2: execute called functions
conversations.append(result)

tool_call = result['tool_calls'][0]
func_name = tool_call['function']['name']
func = mapping[func_name]
arguments = json.loads(tool_call['function']['arguments'])
called_result = func(**arguments)

# stage 3: put executed results
conversations.append(
    {
        'role': 'tool',
        'tool_call_id': tool_call['id'],
        'name': func_name,
        'content': json.dumps(called_result)
    }
)

prompt = prompt_engine.get_prompt(conversations, functions=functions)

output_str2 = _inference(tokenizer, model, generation_config, prompt)
result2 = prompt_engine.parse_generated_str(output_str2)
print(result2)
# {'role': 'assistant', 'content': '台北目前的溫度是攝氏30度。'}
```
