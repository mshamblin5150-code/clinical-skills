"""Complete synthetic approval envelopes without weakening production schemas."""
from hashlib import sha256
from pathlib import Path


def posting_record(source: Path, *items: dict) -> dict:
    fingerprint = sha256(source.read_bytes()).hexdigest()
    return {
        'version': 1, 'approval_revision': 1,
        'items': [{
            'sha256': fingerprint, 'sources': [str(source)],
            'grader_args': [str(source.parent)], 'approval_revision': 1,
            'posting_route': 'agent', 'pregrade_status': 'clean',
            **item,
        } for item in items],
    }
