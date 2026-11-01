"""README figures from committed results: python scripts/make_figures.py -> results/*.png

Reads results/leaderboard.json (python -m azbench.table) and the Kaggle repeat runs
(results/kaggle/). Error bars are 95 % Wilson intervals on the item count, so they
show sampling noise from the question set, not run-to-run noise.
"""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from azbench import kaggle_repeats  # noqa: E402

TASKS = ("belebele-az", "include-az", "tumlu-az")
MAJORITY = {"belebele-az": 0.279, "include-az": 0.263, "tumlu-az": 0.427}  # from LEADERBOARD.md
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})


def wilson(k, n, z=1.96):
    p = k / n
    mid = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return mid - half, mid + half


def load():
    rows = json.loads((ROOT / "results" / "leaderboard.json").read_text())["rows"]
    gem = kaggle_repeats.counts()  # task -> ([correct per run], n)
    return rows, gem


def per_task(rows, gem, path):
    models = [(r["model"], {t: (round(r["tasks"][t]["acc"] * r["tasks"][t]["n"]), r["tasks"][t]["n"]) for t in TASKS})
              for r in rows if r["complete"]]
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    x = np.arange(len(TASKS))
    w = 0.26
    colors = ["#4c72b0", "#dd8452", "#55a868"]
    series = [(m, c) for m, c in models] + [(f"{kaggle_repeats.MODEL} (Kaggle, mean of 3 runs)", None)]
    for i, (name, counts) in enumerate(series):
        xs = x + (i - 1) * w
        if counts is None:  # Gemini: mean of the three runs, dots for each run
            ks = [np.mean(gem[t][0]) for t in TASKS]
            ns = [gem[t][1] for t in TASKS]
            for xi, t in zip(xs, TASKS):
                ax.scatter([xi] * 3, np.array(gem[t][0]) / gem[t][1], s=10, color="black", zorder=3)
        else:
            ks = [counts[t][0] for t in TASKS]
            ns = [counts[t][1] for t in TASKS]
        acc = np.array(ks) / np.array(ns)
        lo, hi = np.array([wilson(k, n) for k, n in zip(ks, ns)]).T
        ax.bar(xs, acc, w, color=colors[i], label=name, yerr=[acc - lo, hi - acc], capsize=3,
               error_kw={"lw": 1, "ecolor": "#333"})
        for xi, h, a in zip(xs, hi, acc):
            ax.text(xi, h + 0.012, f"{a:.1%}", ha="center", fontsize=7.5)
    for i, t in enumerate(TASKS):
        ax.hlines(MAJORITY[t], i - 1.6 * w, i + 1.6 * w, colors="#c0392b", linestyles="--", lw=1.2,
                  label="always the most common letter" if i == 0 else None)
    ax.set_xticks(x, [f"{t}\n({gem[t][1]} items)" for t in TASKS])
    ax.set_ylabel("accuracy")
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.17), frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def belebele(rows, gem, path):
    t = "belebele-az"
    items = []
    for r in rows:
        if t not in r["tasks"]:
            continue
        n, acc = r["tasks"][t]["n"], r["tasks"][t]["acc"]
        note = "" if n == 900 else f"first {n} of 900"
        if r["tasks"][t]["errors"]:
            note += f", {r['tasks'][t]['errors']} without an answer"
        items.append((f"{r['model']} ({r['provider']})", round(acc * n), n, note))
    ks, n = gem[t]
    items.append((f"{kaggle_repeats.MODEL} (kaggle)", np.mean(ks), n, "mean of 3 runs"))
    items.sort(key=lambda i: i[1] / i[2])
    fig, ax = plt.subplots(figsize=(8, 4))
    y = np.arange(len(items))
    for yi, (name, k, n, note) in zip(y, items):
        a = k / n
        lo, hi = wilson(k, n)
        full = n == 900
        ax.errorbar(a, yi, xerr=[[a - lo], [hi - a]], fmt="o", color="#4c72b0" if full else "#999",
                    mfc="#4c72b0" if full else "white", capsize=3, lw=1.2)
        ax.text(hi + 0.015, yi, f"{a:.1%}" + (f"  ({note})" if note else ""), va="center", fontsize=8)
    ax.axvline(MAJORITY[t], color="#c0392b", ls="--", lw=1.2)
    ax.text(MAJORITY[t] + 0.01, len(items) - 0.45, "most common letter", color="#c0392b", fontsize=8)
    ax.set_yticks(y, [i[0] for i in items], fontsize=8.5)
    ax.set_xlim(0.15, 1.45)
    ax.set_xticks(np.arange(0.2, 1.01, 0.2))
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_xlabel("belebele-az accuracy, 95 % Wilson interval (hollow: partial run)")
    ax.set_ylim(-0.6, len(items) - 0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    rows, gem = load()
    per_task(rows, gem, ROOT / "results" / "per_task.png")
    belebele(rows, gem, ROOT / "results" / "belebele.png")
