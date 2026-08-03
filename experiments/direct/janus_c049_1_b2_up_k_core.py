from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable, Sequence
from janus_c049_1_b1_compact_trajectory_core import Statistic, _xor_basis, compactify, encode, span_contains, validate_trajectory, width

OPEN_DISCOVERY_BUDGET = 'OPEN_DISCOVERY_BUDGET'
OPEN_WORK_BUDGET = 'OPEN_WORK_BUDGET'
OPEN_CERTIFICATE_VOLUME = 'OPEN_CERTIFICATE_VOLUME'

class CapabilityExceeded(RuntimeError):
    def __init__(self, terminal: str, counter: str, attempted: int, cap: int):
        super().__init__(terminal)
        self.terminal = terminal
        self.counter = counter
        self.attempted = attempted
        self.cap = cap

@dataclass
class Ledger:
    discovery_cap: int
    work_cap: int
    counters: dict[str, int] = field(default_factory=dict)

    def _charge(self, total_name: str, cap: int, counter: str, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError('negative charge')
        attempted = self.counters.get(total_name, 0) + amount
        if attempted > cap:
            terminal = OPEN_DISCOVERY_BUDGET if total_name == 'discovery_work' else OPEN_WORK_BUDGET
            raise CapabilityExceeded(terminal, counter, attempted, cap)
        self.counters[total_name] = attempted
        self.counters[counter] = self.counters.get(counter, 0) + amount

    def discovery(self, counter: str, amount: int = 1) -> None:
        self._charge('discovery_work', self.discovery_cap, counter, amount)

    def work(self, counter: str, amount: int = 1) -> None:
        self._charge('work', self.work_cap, counter, amount)

    def snapshot(self) -> dict[str, int]:
        required = (
            'discovery_work', 'work', 'rref_input_rows', 'rref_pivot_tests', 'rref_xors',
            'rref_output_rows', 'subspace_inclusion_tests', 'subspace_reduction_xors',
            'boundary_coordinate_changes', 'trajectory_prefix_states', 'trajectory_extension_trials',
            'lattice_cells', 'lattice_predecessor_tests', 'lattice_path_vertices',
            'generator_pair_tests', 'dominance_witnesses', 'full_set_entries',
        )
        out = dict(self.counters)
        for name in required:
            out.setdefault(name, 0)
        return dict(sorted(out.items()))

def trajectory_key(gamma: Sequence[Statistic]) -> tuple:
    return tuple((s.left, s.right, s.value) for s in gamma)

def decode_trajectory(raw: Sequence[dict], ambient_dim: int, require_compact: bool = True) -> tuple[Statistic, ...]:
    gamma = validate_trajectory(raw, ambient_dim)
    if require_compact and compactify(gamma)[0] != gamma:
        raise ValueError('trajectory is not compact')
    return gamma

def statistic_leq(a: Statistic, b: Statistic) -> bool:
    return a.left == b.left and a.right == b.right and a.value <= b.value

def extension_preorder_witness(
    lower: Sequence[Statistic], upper: Sequence[Statistic], ledger: Ledger
) -> dict | None:
    """JKO Section 3.2 preorder: lower preccurlyeq upper via synchronized extensions."""
    if not lower or not upper:
        raise ValueError('empty trajectory')
    m, n = len(lower), len(upper)
    parent: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i in range(m):
        for j in range(n):
            ledger.work('lattice_cells')
            if not statistic_leq(lower[i], upper[j]):
                continue
            if i == 0 and j == 0:
                parent[(i, j)] = None
                continue
            # Deterministic lexicographic predecessor priority: diagonal, vertical, horizontal.
            for prev in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                ledger.work('lattice_predecessor_tests')
                if prev in parent:
                    parent[(i, j)] = prev
                    break
    terminal = (m - 1, n - 1)
    if terminal not in parent:
        return None
    path: list[tuple[int, int]] = []
    cursor: tuple[int, int] | None = terminal
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    ledger.work('lattice_path_vertices', len(path))
    ledger.work('dominance_witnesses')
    lower_extension = [lower[i] for i, _ in path]
    upper_extension = [upper[j] for _, j in path]
    return {
        'path': [[i, j] for i, j in path],
        'lower_extension': encode(lower_extension),
        'upper_extension': encode(upper_extension),
        'path_length': len(path),
    }

def verify_extension_preorder_witness(
    lower: Sequence[Statistic], upper: Sequence[Statistic], witness: dict
) -> bool:
    path = witness.get('path')
    if not isinstance(path, list) or not path:
        return False
    parsed: list[tuple[int, int]] = []
    for cell in path:
        if not isinstance(cell, list) or len(cell) != 2:
            return False
        i, j = cell
        if not isinstance(i, int) or not isinstance(j, int):
            return False
        if not (0 <= i < len(lower) and 0 <= j < len(upper)):
            return False
        parsed.append((i, j))
    if parsed[0] != (0, 0) or parsed[-1] != (len(lower) - 1, len(upper) - 1):
        return False
    for (i, j), (i2, j2) in zip(parsed, parsed[1:]):
        if (i2 - i, j2 - j) not in ((1, 0), (0, 1), (1, 1)):
            return False
    if any(not statistic_leq(lower[i], upper[j]) for i, j in parsed):
        return False
    expected_lower = encode([lower[i] for i, _ in parsed])
    expected_upper = encode([upper[j] for _, j in parsed])
    return (
        witness.get('lower_extension') == expected_lower
        and witness.get('upper_extension') == expected_upper
        and witness.get('path_length') == len(parsed)
    )

def canonical_basis(rows: Iterable[int], ambient_dim: int, ledger: Ledger | None = None) -> tuple[int, ...]:
    if ambient_dim < 0:
        raise ValueError('negative ambient dimension')
    limit = 1 << ambient_dim
    basis: dict[int, int] = {}
    for row in rows:
        value = int(row)
        if value < 0 or value >= limit:
            raise ValueError('vector outside ambient space')
        if ledger is not None:
            ledger.discovery('rref_input_rows')
        x = value
        while x:
            pivot = x.bit_length() - 1
            if ledger is not None:
                ledger.discovery('rref_pivot_tests')
            if pivot in basis:
                x ^= basis[pivot]
                if ledger is not None:
                    ledger.discovery('rref_xors')
                continue
            basis[pivot] = x
            for other, y in list(basis.items()):
                if other != pivot and ((y >> pivot) & 1):
                    basis[other] = y ^ x
                    if ledger is not None:
                        ledger.discovery('rref_xors')
            break
    for pivot in sorted(basis):
        row = basis[pivot]
        for other in sorted(basis, reverse=True):
            if other != pivot and ((basis[other] >> pivot) & 1):
                basis[other] ^= row
                if ledger is not None:
                    ledger.discovery('rref_xors')
    result = tuple(basis[p] for p in sorted(basis, reverse=True))
    if ledger is not None:
        ledger.discovery('rref_output_rows', len(result))
    return result

def charged_span_contains(big: tuple[int, ...], small: tuple[int, ...], ledger: Ledger) -> bool:
    for vector in small:
        x = vector
        for row in big:
            ledger.discovery('subspace_inclusion_tests')
            reduced = min(x, x ^ row)
            if reduced != x:
                ledger.discovery('subspace_reduction_xors')
            x = reduced
        if x:
            return False
    return True

def enumerate_subspaces(ambient_dim: int, ledger: Ledger) -> tuple[tuple[int, ...], ...]:
    zero: tuple[int, ...] = ()
    seen = {zero}
    queue = [zero]
    while queue:
        basis = queue.pop(0)
        ledger.discovery('subspace_queue_pops')
        for vector in range(1, 1 << ambient_dim):
            ledger.discovery('subspace_vector_trials')
            candidate = canonical_basis((*basis, vector), ambient_dim, ledger)
            if candidate not in seen:
                seen.add(candidate)
                queue.append(candidate)
                ledger.discovery('subspaces_discovered')
    return tuple(sorted(seen))

def _is_compact_prefix(seq: Sequence[Statistic]) -> bool:
    return compactify(seq)[0] == tuple(seq)

def enumerate_compact_trajectories(ambient_dim: int, k: int, ledger: Ledger) -> tuple[tuple[Statistic, ...], ...]:
    if k < 0:
        raise ValueError('negative width cap')
    subspaces = enumerate_subspaces(ambient_dim, ledger)
    states = tuple(
        Statistic(left, right, value)
        for left in subspaces
        for right in subspaces
        for value in range(k + 1)
    )
    max_length = (2 * ambient_dim + 1) * (2 * k + 1)
    emitted: dict[tuple, tuple[Statistic, ...]] = {}

    def dfs(seq: tuple[Statistic, ...], target: tuple[int, ...]) -> None:
        ledger.discovery('trajectory_prefix_states')
        last = seq[-1]
        if last.left == target:
            key = trajectory_key(seq)
            if key not in emitted:
                emitted[key] = seq
                ledger.discovery('universe_entries')
        if len(seq) >= max_length:
            return
        for nxt in states:
            ledger.discovery('trajectory_extension_trials')
            if not charged_span_contains(nxt.left, last.left, ledger):
                continue
            if not charged_span_contains(last.right, nxt.right, ledger):
                continue
            # Every prefix L must stay below the required final L=R(first).
            if not charged_span_contains(target, nxt.left, ledger):
                continue
            candidate = (*seq, nxt)
            if not _is_compact_prefix(candidate):
                continue
            dfs(candidate, target)

    for first in states:
        ledger.discovery('trajectory_initial_states')
        if not charged_span_contains(first.right, first.left, ledger):
            # final L=first R and L is monotone, so first L must be contained in it.
            continue
        dfs((first,), first.right)
    return tuple(emitted[key] for key in sorted(emitted))

def minimize_generators(
    generators: Sequence[tuple[Statistic, ...]], ledger: Ledger
) -> tuple[tuple[tuple[Statistic, ...], ...], list[dict]]:
    unique_map = {trajectory_key(g): g for g in generators}
    ordered = tuple(unique_map[key] for key in sorted(unique_map))
    relation: dict[tuple[int, int], dict] = {}
    for i, lower in enumerate(ordered):
        for j, upper in enumerate(ordered):
            ledger.work('generator_pair_tests')
            witness = extension_preorder_witness(lower, upper, ledger)
            if witness is not None:
                relation[(i, j)] = witness

    retained_indices: list[int] = []
    for j in range(len(ordered)):
        strict_predecessors = [
            i for i in range(len(ordered))
            if i != j and (i, j) in relation and (j, i) not in relation
        ]
        equivalent_earlier = [i for i in range(j) if (i, j) in relation and (j, i) in relation]
        if not strict_predecessors and not equivalent_earlier:
            retained_indices.append(j)

    removals: list[dict] = []
    for j, removed in enumerate(ordered):
        if j in retained_indices:
            continue
        candidates = [i for i in retained_indices if (i, j) in relation]
        if not candidates:
            raise AssertionError('finite preorder minimization lost a predecessor')
        i = min(candidates, key=lambda idx: trajectory_key(ordered[idx]))
        removals.append({
            'removed': encode(removed),
            'retained': encode(ordered[i]),
            'witness': {'path': relation[(i, j)]['path'], 'path_length': relation[(i, j)]['path_length']},
            'reason': 'STRICTLY_COVERED' if (j, i) not in relation else 'EQUIVALENT_CANONICAL_REPRESENTATIVE',
        })
    retained = tuple(ordered[i] for i in retained_indices)
    return retained, removals

def up_k_closure(
    generators: Sequence[tuple[Statistic, ...]], ambient_dim: int, k: int, ledger: Ledger
) -> dict:
    for gamma in generators:
        if width(gamma) > k:
            raise ValueError('generator exceeds width cap')
    retained, removals = minimize_generators(generators, ledger)
    universe = enumerate_compact_trajectories(ambient_dim, k, ledger)
    entries: list[dict] = []
    for candidate in universe:
        ledger.work('closure_candidate_tests')
        chosen = None
        for source in retained:
            ledger.work('closure_generator_tests')
            witness = extension_preorder_witness(source, candidate, ledger)
            if witness is not None:
                chosen = (source, witness)
                break
        if chosen is not None:
            ledger.discovery('full_set_entries')
            source_index = retained.index(chosen[0])
            entries.append({
                'trajectory': encode(candidate),
                'source_generator_index': source_index,
                'witness': {'path': chosen[1]['path'], 'path_length': chosen[1]['path_length']},
            })
    return {
        'ambient_dim': ambient_dim,
        'k': k,
        'input_generators': [encode(g) for g in sorted(generators, key=trajectory_key)],
        'retained_generators': [encode(g) for g in retained],
        'removals': removals,
        'universe_size': len(universe),
        'entries': entries,
        'entry_count': len(entries),
        'ledger': ledger.snapshot(),
    }

def decode_trajectory_charged(raw: Sequence[dict], ambient_dim: int, ledger: Ledger, require_compact: bool = True) -> tuple[Statistic, ...]:
    if ambient_dim < 0 or not raw:
        raise ValueError('invalid trajectory')
    stats: list[Statistic] = []
    for item in raw:
        ledger.discovery('trajectory_input_statistics')
        left = canonical_basis(item['left'], ambient_dim, ledger)
        right = canonical_basis(item['right'], ambient_dim, ledger)
        value = int(item['value'])
        if value < 0:
            raise ValueError('negative lambda')
        stats.append(Statistic(left, right, value))
    gamma = tuple(stats)
    if gamma[0].right != gamma[-1].left:
        raise ValueError('endpoint condition')
    for a, b in zip(gamma, gamma[1:]):
        if not charged_span_contains(b.left, a.left, ledger):
            raise ValueError('left not increasing')
        if not charged_span_contains(a.right, b.right, ledger):
            raise ValueError('right not decreasing')
    if require_compact and compactify(gamma)[0] != gamma:
        raise ValueError('trajectory is not compact')
    return gamma
