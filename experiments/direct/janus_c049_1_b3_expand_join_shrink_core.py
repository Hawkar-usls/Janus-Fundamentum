from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Iterator


@dataclass(frozen=True, order=True)
class Statistic:
    left: tuple[int, ...]
    right: tuple[int, ...]
    value: int


def xor_basis(rows: Iterable[int], ambient_dim: int) -> tuple[int, ...]:
    if ambient_dim < 0:
        raise ValueError('negative ambient dimension')
    limit = 1 << ambient_dim
    table: dict[int, int] = {}
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= limit:
            raise ValueError('vector outside ambient space')
        while x:
            p = x.bit_length() - 1
            if p in table:
                x ^= table[p]
            else:
                table[p] = x
                for q, y in list(table.items()):
                    if q != p and ((y >> p) & 1):
                        table[q] = y ^ x
                break
    for p in sorted(table):
        row = table[p]
        for q in sorted(table, reverse=True):
            if q != p and ((table[q] >> p) & 1):
                table[q] ^= row
    return tuple(table[p] for p in sorted(table, reverse=True))


def span_vectors(basis: Sequence[int]) -> tuple[int, ...]:
    values = {0}
    for row in basis:
        values |= {x ^ row for x in tuple(values)}
    return tuple(sorted(values))


def contains(big: Sequence[int], small: Sequence[int]) -> bool:
    b = tuple(big)
    for raw in small:
        x = int(raw)
        for row in b:
            x = min(x, x ^ row)
        if x:
            return False
    return True


def subspace_sum(a: Sequence[int], b: Sequence[int], ambient_dim: int) -> tuple[int, ...]:
    return xor_basis((*a, *b), ambient_dim)


def subspace_intersection(a: Sequence[int], b: Sequence[int], ambient_dim: int) -> tuple[int, ...]:
    # FPT-safe exact implementation over the smaller represented boundary.
    va = set(span_vectors(a))
    vb = set(span_vectors(b))
    return xor_basis(sorted(va & vb), ambient_dim)


def dim(space: Sequence[int]) -> int:
    return len(tuple(space))


def encode_stat(s: Statistic) -> dict:
    return {'left': list(s.left), 'right': list(s.right), 'value': s.value}


def encode_trajectory(gamma: Sequence[Statistic]) -> list[dict]:
    return [encode_stat(s) for s in gamma]


def decode_trajectory(raw: Sequence[dict], boundary: Sequence[int], ambient_dim: int, require_compact: bool = True) -> tuple[Statistic, ...]:
    if not raw:
        raise ValueError('empty trajectory')
    B = xor_basis(boundary, ambient_dim)
    seq: list[Statistic] = []
    for item in raw:
        value = int(item['value'])
        if value < 0:
            raise ValueError('negative lambda')
        left = xor_basis(item['left'], ambient_dim)
        right = xor_basis(item['right'], ambient_dim)
        if not contains(B, left) or not contains(B, right):
            raise ValueError('statistic outside boundary')
        seq.append(Statistic(left, right, value))
    gamma = tuple(seq)
    if gamma[0].right != gamma[-1].left:
        raise ValueError('endpoint condition')
    for a, b in zip(gamma, gamma[1:]):
        if not contains(b.left, a.left):
            raise ValueError('left not increasing')
        if not contains(a.right, b.right):
            raise ValueError('right not decreasing')
    if require_compact and compactify(gamma)[0] != gamma:
        raise ValueError('noncompact trajectory')
    return gamma


