#!/usr/bin/env python3
"""Structural checks for the recorded fixtures.

Runs in CI from .github/workflows/validate.yaml, and locally the same way:

    python3 scripts/validate.py

Why: jikan's test suite consumes this package through `composer link-fixtures`, so a malformed
snapshot or an orphaned page only shows up there, in a run whose diff does not contain the cause.
Checking it here reports it against the commit that introduced it.

Checks:
  * every snapshots/**/*.json parses (the files are JSON models, diffed and parsed by jikan);
  * every pages/*.html has its pages/*.meta.json beside it, and every meta file its page;
  * each meta file carries the url, status and recorded_at that `RecordedPages` reads.
"""

import glob
import json
import os
import sys

problems = []

snapshots = sorted(glob.glob('snapshots/**/*.json', recursive=True))
for path in snapshots:
    try:
        with open(path, encoding='utf-8') as handle:
            json.load(handle)
    except Exception as exc:  # any parse failure is a finding
        problems.append(f'{path}: {exc}')

pages = sorted(glob.glob('pages/*.html'))
metas = sorted(glob.glob('pages/*.meta.json'))

for page in pages:
    meta = page[: -len('.html')] + '.meta.json'
    if not os.path.exists(meta):
        problems.append(f'{page}: missing {meta}')

for meta in metas:
    page = meta[: -len('.meta.json')] + '.html'
    if not os.path.exists(page):
        problems.append(f'{meta}: missing {page}')
        continue

    try:
        with open(meta, encoding='utf-8') as handle:
            data = json.load(handle)
    except Exception as exc:
        problems.append(f'{meta}: {exc}')
        continue

    for key in ('url', 'status', 'recorded_at'):
        if key not in data:
            problems.append(f'{meta}: missing "{key}"')

print(f'{len(snapshots)} snapshot(s), {len(pages)} page(s), {len(metas)} meta file(s) checked')

if problems:
    print(f'\n{len(problems)} problem(s):')
    for problem in problems:
        print(f'  {problem}')
    sys.exit(1)
