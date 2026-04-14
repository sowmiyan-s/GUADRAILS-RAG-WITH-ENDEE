#!/usr/bin/env bash
# Windows batch equivalent setup script
# GUADRAILS RAG WITH ENDEE - Setup for Windows

@echo off
chcp 65001 > nul

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  ⚔️  GUADRAILS RAG WITH ENDEE - Setup Script            ║
echo ║  Privacy-First Offline AI Document Assistant v2.0.0   ║
echo ╚════════════════════════════════════════════════════════╝
echo.

echo [*] Prerequisites Check
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python not found. Download from: https://python.org
    exit /b 1
)
echo ✓ Python found: & python --version

pip --version >nul 2>&1
if errorlevel 1 (
    echo ✗ pip not found
    exit /b 1
)
echo ✓ pip found

echo.
echo [*] Installing Dependencies
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pip install -r requirements.txt

echo.
echo [*] Setup Configuration
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo ✓ .env created
    echo.
    echo ⚠  Edit .env if needed (Ollama, Endee, ports, etc.)
) else (
    echo ✓ .env already exists
)

echo.
echo [*] Next Steps
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 1. Start Ollama:
echo    Download from: https://ollama.com
echo    Then pull a model: ollama pull gemma2:2b
echo.
echo 2. Start Endee Vector Database:
echo    cd ..\endee
echo    run.sh
echo.
echo 3. Start GUADRAILS RAG:
echo    python app.py
echo.
echo 4. Open in browser:
echo    http://localhost:8000
echo.
echo ✨ Setup complete!
