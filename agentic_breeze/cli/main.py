#!/usr/bin/env python3
"""
Agentic Breeze CLI - Command Line Interface for Agentic Breeze Agent Framework
"""
import argparse
import sys
import os

from agentic_breeze.agents.orchestrator import Orchestrator
from agentic_breeze.llm.llm_client import LLMConnector
from agentic_breeze.prompts.prompt_manager import PromptManager
from agentic_breeze.agents.orchestrator_core.planning_manager import PlanningManager
from agentic_breeze.agents.orchestrator_core.tool_executor import ToolExecutor
from agentic_breeze.agents.orchestrator_core.query_rewriter import QueryRewriter
from agentic_breeze.agents.orchestrator_core.conversation_manager import ConversationManager
from agentic_breeze.agents.orchestrator_core.synthesis_generator import SynthesisGenerator
from agentic_breeze.registry.tool_registry import ToolRegistry


def create_orchestrator():
    """Create and configure the Agentic Breeze orchestrator"""
    llm_connector = LLMConnector(
        host_type=os.getenv("HOST_TYPE", "ollama"),
        timeout=int(os.getenv("TIMEOUT", "300")),
        max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
        temperature=float(os.getenv("TEMPERATURE", "0.5"))
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

    return Orchestrator(
        prompt_manager=prompt_manager,
        planning_manager=planning_manager,
        tool_executor=tool_executor,
        conversation_manager=conversation_manager,
        synthesis_generator=synthesis_generator,
        query_rewriter=query_rewriter
    )


def run_web_interface():
    """Launch the Gradio web interface"""
    try:
        import gradio as gr
        from dotenv import load_dotenv
        load_dotenv()
        
        orchestrator = create_orchestrator()
        
        def chat_interface(user_message, history):
            if not history:
                history = []
            
            # Gradio history format is List[List[str, str]] where inner list is [user_message, bot_message]
            # Our orchestrator expects List[Dict[str, str]]
            formatted_history = []
            for human, assistant in history:
                formatted_history.append({"role": "user", "content": human})
                formatted_history.append({"role": "assistant", "content": assistant})

            # Try streaming first, fallback to non-streaming
            try:
                full_reply = ""
                for chunk in orchestrator.aquery_with_history_stream(user_message, formatted_history):
                    if chunk:
                        full_reply += chunk
                        # Yield partial response for streaming effect
                        yield full_reply
                
                # Final yield with complete response
                yield full_reply
                
            except Exception as e:
                # Fallback to non-streaming
                print(f"Web streaming failed, using non-streaming mode: {e}")
                reply = orchestrator.aquery_with_history(user_message, formatted_history)
                yield reply

        print("=== 啟動 Gradio 介面 ===")
        
        gr.ChatInterface(
            chat_interface,
            title="Agentic Breeze 智慧助理",
            description="與您的 Agentic Breeze 助理對話。輸入 'exit' 或 'quit' 結束對話。",
            examples=[
                ["推薦台灣珍珠奶茶手搖店三間"],
                ["台北夜市知名小吃"],
                ["規劃宜蘭週末旅行"],
            ]
        ).launch()
    except ImportError:
        print("Error: gradio is required for web interface. Install with: pip install gradio")
        sys.exit(1)


def run_chat():
    """Run interactive chat mode"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        orchestrator = create_orchestrator()
        
        print("=== Agentic Breeze 智慧助理 CLI ===")
        print("輸入 'exit' 或 'quit' 結束對話")
        print("-" * 40)
        
        history = []
        
        while True:
            try:
                user_input = input("\n你: ").strip()
                
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("\n再見！")
                    break
                
                if not user_input:
                    continue
                
                # Get streaming response from orchestrator
                print(f"\nAgentic Breeze: ", end="", flush=True)
                full_reply = ""
                
                try:
                    for chunk in orchestrator.aquery_with_history_stream(user_input, history):
                        if chunk:
                            print(chunk, end="", flush=True)
                            full_reply += chunk
                    print()  # New line after streaming complete
                except Exception as e:
                    # Fallback to non-streaming if streaming fails
                    print(f"串流模式失敗，切換至一般模式: {e}")
                    full_reply = orchestrator.aquery_with_history(user_input, history)
                    print(full_reply)
                
                # Update history
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": full_reply})
                
            except KeyboardInterrupt:
                print("\n\n再見！")
                break
            except Exception as e:
                print(f"\n錯誤: {e}")
                
    except ImportError as e:
        print(f"Error: Missing required dependencies: {e}")
        print("Please install required packages with: pip install -r requirements.txt")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Agentic Breeze - 智慧助理框架",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Agentic Breeze 1.0.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Web interface command
    web_parser = subparsers.add_parser("web", help="Launch web interface")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat")
    
    args = parser.parse_args()
    
    if args.command == "web":
        run_web_interface()
    elif args.command == "chat":
        run_chat()
    else:
        # Default behavior - show help
        parser.print_help()


if __name__ == "__main__":
    main()