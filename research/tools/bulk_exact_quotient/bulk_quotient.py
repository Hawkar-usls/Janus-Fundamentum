from collections import defaultdict

TAUTOLOGY = object()

def normalize_clause(clause):
    s = {int(x) for x in clause if int(x) != 0}
    if any(-x in s for x in s):
        return TAUTOLOGY
    return tuple(sorted(s, key=lambda x: (abs(x), x < 0)))

def normalize_formula(clauses):
    sat = dead = 0
    residual = []
    for clause in clauses:
        c = normalize_clause(clause)
        if c is TAUTOLOGY:
            sat += 1
        elif not c:
            dead += 1
        else:
            residual.append(c)
    residual.sort()
    return (sat, dead, tuple(residual))

def assign_state(state, var, value):
    sat, dead, residual = state
    out = []
    sat_lit = var if value else -var
    for clause in residual:
        if sat_lit in clause:
            sat += 1
            continue
        c = tuple(l for l in clause if abs(l) != var)
        if not c:
            dead += 1
        else:
            out.append(c)
    out.sort()
    return (sat, dead, tuple(out))

def advance(states, var):
    nxt = defaultdict(int)
    for state, multiplicity in states.items():
        nxt[assign_state(state, var, False)] += multiplicity
        nxt[assign_state(state, var, True)] += multiplicity
    return dict(nxt)

def run_bulk(clauses, variable_order, boundary_len=None):
    states = {normalize_formula(clauses): 1}
    layers = [{"layer": 0, "states": 1, "mass": 1}]
    edges = 0
    boundary_snapshot = None
    for i, var in enumerate(variable_order, start=1):
        edges += 2 * len(states)
        states = advance(states, var)
        layers.append({
            "layer": i,
            "var": var,
            "states": len(states),
            "mass": sum(states.values()),
        })
        if boundary_len is not None and i == boundary_len:
            boundary_snapshot = dict(states)
    if boundary_len == 0:
        boundary_snapshot = {normalize_formula(clauses): 1}
    return states, layers, edges, boundary_snapshot

def terminal_histogram(states, clause_count):
    hist = [0] * (clause_count + 1)
    for (sat, dead, residual), multiplicity in states.items():
        if residual:
            raise ValueError("terminal state still has residual clauses")
        if sat + dead != clause_count:
            raise ValueError("clause accounting mismatch")
        hist[sat] += multiplicity
    return hist

def solve_histogram_bulk(clauses, boundary, internal):
    order = list(boundary) + list(internal)
    states, layers, edges, boundary_states = run_bulk(
        clauses, order, boundary_len=len(boundary)
    )
    return {
        "histogram": terminal_histogram(states, len(clauses)),
        "layers": layers,
        "edges": edges,
        "peak_states": max(x["states"] for x in layers),
        "boundary_states": boundary_states,
    }
