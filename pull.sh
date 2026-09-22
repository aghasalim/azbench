#!/usr/bin/env bash
# Pull azbench results from siba-3 into the repo, rebuild the table, commit if changed.
cd ~/azbench && rsync -az -e "ssh -i $HOME/.ssh/id_pi_polymarket -o BatchMode=yes" zynorex@10.10.2.144:~/azbench/results/ results/ && ~/groundedness/.venv/bin/python -m azbench.table >/dev/null && git add -A results/leaderboard.json LEADERBOARD.md && git diff --cached --quiet || git commit -q -m "results: leaderboard update

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" && git push -q origin master 2>/dev/null; true
