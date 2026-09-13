from itertools import combinations


def normalize_clause(clause):
    return tuple(sorted(clause, key=lambda x: (abs(x), x)))


def recognize_complete_negative_triples(horn_clauses):
    clauses = tuple(normalize_clause(c) for c in horn_clauses)
    if not clauses:
        return None
    if any(len(c) != 3 for c in clauses):
        return None
    if any(any(lit >= 0 for lit in c) for c in clauses):
        return None
    if any(len({abs(l) for l in c}) != 3 for c in clauses):
        return None
    variables = tuple(sorted({abs(l) for c in clauses for l in c}))
    expected_count = len(variables) * (len(variables)-1) * (len(variables)-2) // 6
    unique = {tuple(sorted(abs(l) for l in c)) for c in clauses}
    if len(clauses) != expected_count or len(unique) != expected_count:
        return None
    expected = set(combinations(variables, 3))
    if unique != expected:
        return None
    return {
        "kind": "AT_MOST_K",
        "variables": variables,
        "k": 2,
        "certificate": {
            "uniform_width": 3,
            "all_negative": True,
            "complete_triple_count": expected_count,
        },
    }


def eval_cardinality(carrier, assignment):
    total = sum(int(bool(assignment.get(v, False))) for v in carrier["variables"])
    return total <= carrier["k"]


def update_cardinality(carrier, assignment):
    remaining = []
    spent = 0
    for v in carrier["variables"]:
        if v in assignment:
            spent += int(bool(assignment[v]))
        else:
            remaining.append(v)
    k = carrier["k"] - spent
    if k < 0:
        return {"kind": "FALSE"}
    if k >= len(remaining):
        return {"kind": "TRUE"}
    return {"kind": "AT_MOST_K", "variables": tuple(remaining), "k": k}


def verify_neq_pairs(affine_rows, source_vars, falsity_vars):
    want = set()
    for x, c in zip(source_vars, falsity_vars):
        want.add(((1 << (x-1)) | (1 << (c-1)), 1))
    return set(affine_rows) == want and len(affine_rows) == len(want)


def compile_c023_dense_image(horn_clauses, affine_rows, source_vars, falsity_vars):
    if len(source_vars) != len(falsity_vars):
        return None
    if not verify_neq_pairs(affine_rows, source_vars, falsity_vars):
        return None
    carrier = recognize_complete_negative_triples(horn_clauses)
    if carrier is None or tuple(carrier["variables"]) != tuple(sorted(falsity_vars)):
        return None
    carrier["source_variables"] = tuple(source_vars)
    carrier["morph"] = "COMPLETE_NEGATIVE_3_UNIFORM_HORN_TO_AT_MOST_2"
    return carrier
