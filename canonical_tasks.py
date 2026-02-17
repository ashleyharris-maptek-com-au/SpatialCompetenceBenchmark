"""Canonical SCBench task manifest.

This file is intentionally static/readable for reviewers.
Source of truth for bucket mapping remains:
experiments/benchmark_summary/bucket_mapping.py
"""

from __future__ import annotations

from experiments.benchmark_summary.bucket_mapping import BUCKET_ORDER, PAPER_TASKS_BY_BUCKET

CANONICAL_TASK_IDS: tuple[int, ...] = tuple(
  idx
  for bucket in BUCKET_ORDER
  for idx, _name in PAPER_TASKS_BY_BUCKET[bucket]
)

CANONICAL_TASK_SET: frozenset[int] = frozenset(CANONICAL_TASK_IDS)

CANONICAL_TASKS_BY_BUCKET: dict[str, list[tuple[int, str]]] = {
  bucket: list(PAPER_TASKS_BY_BUCKET[bucket])
  for bucket in BUCKET_ORDER
}
