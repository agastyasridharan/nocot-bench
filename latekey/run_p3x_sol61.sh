#!/usr/bin/env bash
# Run after run_main_sol61.sh. This script can also be run independently.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p latekey/runs
python3 latekey/run.py --model gpt-6.1-sol --effort low --no-prefill --recipe r4_noprefill --data latekey/data_p3x \
  --out latekey/runs/p3x__gpt-6.1-sol.jsonl --tag p3x --budget 10 --workers 64 --seed 4
echo P3X_DONE
