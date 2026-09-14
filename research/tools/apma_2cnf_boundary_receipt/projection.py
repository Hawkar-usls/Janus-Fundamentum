from __future__ import annotations

import hashlib
import json

from research.tools.apma_ss_provenance.apma_ss_controller import solve_source

SCHEMA = "JANUS_TRUMP_EXACT_2CNF_BOUNDARY_RECEIPT_V1"


def _lit_key(x):
    return (abs(int(x)), int(x) < 0)


def canon_2cnf(raw):
    out = set()
    for clause in raw:
        s = {int(x) for x in clause}
        if any(-x in s for x in s):
            continue
        if len(s) > 2:
            raise ValueError("NOT_2CNF")
        c = tuple(sorted(s, key=_lit_key))
        if len(c) == 0:
            return ((),)
        out.add(c)
    return tuple(sorted(out, key=lambda c: (len(c), tuple(_lit_key(x) for x in c))))


def vars_of(clauses):
    return {abs(int(l)) for c in clauses for l in c}


def _canon_payload(receipt):
    return {
        "schema": receipt["schema"],
        "n": int(receipt["n"]),
        "boundary": list(receipt["boundary"]),
        "internal_elimination_order": list(receipt["internal_elimination_order"]),
        "projected_clauses": [list(c) for c in receipt["projected_clauses"]],
    }


def receipt_sha256(receipt):
    raw = json.dumps(_canon_payload(receipt), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def eliminate_var_2cnf(clauses, x):
    clauses = canon_2cnf(clauses)
    x = int(x)
    if () in clauses:
        return clauses
    pos = [c for c in clauses if x in c]
    neg = [c for c in clauses if -x in c]
    rest = [c for c in clauses if x not in c and -x not in c]
    resolvents = []
    for cp in pos:
        lp = [l for l in cp if l != x]
        for cn in neg:
            ln = [l for l in cn if l != -x]
            r = tuple(lp + ln)
            s = set(r)
            if any(-l in s for l in s):
                continue
            if len(s) > 2:
                raise AssertionError("2CNF_WIDTH_INVARIANT_BROKEN")
            resolvents.append(tuple(s))
    return canon_2cnf(tuple(rest) + tuple(resolvents))


def project_2cnf(source, n, boundary):
    clauses = canon_2cnf(source)
    n = int(n)
    boundary = tuple(sorted({int(v) for v in boundary}))
    if any(v < 1 or v > n for v in boundary):
        raise ValueError("BOUNDARY_OUT_OF_RANGE")
    source_vars = vars_of(clauses)
    if any(v > n for v in source_vars):
        raise ValueError("SOURCE_VAR_OUT_OF_RANGE")
    internal = tuple(sorted(source_vars - set(boundary)))
    current = clauses
    max_clause_count = len(current)
    resolution_pairs = 0
    for x in internal:
        if () in current:
            break
        pos = sum(1 for c in current if x in c)
        neg = sum(1 for c in current if -x in c)
        resolution_pairs += pos * neg
        current = eliminate_var_2cnf(current, x)
        max_clause_count = max(max_clause_count, len(current))
    if vars_of(current) - set(boundary):
        raise AssertionError("INTERNAL_VARIABLE_SURVIVED_PROJECTION")
    receipt = {
        "schema": SCHEMA,
        "n": n,
        "boundary": boundary,
        "internal_elimination_order": internal,
        "projected_clauses": current,
        "metrics": {
            "source_clause_count": len(clauses),
            "projected_clause_count": len(current),
            "max_intermediate_clause_count": max_clause_count,
            "resolution_pair_count": resolution_pairs,
        },
    }
    receipt["receipt_sha256"] = receipt_sha256(receipt)
    return receipt


def verify_receipt(source, n, boundary, receipt):
    if receipt.get("schema") != SCHEMA:
        return {"status": "REJECT", "reason": "SCHEMA"}
    actual = receipt.get("receipt_sha256")
    if not isinstance(actual, str) or actual != receipt_sha256(receipt):
        return {"status": "REJECT", "reason": "RECEIPT_HASH"}
    expected = project_2cnf(source, n, boundary)
    fields = (
        "schema", "n", "boundary", "internal_elimination_order",
        "projected_clauses", "receipt_sha256",
    )
    if any(receipt.get(k) != expected.get(k) for k in fields):
        return {"status": "REJECT", "reason": "RECOMPUTATION_MISMATCH"}
    return {"status": "ADMIT", "receipt": expected}


def boundary_satisfies(receipt, assignment):
    projected = receipt["projected_clauses"]
    if () in projected:
        return False
    beta = {int(v): bool(b) for v, b in assignment.items()}
    for v in receipt["boundary"]:
        if v not in beta:
            raise ValueError("BOUNDARY_ASSIGNMENT_INCOMPLETE")
    for c in projected:
        if not any(beta[abs(l)] == (l > 0) for l in c):
            return False
    return True


def _condition_2cnf(source, assignment):
    out = []
    for c in canon_2cnf(source):
        if c == ():
            return None
        rem = []
        sat = False
        for lit in c:
            v = abs(lit)
            if v in assignment:
                if bool(assignment[v]) == (lit > 0):
                    sat = True
                    break
            else:
                rem.append(lit)
        if sat:
            continue
        if not rem:
            return None
        out.append(tuple(rem))
    return canon_2cnf(out)


def reconstruct_extension(source, n, receipt, boundary_assignment):
    if not boundary_satisfies(receipt, boundary_assignment):
        return {"status": "REJECT_BOUNDARY", "witness": None}
    beta = {int(v): bool(b) for v, b in boundary_assignment.items()}
    conditioned = _condition_2cnf(source, beta)
    if conditioned is None:
        return {"status": "INTERNAL_PROJECTION_MISMATCH", "witness": None}
    solved = solve_source(conditioned, int(n), "2CNF")
    if not solved["sat"]:
        return {"status": "INTERNAL_PROJECTION_MISMATCH", "witness": None}
    witness = {i: bool(solved["witness"].get(i, False)) for i in range(1, int(n) + 1)}
    witness.update(beta)
    if not all(any(witness[abs(l)] == (l > 0) for l in c) for c in canon_2cnf(source)):
        return {"status": "INTERNAL_ROOT_REPLAY_MISMATCH", "witness": None}
    return {"status": "CERTIFIED_EXTENSION", "witness": witness}
