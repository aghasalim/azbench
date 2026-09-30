"""Repeat runs of one model on Kaggle Benchmarks, to see how much a score moves
between runs with the same prompts at temperature 0.

    python -m azbench.kaggle_repeats build DIR   # from `kaggle b t download` output
    python -m azbench.kaggle_repeats             # print the counts
    python -m azbench.kaggle_repeats check       # fail if the README disagrees
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "kaggle" / "gemini-3.7-flash-repeats.json"
MODEL = "gemini-3.7-flash"
TASKS = ("belebele-az", "include-az", "tumlu-az")


def build(download_dir):
    runs = {}
    for f in sorted(glob.glob(f"{download_dir}/azbench-*/*/{MODEL}/*/azbench_*-run_id_*.run.json")):
        task, version = f.split("/")[-5].removeprefix("azbench-"), f.split("/")[-4]
        d = json.load(open(f))
        if d["state"] != "BENCHMARK_TASK_RUN_STATE_COMPLETED":
            continue
        answers = {}
        for s in d["subruns"]:
            for r in s.get("results", []):
                x = r.get("dictResult")
                if x:
                    answers[x["id"]] = [x["predicted"], x["gold"]]
        runs.setdefault(task, {})[f"v{version}"] = answers
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(runs, indent=0, sort_keys=True))


def counts():
    runs = json.loads(OUT.read_text())
    out = {}
    for task in TASKS:
        per_run = [sum(p == g for p, g in a.values()) for _, a in sorted(runs[task].items())]
        n = {len(a) for a in runs[task].values()}
        assert len(n) == 1, f"{task}: runs cover different questions"
        out[task] = (per_run, n.pop())
    return out


def sentence(c):
    parts = [f"{', '.join(map(str, runs[:-1]))} and {runs[-1]} of {n} {task}" for task, (runs, n) in c.items()]
    return "; ".join(parts)


if __name__ == "__main__":
    if sys.argv[1:2] == ["build"]:
        build(sys.argv[2])
    c = counts()
    for task, (runs, n) in c.items():
        print(f"{task:12} {runs} of {n}, spread {max(runs) - min(runs)}")
    if sys.argv[1:2] == ["check"]:
        readme = (ROOT / "README.md").read_text()
        spread, n = max((max(r) - min(r), n) for r, n in c.values())
        for want in (sentence(c), f"largest spread is {spread} of {n}"):
            if want not in readme:
                sys.exit(f"README does not contain: {want}")
        print("README matches")
