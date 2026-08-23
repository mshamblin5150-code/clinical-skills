"""Shared row-identifier grammar for assertion records.

The grammar reads an assertion table's cell zero and nothing else. Consumers
retain responsibility for interpreting the rows it identifies.
"""

from __future__ import annotations

import re


ROW_ID = re.compile(r"^\|\s*([A-Z]\d+)\s*\|", re.M)
