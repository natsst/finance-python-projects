#!/bin/zsh
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

# Activate env
if [ -x "$REPO_DIR/.venv/bin/activate" ]; then
  source "$REPO_DIR/.venv/bin/activate"
else
  if command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate finpy
  fi
fi

echo ""
echo "==============================="
echo " Finance Python Apps Launcher"
echo "==============================="
echo "1) Comparable Companies (Comps)"
echo "2) DCF Valuation Model"
echo ""
read -r "choice?Select an app (1 or 2): "

case "$choice" in
  1)
    PORT=8503
    APP="01_comps/app.py"
    ;;
  2)
    PORT=8502
    APP="02_dcf/app.py"
    ;;
  *)
    echo "Invalid choice. Exiting."
    exit 1
    ;;
esac

# Free port
lsof -ti tcp:$PORT | xargs -r kill -9 2>/dev/null || true

echo ""
echo "Launching app on http://localhost:$PORT"
open "http://localhost:$PORT"
streamlit run "$APP" --server.port "$PORT" --server.headless true