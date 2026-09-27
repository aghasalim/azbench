# -*- coding: utf-8 -*-
"""Write the Hugging Face dataset: python -m azbench.export_hf -> hf/

One config per source, each under that source's own licence, with the exact
Azerbaijani prompt azbench sends, so a score run from the dataset is comparable
to a score from azbench.run."""
import os
import pandas as pd
from azbench.tasks import TASKS, LETTERS

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'hf')

for name, fn in TASKS.items():
    rows = []
    for x in fn():
        rows.append({'id': x['id'], 'subject': x['subject'], 'prompt': x['prompt'],
                     'choices': x['choices'], 'answer': x['answer'],
                     'answer_letter': LETTERS[x['answer']]})
    d = os.path.join(OUT, 'data', name)
    os.makedirs(d, exist_ok=True)
    pd.DataFrame(rows).to_parquet(os.path.join(d, 'test.parquet'), index=False)
    print(name, len(rows))