def compactify(stats: Sequence[Statistic]) -> tuple[tuple[Statistic, ...], list[dict]]:
    seq = list(stats)
    trace: list[dict] = []
    while True:
        changed = False
        for i in range(1, len(seq)):
            if seq[i - 1] == seq[i]:
                before = len(seq)
                removed = encode_stat(seq[i])
                del seq[i]
                trace.append({'rule': 'duplicate', 'start': i - 1, 'end': i, 'removed': [removed], 'before_length': before, 'after_length': len(seq)})
                changed = True
                break
        if changed:
            continue
        for i in range(len(seq)):
            for j in range(i + 2, len(seq)):
                if (seq[i].left, seq[i].right) != (seq[j].left, seq[j].right):
                    continue
                values = [x.value for x in seq[i:j + 1]]
                inc = values[0] <= values[-1] and all(values[0] <= z <= values[-1] for z in values[1:-1])
                dec = values[0] >= values[-1] and all(values[0] >= z >= values[-1] for z in values[1:-1])
                if inc or dec:
                    before = len(seq)
                    removed = [encode_stat(x) for x in seq[i + 1:j]]
                    del seq[i + 1:j]
                    trace.append({'rule': 'interval', 'start': i, 'end': j, 'removed': removed, 'before_length': before, 'after_length': len(seq)})
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq), trace


def width(gamma: Sequence[Statistic]) -> int:
    return max(s.value for s in gamma)


def coordinate_vector(vector: int, basis_rows: Sequence[int]) -> int:
    rows = tuple(basis_rows)
    theta = len(rows)
    for mask in range(1 << theta):
        value = 0
        for i, row in enumerate(rows):
            if (mask >> i) & 1:
                value ^= row
        if value == vector:
            return mask
    raise ValueError('vector not in target basis span')


def boundary_transport(child_boundary: Sequence[int], parent_boundary: Sequence[int], ambient_dim: int) -> dict:
    child = xor_basis(child_boundary, ambient_dim)
    parent = xor_basis(parent_boundary, ambient_dim)
    if not contains(parent, child):
        raise ValueError('child boundary not contained in parent')
    return {
        'child_boundary': list(child),
        'parent_boundary': list(parent),
        'child_basis_in_parent_coordinates': [coordinate_vector(row, parent) for row in child],
    }


def expand_trajectory(gamma: Sequence[Statistic], child_boundary: Sequence[int], parent_boundary: Sequence[int], ambient_dim: int) -> tuple[tuple[Statistic, ...], dict]:
    transport = boundary_transport(child_boundary, parent_boundary, ambient_dim)
    child = xor_basis(child_boundary, ambient_dim)
    parent = xor_basis(parent_boundary, ambient_dim)
    for s in gamma:
        if not contains(child, s.left) or not contains(child, s.right):
            raise ValueError('child trajectory not represented in child boundary')
        if not contains(parent, s.left) or not contains(parent, s.right):
            raise ValueError('expanded statistic outside parent boundary')
    return tuple(gamma), transport


def project_stat(s: Statistic, target_boundary: Sequence[int], ambient_dim: int) -> tuple[Statistic, dict]:
    target = xor_basis(target_boundary, ambient_dim)
    left = subspace_intersection(s.left, target, ambient_dim)
    right = subspace_intersection(s.right, target, ambient_dim)
    lr = subspace_intersection(s.left, s.right, ambient_dim)
    lr_target = subspace_intersection(lr, target, ambient_dim)
    correction = dim(lr) - dim(lr_target)
    out = Statistic(left, right, s.value + correction)
    return out, {
        'input': encode_stat(s),
        'output': encode_stat(out),
        'lambda_correction': correction,
        'dim_left_intersection_right': dim(lr),
        'dim_triple_intersection': dim(lr_target),
    }


def shrink_trajectory(gamma: Sequence[Statistic], target_boundary: Sequence[int], ambient_dim: int) -> tuple[tuple[Statistic, ...], dict]:
    projected: list[Statistic] = []
    receipts: list[dict] = []
    for s in gamma:
        out, receipt = project_stat(s, target_boundary, ambient_dim)
        projected.append(out)
        receipts.append(receipt)
    compact, trace = compactify(projected)
    decode_trajectory(encode_trajectory(compact), target_boundary, ambient_dim, require_compact=True)
    return compact, {
        'target_boundary': list(xor_basis(target_boundary, ambient_dim)),
        'projected_precompact': encode_trajectory(projected),
        'projection_receipts': receipts,
        'compactification_trace': trace,
        'output': encode_trajectory(compact),
    }


