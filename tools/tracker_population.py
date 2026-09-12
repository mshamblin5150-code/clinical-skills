"""Derive ``tracker_scan``'s population manifest from kept GitHub probes.

This module opens no socket. Fetch the three probes before the harvest::

    gh api graphql -f owner=OWNER -f name=REPO \
      -f query='query($owner:String!,$name:String!){repository(owner:$owner,name:$name){issues{totalCount} pullRequests{totalCount}}}' \
      > "$H/tracker-issues-population.json"
    gh api --include "repos/OWNER/REPO/issues/comments?per_page=1&page=1" \
      > "$H/tracker-comments-population.http"
    gh api --include "repos/OWNER/REPO/pulls/comments?per_page=1&page=1" \
      > "$H/tracker-reviews-population.http"
    python tools/tracker_population.py \
      "$H/tracker-issues-population.json" \
      "$H/tracker-comments-population.http" \
      "$H/tracker-reviews-population.http" \
      --write "$H/tracker-population.json"

For a comments endpoint, ``rel="last"`` at ``per_page=1`` is its exact count.
When that header is absent, the probe body must be a zero- or one-row JSON
array, whose length settles the remaining case.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from console_codec import require_python_floor, use_utf8


class PopulationError(Exception):
    """A probe that cannot establish its surface's population."""


def _count(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise PopulationError(f"{label} is not a nonnegative integer")
    return value


def issue_population(text: str) -> int:
    """Sum GraphQL's independent issue and pull-request populations."""
    try:
        repository = json.loads(text)["data"]["repository"]
        issues = repository["issues"]["totalCount"]
        pulls = repository["pullRequests"]["totalCount"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise PopulationError(f"invalid issue population probe: {error}") from error
    return _count(issues, "issues.totalCount") + _count(
        pulls, "pullRequests.totalCount"
    )


def comment_population(text: str) -> int:
    """Read an exact comments count from a per-page-one HTTP response."""
    parts = re.split(r"\r?\n\r?\n", text)
    if len(parts) < 2:
        raise PopulationError("comment population probe has no header/body split")
    headers = parts[-2]
    body = parts[-1].strip()
    link = next(
        (
            line.partition(":")[2].strip()
            for line in headers.splitlines()
            if line.lower().startswith("link:")
        ),
        "",
    )
    if link:
        for item in link.split(","):
            if 'rel="last"' not in item:
                continue
            match = re.search(r"<([^>]+)>", item)
            if match is None:
                break
            query = parse_qs(urlparse(match.group(1)).query)
            if query.get("per_page") != ["1"]:
                raise PopulationError(
                    'comment population rel="last" is not from per_page=1'
                )
            pages = query.get("page", [])
            if len(pages) == 1 and pages[0].isdigit():
                return _count(int(pages[0]), 'rel="last" page')
        raise PopulationError('comment population probe has an invalid rel="last"')
    try:
        rows = json.loads(body)
    except json.JSONDecodeError as error:
        raise PopulationError(f"invalid comment probe body: {error}") from error
    if not isinstance(rows, list) or len(rows) > 1:
        raise PopulationError(
            "a comment probe without rel=last must contain zero or one row"
        )
    return len(rows)


def manifest(issues: str, comments: str, reviews: str) -> dict:
    return {
        "version": 1,
        "populations": {
            "tracker-issues.json": issue_population(issues),
            "tracker-comments.json": comment_population(comments),
            "tracker-reviews.json": comment_population(reviews),
        },
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Derive tracker harvest populations from kept API probes."
    )
    parser.add_argument("issues", type=Path)
    parser.add_argument("comments", type=Path)
    parser.add_argument("reviews", type=Path)
    parser.add_argument("--write", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        payload = manifest(
            args.issues.read_text(encoding="utf-8"),
            args.comments.read_text(encoding="utf-8"),
            args.reviews.read_text(encoding="utf-8"),
        )
        temporary = args.write.with_name(args.write.name + ".tmp")
        args.write.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(args.write)
    except (OSError, PopulationError) as error:
        print(f"tracker-population: DID NOT DERIVE -- {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
