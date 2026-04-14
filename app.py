#!/usr/bin/env python3
"""
GUADRAILS RAG WITH ENDEE - Application Entry Point

Start the Guadrails RAG application with Endee vector database:
    python app.py

The web interface will be available at http://localhost:8000

Requirements:
    - Ollama must be running (https://ollama.com)
    - Endee vector database must be running (https://github.com/endee-io/endee)
      Start with: ./run.sh (in Endee repository)

Environment Setup:
    1. Copy .env.example to .env and configure if needed
    2. Start Ollama: download from https://ollama.com and run
    3. Start Endee: clone https://github.com/endee-io/endee and run ./run.sh
    4. Run this script: python app.py
"""

import os
import sys
import argparse
import logging
import webbrowser
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables early
from dotenv import load_dotenv
load_dotenv()

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="GUADRAILS RAG WITH ENDEE - Privacy-First Offline AI Document Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python app.py                           # Start web server on localhost:8000
    python app.py --host 0.0.0.0            # Listen on all interfaces
    python app.py --port 8080               # Use custom port
    python app.py --no-browser              # Start without opening browser
    python app.py --model llama2            # Use specific Ollama model
        """,
    )

    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "127.0.0.1"),
        help="Host to bind server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="Port to bind server to (default: 8000)",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OLLAMA_MODEL", "gemma2:2b"),
        help="Ollama model to use (default: gemma2:2b)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on file changes (development)",
    )
    parser.add_argument(
        "--ollama-host",
        default=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        help="Ollama host URL (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--endee-host",
        default=os.environ.get("ENDEE_HOST", "http://localhost:8080"),
        help="Endee host URL (default: http://localhost:8080)",
    )

    args = parser.parse_args()

    # Display welcome banner
    display_banner(args.host, args.port)

    # Set environment variables
    os.environ["OLLAMA_HOST"] = args.ollama_host
    os.environ["ENDEE_HOST"] = args.endee_host
    os.environ["OLLAMA_MODEL"] = args.model

    # Pre-flight checks
    if not check_dependencies(args.ollama_host, args.endee_host):
        logger.warning("Some dependencies are not available. The application will attempt to run anyway.")
        logger.warning("Please ensure Ollama and Endee are running.")

    # Import FastAPI app
    from guardrag.api.main import app

    # Start server with uvicorn
    try:
        import uvicorn

        server_url = f"http://{args.host}:{args.port}"
        logger.info(f"\n🚀 Starting GUADRAILS RAG WITH ENDEE")
        logger.info(f"📡 Server: {server_url}")
        logger.info(f"🤖 Ollama: {args.ollama_host}")
        logger.info(f"🦅 Endee: {args.endee_host}")
        logger.info(f"📚 Model: {args.model}")
        logger.info(f"\n✨ Open your browser to: {server_url}")
        logger.info(f"Press CTRL+C to stop the server\n")

        if not args.no_browser:
            # Open browser after a short delay
            import threading
            timer = threading.Timer(1.5, lambda: webbrowser.open(server_url))
            timer.daemon = True
            timer.start()

        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
        )

    except ImportError:
        logger.error("uvicorn not found! Install with: pip install uvicorn")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        sys.exit(1)


def display_banner(host: str, port: int):
    """Display startup banner."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich.rule import Rule

    console = Console()

    # Title
    title = Text("⚔️  GUADRAILS RAG WITH ENDEE", style="bold cyan")
    subtitle = Text("Privacy-First Offline AI Document Assistant", style="dim cyan")
    powered = Text(
        "Powered by Endee Vector Database",
        style="bold magenta"
    )

    content = Text.assemble(
        "\n",
        title,
        "\n",
        subtitle,
        "\n\n",
        powered,
        "\n",
    )

    console.print(Align.center(Panel(
        content,
        border_style="cyan",
        padding=(1, 10),
    )))
    console.print()


def check_dependencies(ollama_host: str, endee_host: str) -> bool:
    """Check if all required services are running."""
    import requests

    services = {
        "Ollama": ollama_host,
        "Endee": endee_host,
    }

    all_healthy = True

    logger.info("🔍 Checking dependencies...")

    for service_name, service_url in services.items():
        try:
            response = requests.get(
                f"{service_url}/health" if service_name == "Endee" else service_url,
                timeout=2
            )
            if response.status_code == 200:
                logger.info(f"✓ {service_name}: {service_url} - OK")
            else:
                logger.warning(f"✗ {service_name}: {service_url} - Not responding")
                all_healthy = False
        except requests.exceptions.ConnectionError:
            logger.warning(f"✗ {service_name}: {service_url} - Connection failed")
            all_healthy = False
        except Exception as e:
            logger.warning(f"✗ {service_name}: {service_url} - Error: {e}")
            all_healthy = False
    
    logger.info("")
    return all_healthy


if __name__ == "__main__":
    main()
