import json
import subprocess
from pathlib import Path

MAX_CODE_BYTES = 256 * 1024
TIMEOUT_SECONDS = 8
WORKER = Path(__file__).parent / 'lint-worker' / 'check.cjs'


def run_writing_checks(code: dict, rules: list[str]) -> list[dict]:
    if sum(len(value.encode('utf-8')) for value in code.values()) > MAX_CODE_BYTES:
        raise ValueError('Kod boyutu yazım kontrolü sınırını aşıyor.')
    try:
        result = subprocess.run(
            ['node', str(WORKER)], input=json.dumps({'code': code, 'rules': rules}),
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=True,
        )
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, OSError, json.JSONDecodeError) as error:
        raise RuntimeError('Yazım kontrolü tamamlanamadı.') from error
