# -*- coding: utf-8 -*-
"""azbench tasks: every task yields dicts {id, prompt, choices, answer (index), subject}.
All multiple-choice, scored by exact letter match, zero-shot, in Azerbaijani."""
import json, os, random
os.environ.setdefault('HF_HUB_DISABLE_IMPLICIT_TOKEN', '1')
from datasets import load_dataset

LETTERS = 'ABCD'
INSTR = 'Aşağıdakı sualın düzgün cavabını seçin. Yalnız hərfi yazın: A, B, C və ya D.'

def _mc(q, choices, passage=None):
    body = (f'Mətn: {passage}\n\n' if passage else '') + f'Sual: {q}\n' + '\n'.join(f'{LETTERS[i]}. {c}' for i, c in enumerate(choices)) + '\nCavab:'
    return INSTR + '\n\n' + body

def belebele():
    ds = load_dataset('facebook/belebele', 'azj_Latn', split='test')
    for i, r in enumerate(ds):
        ch = [r['mc_answer1'], r['mc_answer2'], r['mc_answer3'], r['mc_answer4']]
        yield {'id': f'belebele/{i}', 'prompt': _mc(r['question'], ch, r['flores_passage']), 'choices': ch, 'answer': int(r['correct_answer_num']) - 1, 'subject': 'reading'}

def include():
    ds = load_dataset('CohereLabs/include-base-44', 'Azerbaijani', split='test')
    for i, r in enumerate(ds):
        ch = [r['option_a'], r['option_b'], r['option_c'], r['option_d']]
        yield {'id': f'include/{i}', 'prompt': _mc(r['question'], ch), 'choices': ch, 'answer': int(r['answer']), 'subject': f"{r['domain']}/{r['subject']}"}

def _gated(name, key, split, qk, ck, ak, tag):
    tok = os.environ.get('HF_TOKEN') or ''
    ds = load_dataset(name, split=split, token=tok or None)
    for i, r in enumerate(ds):
        ch = [r[c] for c in ck] if isinstance(ck, (list, tuple)) else list(r[ck])
        a = r[ak]; a = LETTERS.index(a.strip().upper()[0]) if isinstance(a, str) and a.strip().upper()[:1] in LETTERS else int(a)
        yield {'id': f'{tag}/{i}', 'prompt': _mc(r[qk], ch), 'choices': ch, 'answer': a, 'subject': str(r.get('subject') or r.get('category') or tag)}

def tumlu():
    import ast
    ds = load_dataset('jafarisbarov/TUMLU-mini', 'azerbaijani', split='test')
    for i, r in enumerate(ds):
        ch = ast.literal_eval(r['choices']) if isinstance(r['choices'], str) else list(r['choices'])
        if len(ch) != 4 or r['answer'].strip().upper() not in LETTERS: continue
        yield {'id': f'tumlu/{i}', 'prompt': _mc(r['question'], ch), 'choices': ch, 'answer': LETTERS.index(r['answer'].strip().upper()), 'subject': r['subject']}

TASKS = {'belebele-az': belebele, 'include-az': include, 'tumlu-az': tumlu}

def load(name):
    return list(TASKS[name]())

if __name__ == '__main__':
    for t in TASKS:
        xs = load(t); print(t, len(xs)); print(xs[0]['prompt'][:400]); print('answer', LETTERS[xs[0]['answer']])
