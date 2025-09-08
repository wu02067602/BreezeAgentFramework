
import time
import uuid
from typing import List, Dict, Any, Optional

from openai import OpenAI
from mtkresearch.llm.prompt import MRPromptV3


class StreamingChunk:
    """Wrapper to make streaming chunks compatible with OpenAI format."""
    def __init__(self, chunk_data: Dict[str, Any]):
        self._data = chunk_data
        
    @property
    def choices(self):
        return [Choice(self._data.get('choices', [{}])[0])]


class Choice:
    """Choice wrapper for streaming chunks."""
    def __init__(self, choice_data: Dict[str, Any]):
        self._data = choice_data
        
    @property
    def delta(self):
        return Delta(self._data.get('delta', {}))
    
    @property
    def finish_reason(self):
        return self._data.get('finish_reason')


class Delta:
    """Delta wrapper for streaming chunks."""
    def __init__(self, delta_data: Dict[str, Any]):
        self._data = delta_data
        
    @property
    def content(self):
        return self._data.get('content')
    
    @property
    def tool_calls(self):
        return self._data.get('tool_calls')


class Message:
    """Message wrapper for chat completion responses."""
    def __init__(self, message_data: Dict[str, Any]):
        self._data = message_data
        
    @property
    def content(self):
        return self._data.get('content')
    
    @property
    def tool_calls(self):
        return self._data.get('tool_calls')


class ResponseChoice:
    """Choice wrapper for chat completion responses."""
    def __init__(self, choice_data: Dict[str, Any]):
        self._data = choice_data
        
    @property
    def message(self):
        return Message(self._data.get('message', {}))
    
    @property
    def finish_reason(self):
        return self._data.get('finish_reason')


class ChatCompletionResponse:
    """Response wrapper to make dictionary responses compatible with object access."""
    def __init__(self, response_data: Dict[str, Any]):
        self._data = response_data
        
    @property
    def choices(self):
        return [ResponseChoice(choice) for choice in self._data.get('choices', [])]
    
    @property
    def id(self):
        return self._data.get('id')
    
    @property
    def object(self):
        return self._data.get('object')
    
    @property
    def created(self):
        return self._data.get('created')
    
    @property
    def model(self):
        return self._data.get('model')
    
    @property
    def usage(self):
        return self._data.get('usage')
        
    def to_dict(self):
        return self._data
        
    def model_dump(self):
        return self._data

