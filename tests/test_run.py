from azbench.run import to_retry


def test_resume_retries_errors_and_empty_replies_only():
    res = {
        'err': {'pred': -1, 'raw': 'ERROR 429'},
        'empty': {'pred': -1, 'raw': ''},
        'unparsed': {'pred': -1, 'raw': 'Bilmirəm, hamısı ola bilər'},
        'answered': {'pred': 2, 'raw': 'C'},
    }
    assert sorted(to_retry(res)) == ['empty', 'err']
