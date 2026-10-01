#!/usr/bin/env bash
cd "$(dirname "$0")/.."
until grep -q ALL_DONE latekey/runs/main_sol61.log; do sleep 10; done
python3 latekey/run.py --model gpt-6.1-sol --effort low --no-prefill --recipe r4_noprefill --data latekey/data_p3x \
  --out latekey/runs/p3x__gpt-6.1-sol.jsonl --tag p3x --budget 10 --workers 64 --seed 4
echo P3X_DONE
