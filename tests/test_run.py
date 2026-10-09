from azbench.run import to_retry


def test_resume_retries_errors_and_empty_replies_only():
    res = {
        'err': {'pred': -1, 'raw': 'ERROR 429'},
        'empty': {'pred': -1, 'raw': ''},
        'unparsed': {'pred': -1, 'raw': 'Bilmirəm, hamısı ola bilər'},
        'answered': {'pred': 2, 'raw': 'C'},
    }
    assert sorted(to_retry(res)) == ['empty', 'err']


import pytest

from azbench.run import letter


@pytest.mark.parametrize('text,want', [
    ('B', 1),
    ('b', 1),
    ('Cavab: C', 2),
    ('Cavab: (D)', 3),
    ('a) yox, düzgün cavab B', 1),
    ('A variantı səhvdir, B də. Doğrusu C', 2),
    ('B is a good choice', 1),
    ('Bilmirəm', -1),
])
def test_letter(text, want):
    assert letter(text) == want


def test_ollama_totals_are_committed_and_match_the_leaderboard():
    """README links results/ollama/ and its two complete rows come from summary.json."""
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    summary = json.loads((root / 'results/ollama/summary.json').read_text())
    board = {(r['model'], r['provider']): r for r in json.loads((root / 'results/leaderboard.json').read_text())['rows']}
    for model, tasks in summary['models'].items():
        row = board[(model, 'ollama')]
        for task, (correct, n) in tasks.items():
            assert row['tasks'][task] == {'n': n, 'acc': round(correct / n, 4), 'errors': 0}
