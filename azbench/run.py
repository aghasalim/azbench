# -*- coding: utf-8 -*-
"""Run azbench tasks against OpenAI-compatible chat models. Resumable per (model, task, id).
    GROQ_API_KEY=... python -m azbench.run --models qwen/qwen3.8-27b,openai/gpt-oss-120b --tasks belebele-az,include-az
    OPENAI_BASE_URL=http://localhost:11434/v1 python -m azbench.run --models meristem2 ...   (Ollama)
Results: results/<provider>/<model>.json  {task: {id: {pred, ok}}}"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from azbench.tasks import TASKS, load, LETTERS
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def env():
    e = {}
    p = os.path.expanduser('~/SIBA/.env.local')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1); e[k.strip()] = v.strip().strip('"\'')
    return e

def ask(base, key, model, prompt, max_tokens):
    body = {'model': model, 'temperature': 0, 'max_tokens': max_tokens, 'messages': [{'role': 'user', 'content': prompt}]}
    if 'qwen3' in model: body['reasoning_format'] = 'hidden'
    if 'gpt-oss' in model: body['reasoning_effort'] = 'low'
    req = urllib.request.Request(base.rstrip('/') + '/chat/completions', data=json.dumps(body).encode(), headers={'authorization': 'Bearer ' + key, 'content-type': 'application/json', 'user-agent': 'azbench/0.1'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return (json.load(r)['choices'][0]['message'].get('content') or '').strip()

def letter(text):
    m = re.search(r'\b([ABCD])\b', text.upper())
    return LETTERS.index(m.group(1)) if m else -1

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--models', required=True); ap.add_argument('--tasks', default=','.join(TASKS)); ap.add_argument('--provider', default='')
    ap.add_argument('--base', default=''); ap.add_argument('--key', default=''); ap.add_argument('--max-tokens', type=int, default=1024); ap.add_argument('--pace', type=float, default=0.5); ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args(); e = env()
    base = a.base or os.environ.get('OPENAI_BASE_URL') or 'https://api.groq.com/openai/v1'
    key = a.key or os.environ.get('OPENAI_API_KEY') or (e.get('GROQ_API_KEY') if 'groq' in base else e.get('OPENROUTER_API_KEY', 'x')) or 'x'
    provider = a.provider or ('groq' if 'groq' in base else 'openrouter' if 'openrouter' in base else 'local')
    for model in a.models.split(','):
        path = os.path.join(HERE, 'results', provider, model.replace('/', '__') + '.json'); os.makedirs(os.path.dirname(path), exist_ok=True)
        out = json.load(open(path)) if os.path.exists(path) else {'model': model, 'provider': provider, 'tasks': {}}
        for task in a.tasks.split(','):
            rows = load(task); rows = rows[:a.limit] if a.limit else rows
            res = out['tasks'].setdefault(task, {})
            for k in [k for k, v in res.items() if v.get('pred') == -1 and (v.get('raw') or '').startswith(('ERROR', ''))]: res.pop(k)
            for r in rows:
                if r['id'] in res: continue
                for attempt in range(8):
                    try:
                        txt = ask(base, key, model, r['prompt'], a.max_tokens); break
                    except urllib.error.HTTPError as ex:
                        ra = ex.headers.get('retry-after'); wait = float(ra) + 1 if ra and ra.replace('.', '').isdigit() else 10 * (attempt + 1)
                        if ex.code in (429, 500, 502, 503) and attempt < 7: time.sleep(min(wait, 900)); continue
                        txt = f'ERROR {ex.code}'; break
                    except Exception as ex:  # noqa: BLE001
                        txt = f'ERROR {str(ex)[:40]}'; time.sleep(5)
                if not txt:  # reasoning models spend the budget before the first visible token
                    try: txt = ask(base, key, model, r['prompt'], 4000)
                    except Exception: txt = ''
                if not txt or txt.startswith('ERROR'):
                    time.sleep(30); continue  # rate-limited or empty: leave it for the next pass
                pred = letter(txt)
                res[r['id']] = {'pred': pred, 'ok': pred == r['answer'], 'raw': txt[:80], 'subject': r['subject']}
                json.dump(out, open(path, 'w'), ensure_ascii=False)
                n = len(res); acc = sum(1 for x in res.values() if x['ok']) / n
                if n % 25 == 0: print(f'{model} {task} {n}/{len(rows)} acc {acc:.3f}', flush=True)
                time.sleep(a.pace)
            n = len(res); print(f'== {model} {task}: {sum(1 for x in res.values() if x["ok"])}/{n} = {sum(1 for x in res.values() if x["ok"]) / max(1, n):.3f}', flush=True)

if __name__ == '__main__':
    main()
