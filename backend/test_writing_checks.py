import json
import subprocess
from pathlib import Path

import pytest

from writing_checks import MAX_CODE_BYTES, run_writing_checks

DATA = Path(__file__).parent / 'testdata'
ALL_RULES = ['html_tag_pair', 'html_id_unique', 'html_alt', 'html_doctype', 'html_presentational',
             'css_syntax', 'css_unknown_property', 'css_invalid_value', 'js_syntax', 'js_eqeqeq', 'js_unused', 'js_undef', 'indentation']


def example(name):
    return {language: (DATA / f'lint_{name}.{extension}').read_text() for language, extension in [('html', 'html'), ('css', 'css'), ('javascript', 'js')]}


def test_clean_solution_has_no_issues():
    assert run_writing_checks(example('clean'), ALL_RULES) == []


def test_faulty_solution_uses_selected_rules_and_ignores_directives():
    report = run_writing_checks(example('faulty'), ALL_RULES)
    ids = {item['rule'] for item in report}
    assert {'alt-require', 'id-unique', 'doctype-first', 'presentational-tag', 'css-unknown-property', 'css-invalid-value', 'no-undef', 'no-unused-vars', 'eqeqeq'} <= ids
    assert all(item['severity'] == 'warning' for item in report)
    assert all(item['line'] >= 1 and item['column'] >= 1 for item in report)
    assert 'js-syntax' not in ids


def test_empty_tag_and_rule_selection():
    code = {'html': (DATA / 'lint_empty_tag.html').read_text(), 'css': '', 'javascript': ''}
    report = run_writing_checks(code, ['html_alt'])
    assert [item['rule'] for item in report] == ['alt-require']


def test_syntax_error_and_raw_message_fallback():
    report = run_writing_checks({'html': '', 'css': '', 'javascript': 'const = ;'}, ['js_syntax'])
    assert len(report) == 1
    assert report[0]['severity'] == 'error'
    assert report[0]['message'] == 'JavaScript yazımında beklenmeyen bir öğe var.'
    unknown = 'function f(a=1){"use strict";}'
    report = run_writing_checks({'html': '', 'css': '', 'javascript': unknown}, ['js_syntax'])
    assert report[0]['message'] == report[0]['raw_message']


def test_html_and_css_syntax_errors_are_errors():
    code = {'html': '<div><span></div>', 'css': 'p { color red; }', 'javascript': ''}
    report = run_writing_checks(code, ['html_tag_pair', 'css_syntax'])
    assert any(item['rule'] == 'tag-pair' and item['severity'] == 'error' for item in report)
    assert any(item['rule'] == 'css-syntax' and item['severity'] == 'error' for item in report)


def test_embedded_js_and_css_are_analyzed_without_running():
    html = '<style>p { colour: red }</style>\n<script>const bad = missing;</script>'
    report = run_writing_checks({'html': html, 'css': '', 'javascript': ''}, ['css_unknown_property', 'js_undef'])
    assert {(item['language'], item['rule'], item['line']) for item in report} == {('html', 'css-unknown-property', 1), ('html', 'no-undef', 2)}
    assert {item['rule']: item['column'] for item in report} == {'css-unknown-property': 12, 'no-undef': 21}


def test_student_javascript_is_not_executed(tmp_path):
    target = tmp_path / 'should-not-exist'
    code = f"require('node:fs').writeFileSync({json.dumps(str(target))}, 'executed')"
    run_writing_checks({'html': '', 'css': '', 'javascript': code}, ['js_syntax'])
    assert not target.exists()


def test_indentation_accepts_consistent_four_spaces_and_flags_inconsistency():
    clean = {'html': '', 'css': '', 'javascript': 'if (true) {\n    console.log(1);\n}\n'}
    assert run_writing_checks(clean, ['indentation']) == []
    clean['javascript'] = 'if (true) {\n    console.log(1);\n  console.log(2);\n}\n'
    assert any(item['rule'] == 'indent' for item in run_writing_checks(clean, ['indentation']))


def test_size_and_timeout_limits(monkeypatch):
    with pytest.raises(ValueError):
        run_writing_checks({'html': 'x' * (MAX_CODE_BYTES + 1), 'css': '', 'javascript': ''}, ['html_alt'])
    def timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired('node', 1)
    monkeypatch.setattr('writing_checks.subprocess.run', timeout)
    with pytest.raises(RuntimeError):
        run_writing_checks({'html': '', 'css': '', 'javascript': ''}, ['html_alt'])
