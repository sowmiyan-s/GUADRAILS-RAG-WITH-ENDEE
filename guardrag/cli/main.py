"""
GuardRAG CLI - Command-line interface for the RAG chatbot.

Usage:
    guard-rag --pdf path/to/document.pdf
    guard-rag --pdf document.pdf --model llama2
"""

import os
import sys
import argparse
from pathlib import Path

# Add rich for console GUI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.theme import Theme
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.box import ROUNDED
from rich.rule import Rule

custom_theme = Theme({
    "info": "white",
    "warning": "dim white",
    "danger": "bold white"
})
console = Console(theme=custom_theme)

# Fix OMP error for FAISS
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from dotenv import load_dotenv

from guardrag.rag.core import build_rag_chain
from guardrag.utils.ollama import is_ollama_running, start_ollama_server
from guardrag.utils.safety import check_input_safety, check_output_safety

# Load environment variables
load_dotenv()

def display_banner(mode="CLI", version="1.1.3"):
    """Display a unified, premium centered banner for GuardRAG."""
    # Big Project Name
    title = Text("GUARD - RAG", style="bold white")
    # Small Description
    subtitle = Text("Privacy-First Offline AI Document Assistant", style="dim white")
    
    # Header Content centered in a panel
    header_content = Text.assemble(
        "\n",
        title,
        "\n",
        subtitle,
        "\n",
        justify="center"
    )

    console.print(Align.center(Panel(
        header_content,
        box=ROUNDED,
        border_style="white",
        padding=(1, 10),
        subtitle=f"v{version}",
        expand=False
    )))

    if mode == "WEB":
        from guardrag.utils.ollama import is_ollama_running
        ollama_active = is_ollama_running("http://localhost:11434")
        ollama_status = "[bold white]ONLINE[/bold white]" if ollama_active else "[dim white]OFFLINE[/dim white]"
        
        table = Table(box=None, show_header=False, padding=(0, 2))
        table.add_row("STATUS:", "ENGINES READY")
        table.add_row("ACCESS:", "[white underline]http://127.0.0.1:8000[/white underline]")
        table.add_row("OLLAMA:", ollama_status)
        console.print(Align.center(table))
    
    credits = Text.assemble(
        ("DEVELOPER: ", "dim"), ("SOWMIYAN S", "white"),
        ("  |  GITHUB: ", "dim"), ("https://github.com/sowmiyan-s/GUARD-RAG", "white underline")
    )
    console.print(Align.center(credits))
    console.print(Rule(style="dim white", characters="─"))
    console.print()

def display_web_ui_banner():
    """Proxy for unified banner in Web mode."""
    display_banner(mode="WEB")

def display_welcome_banner():
    """Proxy for unified banner in CLI mode."""
    display_banner(mode="CLI")

def run_web_ui():
    """Launch the internal FastAPI web application."""
    import uvicorn
    import threading
    import time
    import webbrowser

    display_web_ui_banner()
    
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:8000")
        
    threading.Thread(target=open_browser, daemon=True).start()
    # Reduced log level to hide unwanted server dump info
    uvicorn.run("guardrag.api.main:app", host="127.0.0.1", port=8000, log_level="info")
    sys.exit(0)





# Unified banner system handles this now.

def display_session_info(pdf_name, model, sensitivity, guardrails):
    """Display session configuration in a clean table."""
    table = Table(title="\n[bold cyan]Session Configuration[/bold cyan]", title_justify="left", box=None, padding=(0, 2))
    table.add_column("Parameter", style="dim", width=15)
    table.add_column("Value", style="bold white")
    
    table.add_row("📄 Document", pdf_name)
    table.add_row("🤖 Model", model)
    table.add_row("🔒 Sensitivity", f"[{'green' if sensitivity == 'Public' else 'yellow' if sensitivity == 'Internal' else 'orange3' if sensitivity == 'Confidential' else 'red'}]{sensitivity}[/]")
    table.add_row("⚙️ Guardrails", "[green]Enabled[/green]" if guardrails else "[red]Disabled[/red]")
    table.add_row("👤 Developer", "Sowmiyan S")
    table.add_row("🔗 GitHub", "[blue]sowmiyan-s[/blue]")
    
    console.print(table)
    console.print(Rule(style="dim"))



