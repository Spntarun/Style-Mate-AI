# ──────────────────────────────────────────────
#  StyleMate Setup Script — Windows
#  Run once to prepare the full environment.
# ──────────────────────────────────────────────
@echo off
setlocal enabledelayedexpansion
title StyleMate Setup

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║        StyleMate — Setup Wizard          ║
echo  ╚══════════════════════════════════════════╝
echo.

:: ── Check Python ──────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install Python 3.9+ from https://python.org
    pause & exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo  [OK] Python %PY_VER% found.

:: ── Check Git ─────────────────────────────────
git --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Git not found. Install Git from https://git-scm.com
    pause & exit /b 1
)
echo  [OK] Git found.

:: ── Install Flask app requirements ────────────
echo.
echo  [1/4] Installing Flask app dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 ( echo  [ERROR] pip install failed. & pause & exit /b 1 )
echo  [OK] Flask dependencies installed.

:: ── Clone FASHN VTON 1.5 ──────────────────────
echo.
echo  [2/4] Cloning FASHN VTON 1.5 model...
if exist "fashn-vton-1.5\.git" (
    echo  [SKIP] fashn-vton-1.5 already cloned.
) else (
    git clone https://github.com/fashn-AI/fashn-vton-1.5.git fashn-vton-1.5
    if errorlevel 1 ( echo  [ERROR] Clone failed. Check internet connection. & pause & exit /b 1 )
    echo  [OK] FASHN VTON 1.5 cloned.
)

:: ── Install FASHN VTON Python package ─────────
echo.
echo  [3/4] Installing FASHN VTON package...
pip install -e fashn-vton-1.5 --quiet
if errorlevel 1 ( echo  [ERROR] FASHN install failed. & pause & exit /b 1 )
echo  [OK] FASHN VTON package installed.

:: ── Download FASHN weights ────────────────────
echo.
echo  [4/4] Downloading model weights (~2 GB)...
if exist "fashn-weights\model.safetensors" (
    echo  [SKIP] Weights already downloaded.
) else (
    python fashn-vton-1.5\scripts\download_weights.py --weights-dir fashn-weights
    if errorlevel 1 (
        echo  [WARN] Weight download had issues. Check output above.
    ) else (
        echo  [OK] Weights downloaded to .\fashn-weights\
    )
)

:: ── Create .env if missing ────────────────────
if not exist ".env" (
    copy .env.example .env >nul 2>&1
    echo  [OK] .env file created from template.
)

:: ── Done ──────────────────────────────────────
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   Setup complete! Start the app with:    ║
echo  ║         python app.py                    ║
echo  ║   Then open: http://127.0.0.1:5000      ║
echo  ╚══════════════════════════════════════════╝
echo.
pause