def lattice_paths(m: int, n: int) -> Iterator[tuple[tuple[int, int], ...]]:
    if m <= 0 or n <= 0:
        return
    def rec(i: int, j: int, path: list[tuple[int, int]]):
        if i == m - 1 and j == n - 1:
            yield tuple(path)
            return
        for di, dj in ((1, 0), (0, 1), (1, 1)):
            ni, nj = i + di, j + dj
            if ni < m and nj < n:
                path.append((ni, nj))
                yield from rec(ni, nj, path)
                path.pop()
    yield from rec(0, 0, [(0, 0)])


def validate_lattice_path(path: Sequence[Sequence[int]], m: int, n: int) -> tuple[tuple[int, int], ...]:
    parsed = tuple((int(x[0]), int(x[1])) for x in path)
    if not parsed or parsed[0] != (0, 0) or parsed[-1] != (m - 1, n - 1):
        raise ValueError('bad lattice path endpoints')
    if len(set(parsed)) != len(parsed):
        raise ValueError('lattice path repeats a point')
    for a, b in zip(parsed, parsed[1:]):
        if (b[0] - a[0], b[1] - a[1]) not in ((1, 0), (0, 1), (1, 1)):
            raise ValueError('bad lattice step')
    return parsed


def join_trajectory(g1: Sequence[Statistic], g2: Sequence[Statistic], path: Sequence[Sequence[int]], boundary: Sequence[int], ambient_dim: int) -> tuple[tuple[Statistic, ...], dict]:
    B = xor_basis(boundary, ambient_dim)
    for gamma in (g1, g2):
        for s in gamma:
            if not contains(B, s.left) or not contains(B, s.right):
                raise ValueError('join child outside common boundary')
    P = validate_lattice_path(path, len(g1), len(g2))
    initial_intersection = subspace_intersection(g1[0].right, g2[0].right, ambient_dim)
    raw: list[Statistic] = []
    receipts: list[dict] = []
    for i, j in P:
        a, b = g1[i], g2[j]
        left = subspace_sum(a.left, b.left, ambient_dim)
        right = subspace_sum(a.right, b.right, ambient_dim)
        ar = subspace_sum(a.left, a.right, ambient_dim)
        br = subspace_sum(b.left, b.right, ambient_dim)
        current_intersection = subspace_intersection(ar, br, ambient_dim)
        correction = dim(initial_intersection) - dim(current_intersection)
        if correction < 0:
            raise ValueError('negative join correction')
        out = Statistic(left, right, a.value + b.value + correction)
        raw.append(out)
        receipts.append({
            'child_indices': [i, j],
            'child_left': encode_stat(a),
            'child_right': encode_stat(b),
            'initial_right_intersection_dim': dim(initial_intersection),
            'current_span_intersection_dim': dim(current_intersection),
            'lambda_correction': correction,
            'output': encode_stat(out),
        })
    compact, trace = compactify(raw)
    decode_trajectory(encode_trajectory(compact), B, ambient_dim, require_compact=True)
    return compact, {
        'boundary': list(B),
        'path': [[i, j] for i, j in P],
        'raw_join': encode_trajectory(raw),
        'raw_length': len(raw),
        'raw_width': width(raw),
        'stat_receipts': receipts,
        'compactification_trace': trace,
        'compact_join': encode_trajectory(compact),
        'compact_length': len(compact),
        'compact_width': width(compact),
    }


def statistic_leq(a: Statistic, b: Statistic) -> bool:
    return a.left == b.left and a.right == b.right and a.value <= b.value


