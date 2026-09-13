from collections import Counter, defaultdict, deque

from research.tools.query_factorized_quotient.query_factorized import (
    TAUTOLOGY, UNSAT_STATE, assign_formula, normalize_clause, normalize_formula
)


def component_vars(component):
    return {abs(lit) for clause in component for lit in clause}


def split_internal_factors(formula, boundary):
    if formula in (UNSAT_STATE, ()):
        return []
    boundary = set(boundary)
    internal_to_clauses = defaultdict(list)
    for i, clause in enumerate(formula):
        for lit in clause:
            v = abs(lit)
            if v not in boundary:
                internal_to_clauses[v].append(i)
    unseen = set(range(len(formula)))
    factors = []
    while unseen:
        seed = unseen.pop()
        q = deque([seed])
        idxs = {seed}
        while q:
            ci = q.popleft()
            for lit in formula[ci]:
                v = abs(lit)
                if v in boundary:
                    continue
                for cj in internal_to_clauses.get(v, ()): 
                    if cj in unseen:
                        unseen.remove(cj)
                        idxs.add(cj)
                        q.append(cj)
        factors.append(tuple(formula[i] for i in sorted(idxs)))
    return factors


def internal_unate_projection(component, boundary):
    boundary = set(boundary)
    internal = component_vars(component) - boundary
    if not internal:
        return normalize_formula(component)
    signs = defaultdict(set)
    for clause in component:
        for lit in clause:
            v = abs(lit)
            if v in internal:
                signs[v].add(lit > 0)
    if any(len(s) > 1 for s in signs.values()):
        return None
    kept = [clause for clause in component
            if not any(abs(lit) in internal for lit in clause)]
    return normalize_formula(kept)

def dp_project_2cnf(component, boundary):
    if max((len(c) for c in component), default=0) > 2:
        return None, {}
    boundary = set(boundary)
    state = normalize_formula(component)
    if state == UNSAT_STATE:
        return UNSAT_STATE, {"dp_unsat": 1}
    internal = sorted(component_vars(component) - boundary)
    stats = Counter()
    stats["dp_initial_clauses"] = len(state)
    stats["dp_peak_clauses"] = len(state)
    for var in internal:
        pos = [c for c in state if var in c]
        neg = [c for c in state if -var in c]
        rest = [c for c in state if var not in c and -var not in c]
        generated = []
        for p in pos:
            for n in neg:
                raw = tuple(l for l in p if l != var) + tuple(l for l in n if l != -var)
                c = normalize_clause(raw)
                if c is TAUTOLOGY:
                    stats["dp_tautological_resolvents"] += 1
                    continue
                if not c:
                    return UNSAT_STATE, {**dict(stats), "dp_unsat": 1}
                generated.append(c)
        state = normalize_formula(rest + generated)
        stats["dp_eliminated_vars"] += 1
        stats["dp_generated_resolvents"] += len(generated)
        stats["dp_peak_clauses"] = max(stats["dp_peak_clauses"], len(state))
    return state, dict(stats)


def project_open_state(formula, boundary):
    if formula == UNSAT_STATE:
        return UNSAT_STATE, {"unsat": 1}
    boundary = list(boundary)
    kept = []
    stats = Counter()
    for factor in split_internal_factors(formula, boundary):
        internal = component_vars(factor) - set(boundary)
        if not internal:
            kept.extend(factor)
            stats["boundary_only_factors"] += 1
            continue
        unate = internal_unate_projection(factor, boundary)
        if unate is not None:
            if unate == UNSAT_STATE:
                return UNSAT_STATE, {**dict(stats), "unate_unsat": 1}
            kept.extend(unate)
            stats["open_unate_projected"] += 1
            continue
        dp, dp_stats = dp_project_2cnf(factor, boundary)
        if dp is not None:
            stats.update(dp_stats)
            if dp == UNSAT_STATE:
                stats["open_2cnf_unsat"] += 1
                return UNSAT_STATE, dict(stats)
            kept.extend(dp)
            stats["open_2cnf_projected"] += 1
            continue
        kept.extend(factor)
        stats["open_unresolved_kept"] += 1
    return normalize_formula(kept), dict(stats)


def run_open_message_quotient(clauses, boundary):
    initial = normalize_formula(clauses)
    initial, init_stats = project_open_state(initial, boundary)
    states = {initial: 1}
    layers = [{"layer": 0, "states": 1, "mass": 1,
               "projection": init_stats}]
    totals = Counter(init_stats)
    for i, var in enumerate(boundary):
        remaining = list(boundary[i + 1:])
        raw = defaultdict(int)
        step = Counter()
        for state, mass in states.items():
            for value in (False, True):
                child = assign_formula(state, var, value)
                child, st = project_open_state(child, remaining)
                raw[child] += mass
                step.update(st)
        states = dict(raw)
        totals.update(step)
        layers.append({"layer": i + 1, "var": var,
                       "states": len(states), "mass": sum(states.values()),
                       "projection": dict(step)})
    return {"states": states, "layers": layers,
            "stats": dict(totals),
            "peak_states": max(x["states"] for x in layers)}