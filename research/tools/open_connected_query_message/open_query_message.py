from collections import Counter, defaultdict, deque

from research.tools.query_factorized_quotient.query_factorized import (
    TAUTOLOGY, UNSAT_STATE, assign_formula, component_vars, is_unate,
    merge_query_states, normalize_clause, normalize_formula
)

def split_boundary_factors(formula, boundary):
    if formula == UNSAT_STATE or not formula:
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
                        unseen.remove(cj); idxs.add(cj); q.append(cj)
        factors.append(tuple(formula[i] for i in sorted(idxs)))
    return factors

def project_unate_factor(factor, boundary):
    boundary = set(boundary)
    if not is_unate(factor):
        return None, {}
    internal = component_vars(factor) - boundary
    if not internal:
        return normalize_formula(factor), {"unate_pure_boundary": 1}
    kept = []
    for clause in factor:
        if all(abs(lit) in boundary for lit in clause):
            kept.append(clause)
    return normalize_formula(kept), {
        "unate_projected": 1,
        "unate_internal_eliminated": len(internal),
        "unate_boundary_clauses": len(kept),
    }

def _clause_set_after_resolution(formula, var):
    pos = [c for c in formula if var in c]
    neg = [c for c in formula if -var in c]
    rest = {c for c in formula if var not in c and -var not in c}
    added = 0
    for p in pos:
        for n in neg:
            lits = (set(p) - {var}) | (set(n) - {-var})
            c = normalize_clause(lits)
            if c is TAUTOLOGY:
                continue
            if not c:
                return UNSAT_STATE, added
            if c not in rest:
                rest.add(c); added += 1
    return tuple(sorted(rest)), added

def project_2cnf_factor(factor, boundary):
    if any(len(c) > 2 for c in factor):
        return None, {}
    boundary = set(boundary)
    formula = tuple(factor)
    internal = sorted(component_vars(factor) - boundary)
    total_added = 0
    for var in internal:
        formula, added = _clause_set_after_resolution(formula, var)
        total_added += added
        if formula == UNSAT_STATE:
            return UNSAT_STATE, {
                "two_cnf_projected": 1,
                "two_cnf_internal_eliminated": len(internal),
                "two_cnf_resolvents_added": total_added,
                "two_cnf_projection_unsat": 1,
            }
    return normalize_formula(formula), {
        "two_cnf_projected": 1,
        "two_cnf_internal_eliminated": len(internal),
        "two_cnf_resolvents_added": total_added,
        "two_cnf_boundary_clauses": len(formula),
    }

def project_factor(factor, boundary):
    vars_ = component_vars(factor)
    internal = vars_ - set(boundary)
    if not internal:
        return normalize_formula(factor), {"pure_boundary_factor": 1}
    projected, stats = project_unate_factor(factor, boundary)
    if projected is not None:
        return projected, stats
    projected, stats = project_2cnf_factor(factor, boundary)
    if projected is not None:
        return projected, stats
    return None, {"open_general_factor_kept": 1}

def message_reduce(state, remaining_boundary):
    if state == UNSAT_STATE:
        return UNSAT_STATE, {"unsat_input": 1}
    kept = []
    totals = Counter()
    for factor in split_boundary_factors(state, remaining_boundary):
        projected, stats = project_factor(factor, remaining_boundary)
        totals.update(stats)
        if projected is None:
            kept.extend(factor)
            continue
        if projected == UNSAT_STATE:
            totals["projection_unsat"] += 1
            return UNSAT_STATE, dict(totals)
        kept.extend(projected)
        if not projected:
            totals["projected_true_factor_dropped"] += 1
    return normalize_formula(kept), dict(totals)

def run_open_message_quotient(clauses, boundary):
    initial = normalize_formula(clauses)
    initial, init_stats = message_reduce(initial, boundary)
    states = {initial: 1}
    totals = Counter(init_stats)
    layers = [{"layer": 0, "states": 1, "mass": 1,
               "reduction": init_stats}]
    for i, var in enumerate(boundary):
        remaining = list(boundary[i + 1:])
        raw = defaultdict(int)
        step_stats = Counter()
        for state, mass in states.items():
            for value in (False, True):
                child = assign_formula(state, var, value)
                child, stats = message_reduce(child, remaining)
                raw[child] += mass
                step_stats.update(stats)
        states, merge_stats = merge_query_states(dict(raw), remaining)
        totals.update(step_stats); totals.update(merge_stats)
        layers.append({"layer": i + 1, "var": var,
                       "generated_keys": len(raw), "states": len(states),
                       "mass": sum(states.values()),
                       "reduction": dict(step_stats), **merge_stats})
    return {"states": states, "layers": layers,
            "stats": dict(totals),
            "peak_states": max(x["states"] for x in layers)}
