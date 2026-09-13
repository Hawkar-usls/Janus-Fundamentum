from collections import Counter, defaultdict, deque

TAUTOLOGY = object()
UNSAT_STATE = ("UNSAT",)

def normalize_clause(clause):
    s = {int(x) for x in clause if int(x) != 0}
    if any(-x in s for x in s):
        return TAUTOLOGY
    return tuple(sorted(s, key=lambda x: (abs(x), x < 0)))

def normalize_formula(clauses):
    out = set()
    for clause in clauses:
        c = normalize_clause(clause)
        if c is TAUTOLOGY:
            continue
        if not c:
            return UNSAT_STATE
        out.add(c)
    return tuple(sorted(out))

def assign_formula(state, var, value):
    if state == UNSAT_STATE:
        return UNSAT_STATE
    sat_lit = var if value else -var
    out = []
    for clause in state:
        if sat_lit in clause:
            continue
        c = tuple(l for l in clause if abs(l) != var)
        if not c:
            return UNSAT_STATE
        out.append(c)
    return normalize_formula(out)

def split_components(formula):
    if formula == UNSAT_STATE:
        return []
    if not formula:
        return []
    var_to_clauses = defaultdict(list)
    for i, clause in enumerate(formula):
        for lit in clause:
            var_to_clauses[abs(lit)].append(i)
    unseen = set(range(len(formula)))
    comps = []
    while unseen:
        seed = unseen.pop()
        q = deque([seed])
        idxs = {seed}
        while q:
            ci = q.popleft()
            for lit in formula[ci]:
                for cj in var_to_clauses[abs(lit)]:
                    if cj in unseen:
                        unseen.remove(cj)
                        idxs.add(cj)
                        q.append(cj)
        comps.append(tuple(formula[i] for i in sorted(idxs)))
    return comps

def component_vars(component):
    return {abs(l) for c in component for l in c}

def is_unate(component):
    signs = defaultdict(set)
    for clause in component:
        for lit in clause:
            signs[abs(lit)].add(lit > 0)
    return all(len(s) <= 1 for s in signs.values())

def _implications_2sat(component):
    graph = defaultdict(set)
    rev = defaultdict(set)
    nodes = set()
    def add(a, b):
        graph[a].add(b); rev[b].add(a)
        nodes.add(a); nodes.add(b)
    for clause in component:
        if len(clause) > 2:
            return None
        if len(clause) == 1:
            a = clause[0]
            add(-a, a)
        else:
            a, b = clause
            add(-a, b); add(-b, a)
    return graph, rev, nodes

def two_sat_satisfiable(component):
    built = _implications_2sat(component)
    if built is None:
        return None
    graph, rev, nodes = built
    seen = set(); order = []
    for root in list(nodes):
        if root in seen:
            continue
        stack = [(root, 0)]
        seen.add(root)
        while stack:
            v, phase = stack.pop()
            if phase == 1:
                order.append(v); continue
            stack.append((v, 1))
            for w in graph.get(v, ()):
                if w not in seen:
                    seen.add(w); stack.append((w, 0))
    comp_id = {}; cid = 0
    for root in reversed(order):
        if root in comp_id:
            continue
        q = [root]; comp_id[root] = cid
        while q:
            v = q.pop()
            for w in rev.get(v, ()):
                if w not in comp_id:
                    comp_id[w] = cid; q.append(w)
        cid += 1
    vars_ = {abs(x) for x in nodes}
    return not any(comp_id.get(v) == comp_id.get(-v) for v in vars_)

from research.tools.structural_residual_canon.structural_canon import (
    coarse_key, routing_signature, try_verified_renaming
)

def factor_reduce(state, remaining_boundary):
    if state == UNSAT_STATE:
        return UNSAT_STATE, {"unsat": 1}
    remaining = set(remaining_boundary)
    kept = []
    stats = Counter()
    for comp in split_components(state):
        if component_vars(comp) & remaining:
            kept.extend(comp); stats["open_kept"] += 1
            continue
        if is_unate(comp):
            stats["closed_unate_sat_dropped"] += 1
            continue
        if max((len(c) for c in comp), default=0) <= 2:
            sat = two_sat_satisfiable(comp)
            if sat:
                stats["closed_2sat_sat_dropped"] += 1
                continue
            stats["closed_2sat_unsat"] += 1
            return UNSAT_STATE, dict(stats)
        kept.extend(comp); stats["closed_unresolved_kept"] += 1
    return normalize_formula(kept), dict(stats)

def _wrap(residual):
    return (0, 0, residual)

def merge_query_states(states, pinned):
    out = {}
    buckets = defaultdict(list)
    stats = Counter()
    for state, mass in states.items():
        if state == UNSAT_STATE:
            out[state] = out.get(state, 0) + mass
            continue
        key = (coarse_key(_wrap(state), set(pinned)), routing_signature(_wrap(state), set(pinned)))
        merged = False
        for rep in buckets[key]:
            stats["iso_attempts"] += 1
            mapping = try_verified_renaming(_wrap(state), _wrap(rep), set(pinned))
            if mapping is None:
                continue
            out[rep] += mass
            stats["iso_merges"] += 1
            merged = True
            break
        if not merged:
            buckets[key].append(state)
            out[state] = out.get(state, 0) + mass
    return out, dict(stats)

def run_query_quotient(clauses, boundary):
    initial = normalize_formula(clauses)
    initial, init_stats = factor_reduce(initial, boundary)
    states = {initial: 1}
    layers = [{"layer": 0, "states": 1, "mass": 1, "reduction": init_stats}]
    totals = Counter(init_stats)
    for i, var in enumerate(boundary):
        remaining = list(boundary[i + 1:])
        raw = defaultdict(int)
        step_reduce = Counter()
        for state, mass in states.items():
            for value in (False, True):
                child = assign_formula(state, var, value)
                child, red = factor_reduce(child, remaining)
                raw[child] += mass
                step_reduce.update(red)
        states, merge_stats = merge_query_states(dict(raw), remaining)
        totals.update(step_reduce); totals.update(merge_stats)
        layers.append({"layer": i + 1, "var": var,
                       "generated_keys": len(raw), "states": len(states),
                       "mass": sum(states.values()),
                       "reduction": dict(step_reduce), **merge_stats})
    return {"states": states, "layers": layers, "stats": dict(totals),
            "peak_states": max(x["states"] for x in layers)}

def final_query_classes(result):
    counts = Counter()
    for state, mass in result["states"].items():
        if state == UNSAT_STATE:
            counts["UNSAT_CERTIFIED"] += mass
        elif not state:
            counts["SAT_CERTIFIED"] += mass
        else:
            counts["UNRESOLVED"] += mass
    return dict(counts)
