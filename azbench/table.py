# -*- coding: utf-8 -*-
"""Leaderboard from results/: python -m azbench.table -> results/leaderboard.json + LEADERBOARD.md"""
import glob, json, os, statistics
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []
for p in glob.glob(os.path.join(HERE, 'results', '*', '*.json')):
    d = json.load(open(p)); per = {}
    for t, res in d['tasks'].items():
        n = len(res); per[t] = {'n': n, 'acc': round(sum(1 for x in res.values() if x['ok']) / n, 4) if n else None, 'errors': sum(1 for x in res.values() if x['pred'] == -1)}
    accs = [v['acc'] for v in per.values() if v['acc'] is not None]
    rows.append({'model': d['model'], 'provider': d['provider'], 'tasks': per, 'mean': round(statistics.mean(accs), 4) if accs else None})
rows.sort(key=lambda r: -(r['mean'] or 0))
json.dump({'rows': rows}, open(os.path.join(HERE, 'results', 'leaderboard.json'), 'w'), ensure_ascii=False, indent=1)
tasks = sorted({t for r in rows for t in r['tasks']})
lines = ['| Model | Provider | ' + ' | '.join(tasks) + ' | Mean |', '|---|---|' + '---:|' * (len(tasks) + 1)]
for r in rows:
    lines.append(f"| `{r['model']}` | {r['provider']} | " + ' | '.join(f"{r['tasks'][t]['acc']:.1%} ({r['tasks'][t]['n']})" if t in r['tasks'] and r['tasks'][t]['acc'] is not None else '—' for t in tasks) + f" | **{r['mean']:.1%}** |")
open(os.path.join(HERE, 'LEADERBOARD.md'), 'w').write('# azbench leaderboard\n\nZero-shot, Azerbaijani, multiple choice, exact-letter scoring. Random = 25 %.\n\n' + '\n'.join(lines) + '\n')
print('\n'.join(lines))
