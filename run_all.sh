#!/usr/bin/env bash
# Waits for the groundedness augmenter to release the Groq quota, then runs the
# four Groq judges on every task in parallel (separate per-model daily caps).
set -u; cd "$(dirname "$0")"; PY=~/groundedness/.venv/bin/python
while pgrep -f "train/augment2.py" >/dev/null; do sleep 120; done
for m in qwen/qwen3.8-27b openai/gpt-oss-120b openai/gpt-oss-20b allam-2-7b; do
  nohup $PY -m azbench.run --models $m --pace 1 > "results/run-${m##*/}.log" 2>&1 &
done
wait
$PY -m azbench.table
echo "azbench runs done $(date +%H:%M)"
