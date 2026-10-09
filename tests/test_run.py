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
