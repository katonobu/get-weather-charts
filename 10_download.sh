#/bin/bash
cd "$(dirname "$0")"
source ./.venv/bin/activate
python download_artifacts.py
