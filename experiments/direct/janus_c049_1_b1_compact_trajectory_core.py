from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True, order=True)
class Statistic:
    left: tuple[int, ...]
    right: tuple[int, ...]
    value: int


def stable_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _xor_basis(rows: Iterable[int]) -> tuple[int, ...]:
    """Return a deterministic reduced XOR basis, ordered by descending pivot."""
    basis: dict[int, int] = {}
    for raw in rows:
        x = int(raw)
        if x < 0:
            raise ValueError("negative vector")
        while x:
            pivot = x.bit_length() - 1
            if pivot in basis:
                x ^= basis[pivot]
                continue
            basis[pivot] = x
            # Reduce the new pivot from every existing row.
            for other_pivot, row in list(basis.items()):
                if other_pivot != pivot and ((row >> pivot) & 1):
                    basis[other_pivot] = row ^ x
            break

    # A newly added lower pivot may still occur in higher rows. Sweep once more
    # from low to high to obtain a canonical reduced basis.
    for pivot in sorted(basis):
        row = basis[pivot]
        for other_pivot in sorted(basis, reverse=True):
            if other_pivot != pivot and ((basis[other_pivot] >> pivot) & 1):
                basis[other_pivot] ^= row

    return tuple(basis[p] for p in sorted(basis, reverse=True))


def _checked_rows(raw_rows: Iterable[int], ambient_dim: int) -> tuple[int, ...]:
    if ambient_dim < 0:
        raise ValueError("negative ambient dimension")
    limit = 1 << ambient_dim
    rows = tuple(int(v) for v in raw_rows)
    if any(v < 0 or v >= limit for v in rows):
        raise ValueError("vector outside B")
    return rows


def normalize_stat(raw: dict, ambient_dim: int) -> Statistic:
    value = int(raw["value"])
    if value < 0:
        raise ValueError("negative lambda")
    left_rows = _checked_rows(raw["left"], ambient_dim)
    right_rows = _checked_rows(raw["right"], ambient_dim)
    return Statistic(_xor_basis(left_rows), _xor_basis(right_rows), value)


def span_contains(big: tuple[int, ...], small: tuple[int, ...]) -> bool:
    return _xor_basis(big + small) == _xor_basis(big)


def validate_trajectory(raw: Sequence[dict], ambient_dim: int) -> tuple[Statistic, ...]:
    if ambient_dim < 0:
        raise ValueError("negative ambient dimension")
    if not raw:
        raise ValueError("empty trajectory")

    stats = tuple(normalize_stat(item, ambient_dim) for item in raw)
    if stats[0].right != stats[-1].left:
        raise ValueError("endpoint condition")

    for left_stat, right_stat in zip(stats, stats[1:]):
        if not span_contains(right_stat.left, left_stat.left):
            raise ValueError("left not increasing")
        if not span_contains(left_stat.right, right_stat.right):
            raise ValueError("right not decreasing")
    return stats


def encode(stats: Sequence[Statistic]) -> list[dict]:
    return [
        {"left": list(stat.left), "right": list(stat.right), "value": stat.value}
        for stat in stats
    ]


def sequence_digest(stats: Sequence[Statistic]) -> str:
    return stable_digest(encode(stats))


def _interval_rule(stats: Sequence[Statistic], i: int, j: int) -> bool:
    if j - i <= 1:
        return False
    if (stats[i].left, stats[i].right) != (stats[j].left, stats[j].right):
        return False
    start = stats[i].value
    end = stats[j].value
    interior = [stat.value for stat in stats[i + 1 : j]]
    increasing = start <= end and all(start <= value <= end for value in interior)
    decreasing = start >= end and all(start >= value >= end for value in interior)
    return increasing or decreasing


def compactify(stats: Sequence[Statistic]) -> tuple[tuple[Statistic, ...], list[dict]]:
    """Deterministic leftmost compactification with a replayable transcript."""
    sequence = list(stats)
    if not sequence:
        raise ValueError("empty trajectory")

    trace: list[dict] = []
    while True:
        changed = False

        for index in range(1, len(sequence)):
            if sequence[index - 1] != sequence[index]:
                continue
            removed = [sequence[index]]
            before_length = len(sequence)
            del sequence[index]
            trace.append(
                {
                    "rule": "duplicate",
                    "start": index - 1,
                    "end": index,
                    "before_length": before_length,
                    "removed_entries": encode(removed),
                    "after_length": len(sequence),
                    "after_digest": sequence_digest(sequence),
                }
            )
            changed = True
            break
        if changed:
            continue

        for i in range(len(sequence)):
            for j in range(i + 2, len(sequence)):
                if not _interval_rule(sequence, i, j):
                    continue
                removed = sequence[i + 1 : j]
                before_length = len(sequence)
                del sequence[i + 1 : j]
                trace.append(
                    {
                        "rule": "interval",
                        "start": i,
                        "end": j,
                        "before_length": before_length,
                        "removed_entries": encode(removed),
                        "after_length": len(sequence),
                        "after_digest": sequence_digest(sequence),
                    }
                )
                changed = True
                break
            if changed:
                break

        if not changed:
            return tuple(sequence), trace


def is_compact(stats: Sequence[Statistic]) -> bool:
    compact, _ = compactify(stats)
    return compact == tuple(stats)


def width(stats: Sequence[Statistic]) -> int:
    if not stats:
        raise ValueError("empty trajectory")
    return max(stat.value for stat in stats)
