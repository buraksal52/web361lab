from pathlib import Path
from uuid import uuid4

import pytest

import checker
from checker import MAX_HTML_BYTES, check_html, run_checker


def rule(tag, **changes):
    return {'id': str(uuid4()), 'tag': tag, 'attrs': {}, 'min_count': 1, 'non_empty': False, 'inside': None, 'label_linked': False, **changes}


@pytest.mark.parametrize(('fixture', 'expected'), [
    ('checker_complete.html', [True, True, True]),
    ('checker_incomplete.html', [True, False, True]),
    ('checker_empty.html', [False, True, False]),
])
def test_example_solutions(fixture, expected):
    html = (Path(__file__).parent / 'testdata' / fixture).read_text()
    rules = [rule('h1', non_empty=True), rule('input', attrs={'type': 'email', 'name': 'email', 'required': ''}, inside='form', label_linked=True), rule('button', inside='form', non_empty=True)]
    results = run_checker(html, rules)
    assert [result['used'] for result in results] == expected


def test_count_containment_attributes_and_label_association():
    html = '<input type="email"><form><label>E-posta <input type="email" name="a"></label><label for="b">B</label><input id="b" type="email" name="b"><input type="text"></form>'
    rules = [rule('input', attrs={'type': 'email'}, inside='form', label_linked=True, min_count=2), rule('input', attrs={'name': 'a'}, inside='form'), rule('input', attrs={'placeholder': ''}), rule('h1', non_empty=True)]
    results = check_html(html, rules)
    assert [result['count'] for result in results] == [2, 1, 0, 0]
    assert [result['used'] for result in results] == [True, True, False, False]


def test_checker_rejects_oversize_input():
    with pytest.raises(ValueError):
        run_checker('a' * (MAX_HTML_BYTES + 1), [])


def test_label_for_does_not_implicitly_label_different_input():
    html = '<label for="a">A<input id="b"></label><input id="a" type="hidden">'
    assert check_html(html, [rule('input', label_linked=True)])[0]['count'] == 0


def test_checker_enforces_deadline(monkeypatch):
    monkeypatch.setattr(checker, 'CHECK_TIMEOUT_SECONDS', 0)
    with pytest.raises(TimeoutError):
        run_checker('<h1>Başlık</h1>', [rule('h1')])
