## Prerequisites

- Python 3.12 (recommended)
- pip or uv package manager
- CUDA-supported GPU (recommended for accelerated inference)

## Installation

```bash
# You can remove `uv` in the command if uv is not installed
uv pip install -r requirements.txt
uv pip install vllm --torch-backend=auto
```

## Download Model

Download the Llama-Breeze2-8B-Instruct-text-only model:

1. Go to the [Hugging Face model page](https://huggingface.co/voidful/Llama-Breeze2-8B-Instruct-text-only)
2. Download the model files
3. Place the model in the `Llama-Breeze2-8B-Instruct-text-only` directory

## Start vLLM Server

You can adjust port number, tensor-parallel-size, and other settings in the script:

```bash
sh run_breeze_vllm_server.sh
```

## Invoke Endpoint

Run the example script to test the API:

```bash
python invoke_api.py
```

## Additional Information

- Server runs on localhost:6667 by default
- For custom settings, edit the `run_breeze_vllm_server.sh` script