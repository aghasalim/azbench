# -*- coding: utf-8 -*-
"""Leaderboard from results/: python -m azbench.table -> results/leaderboard.json + LEADERBOARD.md"""
import glob, json, os, statistics
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []
for p in glob.glob(os.path.join(HERE, 'results', '*', '*.json')):
    if p.endswith('summary.json'): continue
    d = json.load(open(p)); per = {}
    for t, res in d['tasks'].items():
        n = len(res); per[t] = {'n': n, 'acc': round(sum(1 for x in res.values() if x['ok']) / n, 4) if n else None, 'errors': sum(1 for x in res.values() if x['pred'] == -1)}
    accs = [v['acc'] for v in per.values() if v['acc'] is not None]
    rows.append({'model': d['model'], 'provider': d['provider'], 'tasks': per, 'mean': round(statistics.mean(accs), 4) if accs else None})
# Runs whose per-question files were lost keep their totals in summary.json.
for p in glob.glob(os.path.join(HERE, 'results', '*', 'summary.json')):
    d = json.load(open(p)); prov = os.path.basename(os.path.dirname(p))
    for model, tasks in d['models'].items():
        per = {t: {'n': n, 'acc': round(c / n, 4), 'errors': 0} for t, (c, n) in tasks.items()}
        rows.append({'model': model, 'provider': prov, 'tasks': per, 'mean': round(statistics.mean(v['acc'] for v in per.values()), 4)})
FULL = {'belebele-az': 900, 'include-az': 548, 'tumlu-az': 700}
for r in rows:  # only a model that answered every question gets a mean and a rank
    r['complete'] = all(r['tasks'].get(t, {}).get('n') == n for t, n in FULL.items())
    if not r['complete']:
        r['mean'] = None
rows.sort(key=lambda r: (not r['complete'], -(r['mean'] or 0)))
json.dump({'rows': rows}, open(os.path.join(HERE, 'results', 'leaderboard.json'), 'w'), ensure_ascii=False, indent=1)
tasks = sorted({t for r in rows for t in r['tasks']})
lines = ['| Model | Provider | ' + ' | '.join(tasks) + ' | Mean |', '|---|---|' + '---:|' * (len(tasks) + 1)]
for r in rows:
    lines.append(f"| `{r['model']}` | {r['provider']} | " + ' | '.join(f"{r['tasks'][t]['acc']:.1%} ({r['tasks'][t]['n']})" if t in r['tasks'] and r['tasks'][t]['acc'] is not None else 'n/a' for t in tasks) + (f" | **{r['mean']:.1%}** |" if r['complete'] else ' | partial |'))
open(os.path.join(HERE, 'LEADERBOARD.md'), 'w').write('# azbench leaderboard\n\nZero-shot, Azerbaijani, multiple choice, exact-letter scoring. Always giving the most common answer scores 27.9 % on belebele-az, 26.3 % on include-az and 42.7 % on tumlu-az, so read each column against that, not against 25 %.\n\n' + '\n'.join(lines) + '\n')
print('\n'.join(lines))
