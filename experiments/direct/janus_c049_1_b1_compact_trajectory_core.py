from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Sequence

@dataclass(frozen=True, order=True)
class Statistic:
    left: tuple[int, ...]
    right: tuple[int, ...]
    value: int

def _xor_basis(rows: Iterable[int]) -> tuple[int, ...]:
    basis: dict[int, int] = {}
    for raw in rows:
        x = int(raw)
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                for q, y in list(basis.items()):
                    if q != p and ((y >> p) & 1):
                        basis[q] = y ^ x
                break
    return tuple(basis[p] for p in sorted(basis, reverse=True))

def normalize_stat(raw: dict) -> Statistic:
    value = int(raw['value'])
    if value < 0:
        raise ValueError('negative lambda')
    return Statistic(_xor_basis(raw['left']), _xor_basis(raw['right']), value)

def span_contains(big: tuple[int, ...], small: tuple[int, ...]) -> bool:
    for x0 in small:
        x = x0
        for y in big:
            x = min(x, x ^ y)
        if x:
            return False
    return True

def validate_trajectory(raw: Sequence[dict], ambient_dim: int) -> tuple[Statistic, ...]:
    if ambient_dim < 0 or not raw:
        raise ValueError('invalid trajectory')
    limit = 1 << ambient_dim
    stats = tuple(normalize_stat(x) for x in raw)
    for s in stats:
        if any(v < 0 or v >= limit for v in s.left + s.right):
            raise ValueError('vector outside B')
    if stats[0].right != stats[-1].left:
        raise ValueError('endpoint condition')
    for a, b in zip(stats, stats[1:]):
        if not span_contains(b.left, a.left):
            raise ValueError('left not increasing')
        if not span_contains(a.right, b.right):
            raise ValueError('right not decreasing')
    return stats

def compactify(stats: Sequence[Statistic]) -> tuple[tuple[Statistic, ...], list[dict]]:
    seq = list(stats)
    trace: list[dict] = []
    while True:
        changed = False
        for i in range(1, len(seq)):
            if seq[i - 1] == seq[i]:
                trace.append({'rule': 'duplicate', 'start': i - 1, 'end': i, 'removed': [i]})
                del seq[i]
                changed = True
                break
        if changed:
            continue
        for i in range(len(seq)):
            for j in range(i + 2, len(seq)):
                if (seq[i].left, seq[i].right) != (seq[j].left, seq[j].right):
                    continue
                values = [x.value for x in seq[i:j + 1]]
                increasing = values[0] <= values[-1] and all(values[0] <= x <= values[-1] for x in values[1:-1])
                decreasing = values[0] >= values[-1] and all(values[0] >= x >= values[-1] for x in values[1:-1])
                if increasing or decreasing:
                    trace.append({'rule': 'interval', 'start': i, 'end': j, 'removed': list(range(i + 1, j))})
                    del seq[i + 1:j]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq), trace

def is_compact(stats: Sequence[Statistic]) -> bool:
    return compactify(stats)[0] == tuple(stats)

def width(stats: Sequence[Statistic]) -> int:
    return max(s.value for s in stats)

def encode(stats: Sequence[Statistic]) -> list[dict]:
    return [{'left': list(s.left), 'right': list(s.right), 'value': s.value} for s in stats]
