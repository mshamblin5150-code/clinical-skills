"""Fixed producer budgets sum below one MiB; fixtures are the sole exclusion."""
import json
CAPS = {'receipt.json': 524288, 'git-first-failure.json': 32768,
        'release.json': 16384, 'admitted.json': 16384, 'owner.json': 2048,
        'worker.json': 98304, 'supervisor.json': 65536, 'external.json': 32768}
assert sum(CAPS.values()) < 1048576
def write(path, value):
    data = json.dumps(value, ensure_ascii=True, sort_keys=True).encode('ascii')
    if path.name not in CAPS or len(data) > CAPS[path.name]:
        raise RuntimeError('Evidence producer budget exceeded: ' + path.name)
    with path.open('xb') as stream:
        stream.write(data)
