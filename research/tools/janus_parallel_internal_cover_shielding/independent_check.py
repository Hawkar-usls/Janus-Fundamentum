#!/usr/bin/env python3
from __future__ import annotations
import hashlib, itertools, json, sys
from pathlib import Path

def lit_value(lit, a):
    v = a[abs(lit)]
    return v if lit > 0 else not v

def formula_value(clauses, a):
    return all(any(lit_value(l, a) for l in c) for c in clauses)

def boundary_projection_tautology(clause, boundary_vars):
    s = {l for l in clause if abs(l) in boundary_vars}
    return any(-l in s for l in s)

def internal_projection(clause, internal_vars):
    return tuple(l for l in clause if abs(l) in internal_vars)

def cover_sat(clauses, n_internal, n_boundary, tautology_safe):
    iv = set(range(1, n_internal + 1))
    bv = set(range(n_internal + 1, n_internal + n_boundary + 1))
    for bits in itertools.product([False, True], repeat=n_internal):
        a = {i + 1: bits[i] for i in range(n_internal)}
        ok = True
        for c in clauses:
            if tautology_safe and boundary_projection_tautology(c, bv):
                continue
            p = internal_projection(c, iv)
            if not p or not any(lit_value(l, a) for l in p):
                ok = False
                break
        if ok:
            return True, bits
    return False, None

def residual_table(clauses, n_internal, n_boundary, alpha):
    out = {}
    for bbits in itertools.product([False, True], repeat=n_boundary):
        a = {i + 1: alpha[i] for i in range(n_internal)}
        a.update({n_internal + j + 1: bbits[j] for j in range(n_boundary)})
        out[bbits] = formula_value(clauses, a)
    return out

def universal_branches(clauses, n_internal, n_boundary):
    out = []
    for alpha in itertools.product([False, True], repeat=n_internal):
        if all(residual_table(clauses, n_internal, n_boundary, alpha).values()):
            out.append(alpha)
    return out

def existential_relation(clauses, n_internal, n_boundary):
    rel = {}
    for bbits in itertools.product([False, True], repeat=n_boundary):
        yes = False
        for alpha in itertools.product([False, True], repeat=n_internal):
            a = {i + 1: alpha[i] for i in range(n_internal)}
            a.update({n_internal + j + 1: bbits[j] for j in range(n_boundary)})
            if formula_value(clauses, a):
                yes = True
                break
        rel[bbits] = yes
    return rel

def kappa(clauses, n_internal, n_boundary):
    rel = existential_relation(clauses, n_internal, n_boundary)
    if not all(rel.values()):
        return None
    alphas = list(itertools.product([False, True], repeat=n_internal))
    tables = {a: residual_table(clauses, n_internal, n_boundary, a) for a in alphas}
    bs = list(itertools.product([False, True], repeat=n_boundary))
    for k in range(1, len(alphas) + 1):
        for ss in itertools.combinations(alphas, k):
            if all(any(tables[a][b] for a in ss) for b in bs):
                return k
    raise AssertionError("TRUE existential relation must have finite branch cover")

def check_instance(clauses, ni, nb):
    safe, witness = cover_sat(clauses, ni, nb, True)
    naive, _ = cover_sat(clauses, ni, nb, False)
    ub = universal_branches(clauses, ni, nb)
    kap = kappa(clauses, ni, nb)
    rel = existential_relation(clauses, ni, nb)
    return {
        "safe_cover_sat": safe,
        "naive_cover_sat": naive,
        "safe_witness": witness,
        "universal_branch_count": len(ub),
        "kappa": "INFINITY" if kap is None else kap,
        "R_C": {"".join("1" if x else "0" for x in b): v for b, v in rel.items()},
        "safe_equivalence": safe == bool(ub) == (kap == 1),
    }

def normalized_clauses(ni=2, nb=2, max_width=3):
    n = ni + nb
    out = []
    for w in range(1, max_width + 1):
        for vs in itertools.combinations(range(1, n + 1), w):
            for signs in itertools.product([1, -1], repeat=w):
                out.append(tuple(v * s for v, s in zip(vs, signs)))
    return out

def exhaustive_normalized():
    atoms = normalized_clauses()
    checked = 0
    for k in (1, 2, 3):
        for f in itertools.combinations(atoms, k):
            checked += 1
            r = check_instance(f, 2, 2)
            if not r["safe_equivalence"] or r["safe_cover_sat"] != r["naive_cover_sat"]:
                return checked, {"formula": f, "result": r}
    return checked, None

def controls():
    cases = {
        "universal_branch": ([(1, 2), (1, -2)], 1, 1),
        "distributed_shielding": ([(1, 2), (-1, -2)], 1, 1),
        "semantic_signal": ([(1, 2), (-1, 2)], 1, 1),
        "trivial_false": ([(1,), (-1,)], 1, 1),
        "boundary_tautology_counterexample_to_naive_cover": ([(2, -2)], 1, 1),
    }
    out = {k: check_instance(*v) for k, v in cases.items()}
    assert out["universal_branch"]["safe_cover_sat"] and out["universal_branch"]["kappa"] == 1
    assert not out["distributed_shielding"]["safe_cover_sat"] and out["distributed_shielding"]["kappa"] == 2
    assert set(out["semantic_signal"]["R_C"].values()) == {False, True}
    assert not any(out["trivial_false"]["R_C"].values())
    t = out["boundary_tautology_counterexample_to_naive_cover"]
    assert t["safe_cover_sat"] is True and t["naive_cover_sat"] is False and t["kappa"] == 1
    return out

def digest(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def main():
    checked, failure = exhaustive_normalized()
    cs = controls()
    result = {
        "artifact_id": "JANUS-PARALLEL-INTERNAL-COVER-SHIELDING-INDEPENDENT-CHECK-2026-09-18-v1.0",
        "verdict": "PASS" if failure is None else "FAIL",
        "lineage": "PARALLEL_FROM_MAIN__NO_MANTEQUILLA_BRANCH_MUTATION",
        "theorem_checked": "U_C_star SAT iff exists universal residual branch iff kappa_C=1",
        "normalized_corollary_checked": True,
        "exhaustive_normalized_formulae_checked": checked,
        "failure": failure,
        "controls": cs,
        "checker_role": "independent executable regression/model checker; mathematical proof lives in proof_attempts and is not replaced by finite enumeration",
        "firewall": {
            "general_sat_in_p": "NOT_PROVED",
            "p_vs_np": "OPEN",
            "internal_cover_sat_is_not_claimed_polynomial_in_general": True,
        },
    }
    result["sha256"] = digest(result)
    print(json.dumps({"verdict": result["verdict"], "checked": checked, "sha256": result["sha256"]}, sort_keys=True))
    if len(sys.argv) > 1:
        Path(sys.argv[1]).parent.mkdir(parents=True, exist_ok=True)
        Path(sys.argv[1]).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failure is not None:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
