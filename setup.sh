#!/usr/bin/env bash
# ──────────────────────────────────────────────
#  StyleMate Setup Script — Linux / macOS
# ──────────────────────────────────────────────
set -e

BOLD="\033[1m"; GREEN="\033[32m"; RED="\033[31m"; YELLOW="\033[33m"; RESET="\033[0m"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║        StyleMate — Setup Script          ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""

# ── Python check ──────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[ERROR] Python 3 not found. Install from https://python.org${RESET}"; exit 1
fi
PY_VER=$(python3 --version)
echo -e "${GREEN}[OK]${RESET} $PY_VER"

# ── Git check ─────────────────────────────────
if ! command -v git &>/dev/null; then
    echo -e "${RED}[ERROR] Git not found. Install git first.${RESET}"; exit 1
fi
echo -e "${GREEN}[OK]${RESET} $(git --version)"

# ── pip install ───────────────────────────────
echo ""
echo -e "${BOLD}[1/4] Installing Flask app dependencies...${RESET}"
pip3 install -r requirements.txt -q
echo -e "${GREEN}[OK]${RESET} Flask dependencies installed."

# ── Clone FASHN VTON ──────────────────────────
echo ""
echo -e "${BOLD}[2/4] Cloning FASHN VTON 1.5 model...${RESET}"
if [ -d "fashn-vton-1.5/.git" ]; then
    echo -e "${YELLOW}[SKIP]${RESET} fashn-vton-1.5 already cloned."
else
    git clone https://github.com/fashn-AI/fashn-vton-1.5.git fashn-vton-1.5
    echo -e "${GREEN}[OK]${RESET} Cloned."
fi

# ── Install FASHN ─────────────────────────────
echo ""
echo -e "${BOLD}[3/4] Installing FASHN VTON package...${RESET}"
pip3 install -e fashn-vton-1.5 -q
echo -e "${GREEN}[OK]${RESET} FASHN VTON package installed."

# ── Download weights ──────────────────────────
echo ""
echo -e "${BOLD}[4/4] Downloading model weights (~2 GB)...${RESET}"
if [ -f "fashn-weights/model.safetensors" ]; then
    echo -e "${YELLOW}[SKIP]${RESET} Weights already downloaded."
else
    python3 fashn-vton-1.5/scripts/download_weights.py --weights-dir fashn-weights
    echo -e "${GREEN}[OK]${RESET} Weights downloaded to ./fashn-weights/"
fi

# ── .env ─────────────────────────────────────
[ ! -f ".env" ] && cp .env.example .env && echo -e "${GREEN}[OK]${RESET} .env created."

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║  Setup complete!  Run:  python3 app.py   ║${RESET}"
echo -e "${BOLD}║  Then open: http://127.0.0.1:5000        ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""