class BreezeClient:
    def __init__(self, host_type='ollama', api_key=None, base_url=None):
        if host_type == 'ollama':
            base_url = "http://localhost:11434/v1"
            api_key = "ollama"
            self._model = 'ycchen/Breeze2-8B-TextOnly-Q4_K_M-NoTemplate'
        elif host_type == 'vllm':
            base_url = "http://localhost:6667/v1"
            api_key = "token-abc123"
            self._model = 'voidful/Llama-Breeze2-8B-Instruct-text-only'
        else:
            self._model = None
            assert api_key and base_url
        
        self._client = OpenAI(base_url=base_url, api_key=api_key)
        self._prompt_engine = MRPromptV3()
    
    def chat_completions_create(
        self,
        messages,
        model=None,
        max_tokens=None,
        temperature=0.8,
        top_p=0.5,
        stream=False,
        tool_choice="auto",  # Keep parameter for API compatibility
        tools=None,
        timeout=None,
    ):
        if model is None:
            model = self._model
        
        # Convert OpenAI tools to MRPromptV3 functions format
        functions = self._convert_openai_tools_to_functions(tools)
        
        # Create MRPromptV3 instance
        prompt_engine = MRPromptV3()
        
        # Convert messages to prompt string
        try:
            final_prompt = prompt_engine.get_prompt(messages, functions=functions)
        except Exception as e:
            raise ValueError(f"Error converting messages to prompt: {str(e)}")
        
        # Estimate prompt tokens
        prompt_tokens = self._estimate_tokens(final_prompt)
        
        # Prepare completion parameters
        completion_params = {
            "model": model,
            "prompt": final_prompt,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
            "stop": ["<|eot_id|>"]  # Stop at end of turn
        }
        
        if max_tokens:
            completion_params["max_tokens"] = max_tokens
        if timeout:
            completion_params["timeout"] = timeout
            
        if stream:
            return self._handle_streaming_response(completion_params, prompt_engine, model, prompt_tokens)
        else:
            return self._handle_non_streaming_response(completion_params, prompt_engine, model, prompt_tokens)

    def _convert_openai_tools_to_functions(self, tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        """Convert OpenAI tools format to MRPromptV3 functions format."""
        if not tools:
            return None
            
        functions = []
        for tool in tools:
            if tool.get('type') == 'function' and 'function' in tool:
                func_def = tool['function']
                functions.append({
                    'name': func_def['name'],
                    'description': func_def['description'],
                    'parameters': func_def.get('parameters')
                })
        return functions if functions else None

    def _create_openai_response(self, generated_text: str, model: str, prompt_tokens: int, 
                              completion_tokens: int, finish_reason: str = "stop") -> Dict[str, Any]:
        """Create OpenAI ChatCompletion format response."""
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": generated_text,  # This will be replaced with parsed message
                "finish_reason": finish_reason
            }],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        }

    def _create_streaming_chunk(self, delta: Optional[Dict[str, Any]], model: str, 
                              finish_reason: Optional[str] = None, index: int = 0) -> Dict[str, Any]:
        """Create OpenAI ChatCompletionChunk format for streaming."""
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": index,
                "delta": delta or {},
                "finish_reason": finish_reason
            }]
        }

    def _estimate_tokens(self, text: str) -> int:
        """Simple token estimation (rough approximation)."""
        return len(text.split())

    def _handle_non_streaming_response(self, completion_params: Dict[str, Any], 
                                     prompt_engine: MRPromptV3, model: str, prompt_tokens: int):
        """Handle non-streaming response."""
        # Call completions API
        completion = self._client.completions.create(**completion_params)
        
        # Get generated text
        generated_text = completion.choices[0].text.strip()

        # Estimate completion tokens
        completion_tokens = self._estimate_tokens(generated_text)
        
        # Parse generated text using MRPromptV3
        parsed_message = prompt_engine.parse_generated_str(generated_text)

        # Determine finish reason
        finish_reason = "tool_calls" if "tool_calls" in parsed_message else "stop"
        
        # Create OpenAI format response
        response = self._create_openai_response(generated_text, model, prompt_tokens, completion_tokens, finish_reason)
        response["choices"][0]["message"] = parsed_message
        
        return ChatCompletionResponse(response)

    def _handle_streaming_response(self, completion_params: Dict[str, Any], 
                                 prompt_engine: MRPromptV3, model: str, _prompt_tokens: int):
        """Handle streaming response with <|use_tool|> detection."""
        
        def stream_generator():
            # Call streaming completions API
            stream = self._client.completions.create(**completion_params)
            
            accumulated_text = ""
            tool_call_detected = False
            buffer = ""
            
            # Send initial chunk
            yield StreamingChunk(self._create_streaming_chunk({'role': 'assistant', 'content': ''}, model))
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].text:
                    delta_text = chunk.choices[0].text
                    accumulated_text += delta_text
                    buffer += delta_text
                    
                    # Check for tool call token
                    if "<|use_tool|>" in buffer and not tool_call_detected:
                        tool_call_detected = True
                        # Don't send any more content chunks, wait for complete generation
                        continue
                    
                    # If not in tool call mode, stream normally
                    if not tool_call_detected:
                        yield StreamingChunk(self._create_streaming_chunk({'content': delta_text}, model))
            
            # Process final accumulated text
            parsed_message = prompt_engine.parse_generated_str(accumulated_text)
            
            if tool_call_detected or "tool_calls" in parsed_message:
                # Send tool calls as a single chunk
                if "tool_calls" in parsed_message:
                    yield StreamingChunk(self._create_streaming_chunk({
                        'tool_calls': parsed_message['tool_calls']
                    }, model))
                
                # Send final chunk with finish reason
                yield StreamingChunk(self._create_streaming_chunk(None, model, finish_reason="tool_calls"))
            else:
                # Send final chunk for regular completion
                yield StreamingChunk(self._create_streaming_chunk(None, model, finish_reason="stop"))
        
        return stream_generator()