def extension_preorder_witness(lower: Sequence[Statistic], upper: Sequence[Statistic]) -> dict | None:
    parent: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i in range(len(lower)):
        for j in range(len(upper)):
            if not statistic_leq(lower[i], upper[j]):
                continue
            if (i, j) == (0, 0):
                parent[(i, j)] = None
                continue
            for prev in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                if prev in parent:
                    parent[(i, j)] = prev
                    break
    end = (len(lower) - 1, len(upper) - 1)
    if end not in parent:
        return None
    path: list[tuple[int, int]] = []
    cur: tuple[int, int] | None = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return {'path': [[i, j] for i, j in path], 'path_length': len(path)}


def enumerate_subspaces(boundary: Sequence[int], ambient_dim: int) -> tuple[tuple[int, ...], ...]:
    B = xor_basis(boundary, ambient_dim)
    vectors = span_vectors(B)
    seen = {()}
    queue = [()]
    while queue:
        current = queue.pop(0)
        for vector in vectors[1:]:
            candidate = xor_basis((*current, vector), ambient_dim)
            if candidate not in seen:
                seen.add(candidate)
                queue.append(candidate)
    return tuple(sorted(seen))


def enumerate_compact_trajectories(boundary: Sequence[int], ambient_dim: int, k: int) -> tuple[tuple[Statistic, ...], ...]:
    B = xor_basis(boundary, ambient_dim)
    theta = len(B)
    subs = enumerate_subspaces(B, ambient_dim)
    states = tuple(Statistic(l, r, v) for l in subs for r in subs for v in range(k + 1))
    bound = (2 * theta + 1) * (2 * k + 1)
    out: dict[tuple, tuple[Statistic, ...]] = {}
    def key(g):
        return tuple((s.left, s.right, s.value) for s in g)
    def dfs(seq: tuple[Statistic, ...], target: tuple[int, ...]):
        last = seq[-1]
        if last.left == target:
            out[key(seq)] = seq
        if len(seq) >= bound:
            return
        for nxt in states:
            if not contains(nxt.left, last.left):
                continue
            if not contains(last.right, nxt.right):
                continue
            if not contains(target, nxt.left):
                continue
            candidate = (*seq, nxt)
            if compactify(candidate)[0] != candidate:
                continue
            dfs(candidate, target)
    for first in states:
        if contains(first.right, first.left):
            dfs((first,), first.right)
    return tuple(out[k0] for k0 in sorted(out))


def up_k(generators: Sequence[Sequence[Statistic]], boundary: Sequence[int], ambient_dim: int, k: int) -> dict:
    B = xor_basis(boundary, ambient_dim)
    normalized: list[tuple[Statistic, ...]] = []
    for g in generators:
        compact, _ = compactify(g)
        decode_trajectory(encode_trajectory(compact), B, ambient_dim, require_compact=True)
        if width(compact) <= k:
            normalized.append(compact)
    universe = enumerate_compact_trajectories(B, ambient_dim, k)
    entries: list[dict] = []
    for candidate in universe:
        for idx, source in enumerate(normalized):
            witness = extension_preorder_witness(source, candidate)
            if witness is not None:
                entries.append({'trajectory': encode_trajectory(candidate), 'source_index': idx, 'witness': witness})
                break
    return {
        'boundary': list(B),
        'k': k,
        'generator_count': len(normalized),
        'universe_size': len(universe),
        'entry_count': len(entries),
        'entries': entries,
    }


def grouped_partition_digest_payload(blocks: Sequence[Sequence[int]], ambient_dim: int) -> list[list[int]]:
    return [list(xor_basis(block, ambient_dim)) for block in blocks]


def validate_grouped_partition(blocks: Sequence[Sequence[int]], expected_block_count: int, ambient_dim: int) -> tuple[tuple[int, ...], ...]:
    if len(blocks) != expected_block_count:
        raise ValueError('grouped factor partition lost')
    normalized = tuple(xor_basis(block, ambient_dim) for block in blocks)
    if any(not block for block in normalized):
        raise ValueError('empty grouped factor block')
    return normalized