def main():
    """Main CLI entry point."""
    if len(sys.argv) == 1:
        run_web_ui()
        
    parser = argparse.ArgumentParser(
        prog="guard-rag",
        description="GuardRAG - Privacy-first, offline AI document assistant",
        epilog="Developer: Sowmiyan S | GitHub: https://github.com/sowmiyan-s | License: MIT"
    )
    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to the PDF file to query"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemma3:1b",
        help="Ollama model name (default: gemma3:1b)"
    )
    parser.add_argument(
        "--ollama-host",
        type=str,
        default="http://localhost:11434",
        help="Ollama server URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Document chunk size (default: 1000)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Chunk overlap (default: 200)"
    )
    parser.add_argument(
        "--no-guardrails",
        action="store_true",
        help="Disable safety guardrails"
    )
    parser.add_argument(
        "--sensitivity",
        type=str,
        default="Internal",
        choices=["Public", "Internal", "Confidential", "Restricted"],
        help="Data sensitivity level (default: Internal)"
    )
    
    args = parser.parse_args()
    
    # Validate PDF path
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        console.print(Panel(f"[bold red]Error:[/bold red] The file '{args.pdf}' does not exist.", border_style="red"))
        sys.exit(1)
    
    display_welcome_banner()
    
    # Check Ollama quietly
    if not is_ollama_running(args.ollama_host):
        console.print("[yellow]Ollama is not running. Attempting to start...[/yellow]")
        if start_ollama_server():
            console.print("[bold green]✓ Ollama started successfully[/bold green]")
        else:
            console.print(Panel(
                "[bold red]✗ Failed to start Ollama.[/bold red]\nPlease ensure Ollama is installed and the service is active.\nSource: [blue]https://ollama.ai[/blue]",
                title="Error", border_style="red"
            ))
            sys.exit(1)
    else:
        console.print("[bold green]✓ Connection stable[/bold green]")
    
    # Build RAG pipeline
    console.print(f"\n[cyan]Initializing neural engine with[/cyan] [bold white]{args.model}[/bold white]...")
    try:
        db_id, rag_chain = build_rag_chain(
            [str(pdf_path)],
            model=args.model,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            ollama_host=args.ollama_host
        )
    except Exception as e:
        console.print(f"[bold red]✗ Pipeline initialization failed: {e}[/bold red]")
        sys.exit(1)
    
    # Session Summary Table
    display_session_info(
        pdf_name=pdf_path.name,
        model=args.model,
        sensitivity=args.sensitivity,
        guardrails=not args.no_guardrails
    )
    
    console.print("\n[dim]Ready for queries. Type 'exit' to quit.[/dim]\n")
    
    messages = []
    enable_guardrails = not args.no_guardrails
    
    while True:
        try:
            # Enhanced prompt
            question = Prompt.ask(f"[bold cyan]Query document ({pdf_path.name})[/bold cyan]").strip()
            
            if not question:
                continue
            
            if question.lower() in ["exit", "quit"]:
                console.print("\n[bold green]✓[/bold green] [dim]Ending session. Goodbye![/dim]")
                break
            
            # Safety check: input
            if enable_guardrails:
                blocked = check_input_safety(
                    question,
                    args.sensitivity,
                    enabled=True
                )
                if blocked:
                    console.print(Panel(
                        f"[bold red]{blocked}[/bold red]", 
                        title="Security Block", 
                        border_style="red",
                        subtitle=f"Sensitivity: {args.sensitivity}"
                    ))
                    continue
            
            # Build message history
            from langchain_core.messages import HumanMessage, AIMessage
            chat_history = []
            for msg in messages:
                if msg["role"] == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                else:
                    chat_history.append(AIMessage(content=msg["content"]))
            
            # Get response
            try:
                with console.status(f"[bold green]Scanning knowledge base for {args.model}...[/bold green]"):
                    result = rag_chain.invoke({
                        "input": question,
                        "chat_history": chat_history
                    })
                
                if isinstance(result, dict) and "answer" in result:
                    answer = result["answer"]
                else:
                    answer = str(result)
                
                # Safety check: output
                if enable_guardrails:
                    blocked_out = check_output_safety(
                        answer,
                        args.sensitivity,
                        enabled=True
                    )
                    if blocked_out:
                        answer = f"[bold red]{blocked_out}[/bold red]"
                
                # Output Panel
                console.print()
                console.print(Panel(
                    Markdown(answer or ""), 
                    title=f"[bold green]Assistant ({args.model})[/bold green]", 
                    border_style="green", 
                    title_align="left",
                    padding=(1, 2)
                ))
                console.print()
                
                # Store in history
                messages.append({"role": "user", "content": question})
                messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                console.print(f"\n[bold red]✗ Inference error: {e}[/bold red]\n")
        
        except KeyboardInterrupt:
            console.print("\n\n[bold green]✓[/bold green] [dim]Session terminated by user.[/dim]")
            break


if __name__ == "__main__":
    main()
