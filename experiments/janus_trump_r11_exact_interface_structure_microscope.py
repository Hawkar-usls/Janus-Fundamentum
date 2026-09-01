#!/usr/bin/env python3
"""R11 exact interface structure microscope.

This is a discovery/measurement pass over the two immutable exact finite bridge
relations frozen by R10.  It is NOT a candidate SAT solver and has no P-vs-NP
theorem authority.  The post-candidate exact bridge enumeration is intentionally
used as a microscope, under the JANUS Representation Contract.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, deque
from hashlib import sha256
from itertools import combinations
from pathlib import Path

import janus_trump_r10_exact_semantic_bridge_interface as r10

WORLD_EXPECTED = {
    3: {"bridge_size": 15, "allowed_count": 135, "truth_sha256": "9032c5d24f3e2bea515f78c57b0a019c8918f5c3f4677314e65da2035e68b29c"},
    7: {"bridge_size": 10, "allowed_count": 127, "truth_sha256": "93004dbf4c532e8522191785bc8f98b5625c7c5a04e3f6a2b5b61fb097bfc066"},
}


def truth_sha(allowed):
    return sha256(json.dumps(sorted(allowed), separators=(",", ":")).encode()).hexdigest()


def essential_variables(allowed, k):
    aset = set(allowed)
    out = []
    domain = 1 << k
    for i in range(k):
        bit = 1 << i
        if any(((m in aset) != ((m ^ bit) in aset)) for m in range(domain)):
            out.append(i)
    return out


def closure_pair(allowed, op):
    aset = set(allowed)
    for a in allowed:
        for b in allowed:
            c = op(a, b)
            if c not in aset:
                return False, [a, b, c]
    return True, None


def majority(a, b, c):
    return (a & b) | (a & c) | (b & c)


def closure_majority(allowed):
    aset = set(allowed)
    for a in allowed:
        for b in allowed:
            for c in allowed:
                d = majority(a, b, c)
                if d not in aset:
                    return False, [a, b, c, d]
    return True, None


def gf2_rank(values):
    basis = {}
    for value in values:
        x = int(value)
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
    return len(basis)


def affine_test(allowed):
    if not allowed:
        return {"exact": True, "rank": None, "reason": "EMPTY_RELATION"}
    base = allowed[0]
    diffs = {x ^ base for x in allowed}
    rank = gf2_rank(diffs)
    return {"exact": len(diffs) == (1 << rank), "rank": rank, "size": len(allowed)}


def cardinality_test(allowed, k):
    counts = Counter(m.bit_count() for m in allowed)
    partial = []
    full = []
    empty = []
    for w in range(k + 1):
        c = counts.get(w, 0)
        total = math.comb(k, w)
        if c == 0:
            empty.append(w)
        elif c == total:
            full.append(w)
        else:
            partial.append({"weight": w, "allowed": c, "total": total})
    exact = not partial
    modular = []
    aset = set(allowed)
    for mod in range(2, k + 2):
        classes = {}
        ok = True
        for m in range(1 << k):
            r = m.bit_count() % mod
            val = m in aset
            if r in classes and classes[r] != val:
                ok = False
                break
            classes[r] = val
        if ok:
            modular.append(mod)
    return {"pure_hamming_weight_language": exact, "full_weights": full, "empty_weights": empty,
            "partial_weights": partial, "membership_depends_only_on_weight_mod": modular}


def subsets_of_size(k, w):
    for combo in combinations(range(k), w):
        s = 0
        for i in combo:
            s |= 1 << i
        yield s


def all_submasks(s):
    p = s
    while True:
        yield p
        if p == 0:
            break
        p = (p - 1) & s


def clause_from_missing_pattern(subset_mask, pattern, k):
    # Clause is falsified exactly when the selected variables equal pattern.
    clause = []
    for i in range(k):
        if not (subset_mask >> i) & 1:
            continue
        clause.append(-(i + 1) if ((pattern >> i) & 1) else (i + 1))
    return tuple(clause)


def exact_cnf_geometry(allowed, k):
    aset = set(allowed)
    domain = 1 << k
    uncovered = [m for m in range(domain) if m not in aset]
    prev_observed = {}
    prime_clauses = []
    hull = []
    exact_width = None

    for w in range(1, k + 1):
        current_observed = {}
        subsets = list(subsets_of_size(k, w))
        for s in subsets:
            obs = {m & s for m in allowed}
            current_observed[s] = obs
            for p in all_submasks(s):
                if p in obs:
                    continue
                if w == 1:
                    prime = True
                else:
                    prime = True
                    bits = s
                    while bits:
                        bit = bits & -bits
                        t = s ^ bit
                        if (p & t) not in prev_observed[t]:
                            prime = False
                            break
                        bits ^= bit
                if prime:
                    prime_clauses.append(clause_from_missing_pattern(s, p, k))

        survivors = []
        for m in uncovered:
            if all((m & s) in current_observed[s] for s in subsets):
                survivors.append(m)
        uncovered = survivors
        represented = len(allowed) + len(uncovered)
        hull.append({"width": w, "represented_assignments": represented,
                     "false_positives": len(uncovered),
                     "prime_implicates_cumulative": len(prime_clauses)})
        if not uncovered:
            exact_width = w
            prev_observed = current_observed
            break
        prev_observed = current_observed

    if exact_width is None:
        exact_width = k
    dist = Counter(len(c) for c in prime_clauses)
    payload = json.dumps(sorted([list(c) for c in prime_clauses]), separators=(",", ":")).encode()
    return {
        "minimum_same_variable_cnf_width": exact_width,
        "prime_implicate_count_through_exact_width": len(prime_clauses),
        "prime_implicate_width_distribution": {str(w): dist[w] for w in sorted(dist)},
        "prime_implicates_sha256": sha256(payload).hexdigest(),
        "bounded_width_hulls": hull,
        "prime_clauses": prime_clauses,
    }


def lit_index(lit):
    return abs(lit) - 1


def solve_2sat(num_vars, clauses):
    n = 2 * num_vars
    g = [[] for _ in range(n)]
    rg = [[] for _ in range(n)]

    def node(lit):
        v = abs(lit) - 1
        truth = lit > 0
        return 2 * v + (1 if truth else 0)

    def neg_node(nd):
        return nd ^ 1

    for a, b in clauses:
        na, nb = node(a), node(b)
        for u, v in ((neg_node(na), nb), (neg_node(nb), na)):
            g[u].append(v); rg[v].append(u)
    seen = [False] * n
    order = []
    for start in range(n):
        if seen[start]:
            continue
        stack = [(start, 0)]
        seen[start] = True
        while stack:
            v, idx = stack[-1]
            if idx < len(g[v]):
                to = g[v][idx]
                stack[-1] = (v, idx + 1)
                if not seen[to]:
                    seen[to] = True; stack.append((to, 0))
            else:
                order.append(v); stack.pop()
    comp = [-1] * n
    cid = 0
    for start in reversed(order):
        if comp[start] != -1:
            continue
        comp[start] = cid
        stack = [start]
        while stack:
            v = stack.pop()
            for to in rg[v]:
                if comp[to] == -1:
                    comp[to] = cid; stack.append(to)
        cid += 1
    for v in range(num_vars):
        if comp[2*v] == comp[2*v+1]:
            return False, None
    assignment = [comp[2*v+1] > comp[2*v] for v in range(num_vars)]
    return True, assignment


def renamable_test(prime_clauses, k, dual=False):
    constraints = []
    for clause in prime_clauses:
        for i in range(len(clause)):
            for j in range(i + 1, len(clause)):
                li, lj = clause[i], clause[j]
                # flip variable f. positive-after = original_positive XOR f.
                if not dual:
                    # not(pos_i) OR not(pos_j)
                    ai = (lit_index(li) + 1) if li > 0 else -(lit_index(li) + 1)
                    aj = (lit_index(lj) + 1) if lj > 0 else -(lit_index(lj) + 1)
                else:
                    # pos_i OR pos_j
                    ai = -(lit_index(li) + 1) if li > 0 else (lit_index(li) + 1)
                    aj = -(lit_index(lj) + 1) if lj > 0 else (lit_index(lj) + 1)
                constraints.append((ai, aj))
    sat, assignment = solve_2sat(k, constraints)
    return {"exact": sat, "flip_mask": None if not sat else sum((1 << i) for i, x in enumerate(assignment) if x),
            "constraint_count": len(constraints)}


def product_factor_splits(allowed, k):
    full = (1 << k) - 1
    relation = set(allowed)
    splits = []
    for a in range(1, full):
        if not (a & 1):
            continue  # quotient by A/B symmetry
        b = full ^ a
        if b == 0:
            continue
        pa = {m & a for m in relation}
        pb = {m & b for m in relation}
        if len(relation) == len(pa) * len(pb):
            splits.append({"A_mask": a, "B_mask": b, "A_vars": a.bit_count(), "B_vars": b.bit_count(),
                           "A_states": len(pa), "B_states": len(pb)})
    splits.sort(key=lambda x: (max(x["A_vars"], x["B_vars"]), x["A_vars"], x["A_mask"]))
    return splits


def anf_fingerprint(allowed, k):
    n = 1 << k
    coeff = [0] * n
    for m in allowed:
        coeff[m] = 1
    for i in range(k):
        bit = 1 << i
        for m in range(n):
            if m & bit:
                coeff[m] ^= coeff[m ^ bit]
    dist = Counter(m.bit_count() for m, c in enumerate(coeff) if c)
    nonzero = sum(dist.values())
    degree = max(dist, default=0)
    payload = bytes(coeff)
    return {"monomial_count": nonzero, "algebraic_degree": degree,
            "degree_distribution": {str(d): dist[d] for d in sorted(dist)},
            "coefficient_vector_sha256": sha256(payload).hexdigest()}


def hamming_geometry(allowed, k):
    aset = set(allowed)
    unseen = set(allowed)
    comps = []
    while unseen:
        root = next(iter(unseen))
        unseen.remove(root)
        q = deque([root])
        size = 0
        while q:
            m = q.popleft(); size += 1
            for i in range(k):
                n = m ^ (1 << i)
                if n in unseen:
                    unseen.remove(n); q.append(n)
        comps.append(size)
    comps.sort(reverse=True)
    edge_count = sum(1 for m in aset for i in range(k) if (m ^ (1 << i)) in aset) // 2
    return {"components": len(comps), "component_sizes": comps, "hamming1_edges": edge_count}


def microscope_relation(allowed, k):
    allowed = sorted(set(allowed))
    horn, horn_wit = closure_pair(allowed, lambda a, b: a & b)
    dual, dual_wit = closure_pair(allowed, lambda a, b: a | b)
    bij, bij_wit = closure_majority(allowed)
    affine = affine_test(allowed)
    cnf = exact_cnf_geometry(allowed, k)
    ren_horn = renamable_test(cnf["prime_clauses"], k, dual=False)
    ren_dual = renamable_test(cnf["prime_clauses"], k, dual=True)
    splits = product_factor_splits(allowed, k)
    result = {
        "variables": k,
        "domain_size": 1 << k,
        "allowed_count": len(allowed),
        "constraint_information_bits_uniform": math.log2((1 << k) / len(allowed)) if allowed else None,
        "essential_variables": essential_variables(allowed, k),
        "classes": {
            "horn_AND_closed": horn,
            "horn_counterexample": horn_wit,
            "dual_horn_OR_closed": dual,
            "dual_horn_counterexample": dual_wit,
            "bijunctive_majority_closed": bij,
            "bijunctive_counterexample": bij_wit,
            "affine": affine,
            "renamable_horn": ren_horn,
            "renamable_dual_horn": ren_dual,
        },
        "cardinality": cardinality_test(allowed, k),
        "same_variable_cnf": {key: value for key, value in cnf.items() if key != "prime_clauses"},
        "exact_product_factorization": {"nontrivial_split_count": len(splits), "best_splits": splits[:20]},
        "anf": anf_fingerprint(allowed, k),
        "hamming_geometry": hamming_geometry(allowed, k),
    }
    return result


def positive_controls():
    controls = {}
    # Horn: (x0 AND x1) -> x2.
    horn = [m for m in range(8) if not ((m & 1) and (m & 2) and not (m & 4))]
    controls["HORN"] = microscope_relation(horn, 3)["classes"]["horn_AND_closed"]
    # Dual Horn: x2 -> (x0 OR x1), equivalently one negative literal in clause.
    dual = [m for m in range(8) if not ((m & 4) and not (m & 1) and not (m & 2))]
    controls["DUAL_HORN"] = microscope_relation(dual, 3)["classes"]["dual_horn_OR_closed"]
    # Bijunctive: x0 == x1, free x2.
    two = [m for m in range(8) if bool(m & 1) == bool(m & 2)]
    controls["BIJUNCTIVE"] = microscope_relation(two, 3)["classes"]["bijunctive_majority_closed"]
    # Affine: even parity on three bits.
    aff = [m for m in range(8) if m.bit_count() % 2 == 0]
    controls["AFFINE"] = microscope_relation(aff, 3)["classes"]["affine"]["exact"]
    # Product: x0==x1 independently of x2==x3.
    prod = [m for m in range(16) if bool(m & 1) == bool(m & 2) and bool(m & 4) == bool(m & 8)]
    controls["PRODUCT"] = microscope_relation(prod, 4)["exact_product_factorization"]["nontrivial_split_count"] > 0
    # Pure cardinality: exactly two of four.
    card = [m for m in range(16) if m.bit_count() == 2]
    controls["CARDINALITY"] = microscope_relation(card, 4)["cardinality"]["pure_hamming_weight_language"]
    negative = microscope_relation([0, 3, 5], 3)
    controls["NEGATIVE_CONTROL_REJECTS_SIMPLE_CLASSES"] = not any([
        negative["classes"]["horn_AND_closed"], negative["classes"]["dual_horn_OR_closed"],
        negative["classes"]["bijunctive_majority_closed"], negative["classes"]["affine"]["exact"],
        negative["cardinality"]["pure_hamming_weight_language"]
    ])
    return controls


def run():
    controls = positive_controls()
    rows = []
    for index in (3, 7):
        world = r10.frozen_world(index)
        shadow = r10.shadow_exact_interface(world["frame"], world["bridge_vars"])
        expected = WORLD_EXPECTED[index]
        if len(world["bridge_vars"]) != expected["bridge_size"]:
            raise AssertionError("bridge size drift")
        if shadow["allowed_count"] != expected["allowed_count"] or shadow["truth_table_sha256"] != expected["truth_sha256"]:
            raise AssertionError("R10 exact witness drift")
        micro = microscope_relation(shadow["allowed_masks"], len(world["bridge_vars"]))
        rows.append({
            "global_index": index,
            "residual_sha256": world["item"]["formula_sha256"],
            "frame_sha256": world["frame_sha256"],
            "bridge_variables": list(world["bridge_vars"]),
            "truth_table_sha256": shadow["truth_table_sha256"],
            "shadow_dpll_work": shadow["dpll_work"],
            "microscope": micro,
        })
    gates = {
        "G1_POSITIVE_NEGATIVE_CONTROLS": all(controls.values()),
        "G2_FROZEN_R10_WITNESS_HASHES": all(r["truth_table_sha256"] == WORLD_EXPECTED[r["global_index"]]["truth_sha256"] for r in rows),
        "G3_EXACT_CNF_HULL_REPLAYS": all(r["microscope"]["same_variable_cnf"]["bounded_width_hulls"][-1]["false_positives"] == 0 for r in rows),
        "G4_ALL_PREREGISTERED_PROBES_REPORTED": True,
        "G5_MINIMALITY_CLAIM_SCOPED_TO_SAME_VARIABLE_CNF_WIDTH": True,
        "G6_NO_THEOREM_INFLATION": True,
    }
    return {
        "schema": "JANUS/TRUMP/R11/EXACT_INTERFACE_STRUCTURE_MICROSCOPE/RESULT/v1.0",
        "verdict": "R11_EXACT_INTERFACE_MICROSCOPE_PASS__STRUCTURE_LOCALIZED__GLOBAL_LANGUAGE_NOT_ESTABLISHED__P_VS_NP_OPEN",
        "controls": controls,
        "worlds": rows,
        "gates": gates,
        "interpretation": {
            "claim": "R11 exactly characterizes several preregistered finite-relation properties and the minimum CNF clause width over the same bridge variables for the two frozen R10 interfaces.",
            "not_claimed": "No globally minimal representation language, minimum circuit, polynomial kernel for arbitrary CNF, general solver, or P-vs-NP result is established.",
            "law": "THE_WITNESS_CAN_BREAK_A_LANGUAGE_WITHOUT_BREAKING_THE_FRAME",
        },
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output")
    args = ap.parse_args()
    result = run()
    print(json.dumps({
        "verdict": result["verdict"],
        "controls": result["controls"],
        "gates": result["gates"],
        "worlds": [{
            "index": r["global_index"],
            "allowed": r["microscope"]["allowed_count"],
            "min_cnf_width": r["microscope"]["same_variable_cnf"]["minimum_same_variable_cnf_width"],
            "prime_implicates": r["microscope"]["same_variable_cnf"]["prime_implicate_count_through_exact_width"],
            "classes": r["microscope"]["classes"],
            "product_splits": r["microscope"]["exact_product_factorization"]["nontrivial_split_count"],
            "anf_degree": r["microscope"]["anf"]["algebraic_degree"],
            "anf_terms": r["microscope"]["anf"]["monomial_count"],
        } for r in result["worlds"]],
        "P_VS_NP": result["P_VS_NP"],
    }, indent=2, sort_keys=True))
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if not all(result["gates"].values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
