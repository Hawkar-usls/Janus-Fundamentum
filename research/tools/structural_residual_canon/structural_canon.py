from collections import Counter, defaultdict
import hashlib

from research.tools.bulk_exact_quotient.bulk_quotient import (
    normalize_formula, assign_state, advance, terminal_histogram
)

def residual_vars(state):
    out = set()
    for clause in state[2]:
        out.update(abs(l) for l in clause)
    return out

def coarse_key(state, pinned):
    sat, dead, residual = state
    lengths = tuple(sorted(Counter(map(len, residual)).items()))
    vars_now = residual_vars(state)
    internal_count = len(vars_now - set(pinned))
    pinned_occ = tuple(v for v in sorted(pinned) if v in vars_now)
    return sat, dead, len(residual), lengths, internal_count, pinned_occ

def _h(obj):
    return hashlib.sha256(repr(obj).encode("utf-8")).hexdigest()

def _initial_colors(state, pinned):
    vars_now = residual_vars(state)
    vcol = {v: (f"P:{v}" if v in pinned else "I") for v in vars_now}
    ccol = {i: f"C:{len(c)}" for i, c in enumerate(state[2])}
    return vcol, ccol

def refined_colors(state, pinned):
    residual = state[2]
    vcol, ccol = _initial_colors(state, pinned)
    var_to_occ = defaultdict(list)
    for ci, clause in enumerate(residual):
        for lit in clause:
            var_to_occ[abs(lit)].append((ci, 1 if lit > 0 else -1))
    rounds = len(vcol) + len(ccol) + 2
    for _ in range(rounds):
        new_v = {}
        for v in vcol:
            neigh = sorted((sgn, ccol[ci]) for ci, sgn in var_to_occ[v])
            new_v[v] = _h(("V", vcol[v], tuple(neigh)))
        new_c = {}
        for ci, clause in enumerate(residual):
            neigh = sorted((1 if lit > 0 else -1, vcol[abs(lit)]) for lit in clause)
            new_c[ci] = _h(("C", ccol[ci], tuple(neigh)))
        vcol, ccol = new_v, new_c
    return vcol, ccol

def apply_mapping(residual, mapping):
    out = []
    for clause in residual:
        mapped = []
        for lit in clause:
            v = mapping.get(abs(lit), abs(lit))
            mapped.append(v if lit > 0 else -v)
        out.append(tuple(sorted(mapped, key=lambda x: (abs(x), x < 0))))
    return tuple(sorted(out))

def try_verified_renaming(a, b, pinned):
    pinned = set(pinned)
    if coarse_key(a, pinned) != coarse_key(b, pinned):
        return None
    va, ca = refined_colors(a, pinned)
    vb, cb = refined_colors(b, pinned)
    if Counter(ca.values()) != Counter(cb.values()):
        return None
    inta = sorted(set(va) - pinned)
    intb = sorted(set(vb) - pinned)
    if Counter(va[v] for v in inta) != Counter(vb[v] for v in intb):
        return None
    mapping = {v: v for v in pinned if v in va or v in vb}
    colors = sorted(set(va[v] for v in inta))
    for color in colors:
        aa = sorted(v for v in inta if va[v] == color)
        bb = sorted(v for v in intb if vb[v] == color)
        if len(aa) != len(bb):
            return None
        mapping.update(zip(aa, bb))
    if apply_mapping(a[2], mapping) != b[2]:
        return None
    return mapping

def verify_explicit_mapping(a, b, mapping):
    if a[:2] != b[:2]:
        return False
    return apply_mapping(a[2], mapping) == b[2]

def merge_verified_isomorphic(states, pinned):
    buckets = defaultdict(list)
    out = {}
    attempts = verified = merges = 0
    for state, multiplicity in states.items():
        key = coarse_key(state, pinned)
        merged = False
        for rep in buckets[key]:
            attempts += 1
            mapping = try_verified_renaming(state, rep, pinned)
            if mapping is None:
                continue
            verified += 1
            out[rep] += multiplicity
            merges += 1
            merged = True
            break
        if not merged:
            buckets[key].append(state)
            out[state] = multiplicity
    return out, {"attempts": attempts, "verified": verified, "merges": merges}

def run_boundary_structural(clauses, boundary):
    states = {normalize_formula(clauses): 1}
    layers = [{"layer": 0, "states": 1, "mass": 1}]
    totals = Counter()
    for i, var in enumerate(boundary):
        raw = defaultdict(int)
        for state, multiplicity in states.items():
            raw[assign_state(state, var, False)] += multiplicity
            raw[assign_state(state, var, True)] += multiplicity
        pinned = list(boundary[i + 1:])
        states, stats = merge_verified_isomorphic(dict(raw), pinned)
        totals.update(stats)
        layers.append({"layer": i + 1, "var": var, "generated": len(raw),
                       "states": len(states), "mass": sum(states.values()),
                       **stats})
    return states, layers, dict(totals)

def finish_internal_exact(boundary_states, internal, clause_count):
    states = dict(boundary_states)
    for var in internal:
        states = advance(states, var)
    return terminal_histogram(states, clause_count)

def solve_structural_boundary(clauses, boundary, internal):
    boundary_states, layers, stats = run_boundary_structural(clauses, boundary)
    hist = finish_internal_exact(boundary_states, internal, len(clauses))
    return {
        "histogram": hist,
        "boundary_states": boundary_states,
        "layers": layers,
        "merge_stats": stats,
        "peak_boundary_states": max(x["states"] for x in layers),
    }
