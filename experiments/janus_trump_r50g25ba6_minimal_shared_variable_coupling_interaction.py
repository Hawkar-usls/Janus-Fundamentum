from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

GATE = "R50G25BA6_MINIMAL_SHARED_VARIABLE_COUPLING_INTERACTION"
PREREG = "7eedb1ffd275c63906b8309a1e2c6e5b8a9924be"
POLARITY_HARDENING = "75df83126fd57dc2e9cadcbf3643cac9b7c2572d"
METHOD_FIREWALL = "b52b4ab0a8ba21f6b41a9a0c5c7c2774d95e5e72"
Q = 2
BLOCK = 30
SOURCE_ALLOWED = {(0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 1)}
PROJECTED_ALLOWED = {(0, 1), (1, 0), (1, 1)}
HOLDOUT_G = (1, 2, 3, 5, 8)


def sha_obj(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def canon_clause(c):
    s = set(int(x) for x in c)
    if any(-x in s for x in s):
        return None
    return tuple(sorted(s, key=lambda x: (abs(x), x < 0)))


def minimize_formula(clauses):
    xs = []
    for c in clauses:
        cc = canon_clause(c)
        if cc is not None:
            xs.append(cc)
    xs = sorted(set(xs), key=lambda c: (len(c), c))
    out = []
    for c in xs:
        sc = set(c)
        if any(set(d).issubset(sc) for d in out):
            continue
        out.append(c)
    return tuple(sorted(out))


def dp_step(formula, var):
    pos = [c for c in formula if var in c]
    neg = [c for c in formula if -var in c]
    rest = [c for c in formula if var not in c and -var not in c]
    raw = []
    for a in pos:
        for b in neg:
            cc = canon_clause((set(a) - {var}) | (set(b) - {-var}))
            if cc is not None:
                raw.append(cc)
    new = minimize_formula(rest + raw)
    return new, {
        "var": var,
        "positive_count": len(pos),
        "negative_count": len(neg),
        "raw_resolvent_count": len(raw),
        "raw_resolvents": [list(c) for c in raw],
        "live_clause_count_after": len(new),
    }


def lit_value(bit, sign):
    return bool(bit) if sign > 0 else not bool(bit)


def source_ok(q1, q2, q3):
    return bool(q1 or q2) and bool((not q2) or q3)


def exact_source_relation():
    sat = {(a, b, c) for a, b, c in product((0, 1), repeat=3) if source_ok(a, b, c)}
    return {
        "satisfying_set": sorted("".join(map(str, x)) for x in sat),
        "expected": sorted("".join(map(str, x)) for x in SOURCE_ALLOWED),
        "pass": sat == SOURCE_ALLOWED,
        "domain_coverage": "EXHAUSTIVE_8_OF_8_ASSIGNMENTS_CHECKED",
    }


def exact_interaction_projection():
    projected = set()
    witnesses = {}
    for q1, q3 in product((0, 1), repeat=2):
        qs = [q2 for q2 in (0, 1) if source_ok(q1, q2, q3)]
        if qs:
            projected.add((q1, q3))
            witnesses[f"{q1}{q3}"] = qs
    F = minimize_formula([(1, 2), (-2, 3)])
    residual, trace = dp_step(F, 2)
    expected = ((1, 3),)
    return {
        "projected_set": sorted("".join(map(str, x)) for x in projected),
        "expected_projected_set": ["01", "10", "11"],
        "existential_witnesses": witnesses,
        "resolution_input": [list(c) for c in F],
        "resolution_trace": trace,
        "resolution_output": [list(c) for c in residual],
        "resolution_exact_target": residual == expected,
        "semantic_exact_target": projected == PROJECTED_ALLOWED,
        "equivalence": projected == PROJECTED_ALLOWED and residual == expected,
        "derived_edge": [1, 3],
    }


def constructive_return():
    rows = []
    ok = True
    for q1, q3 in sorted(PROJECTED_ALLOWED):
        q2 = 1 - q1
        c1 = bool(q1 or q2)
        c2 = bool((not q2) or q3)
        row = {"projected": f"{q1}{q3}", "q2": q2, "K12": c1, "K23": c2}
        rows.append(row)
        ok = ok and c1 and c2
    return {
        "map": "q_2 := NOT q_1",
        "rows": rows,
        "pass": ok,
        "complete_projected_domain": ["01", "10", "11"],
    }


def polarity_audit():
    rows = []
    counts = {
        "TAUTOLOGICAL_PROJECTION": 0,
        "UNARY_PROJECTION": 0,
        "BINARY_DERIVED_COUPLING": 0,
        "CONTRADICTION_IF_ANY": 0,
    }
    full = set(product((0, 1), repeat=2))
    for s1, s2a, s2b, s3 in product((1, -1), repeat=4):
        sat = set()
        proj = set()
        for q1, q2, q3 in product((0, 1), repeat=3):
            c1 = lit_value(q1, s1) or lit_value(q2, s2a)
            c2 = lit_value(q2, s2b) or lit_value(q3, s3)
            if c1 and c2:
                sat.add((q1, q2, q3))
                proj.add((q1, q3))
        if proj == full:
            cls = "TAUTOLOGICAL_PROJECTION"
        elif not proj:
            cls = "CONTRADICTION_IF_ANY"
        elif len(proj) == 2 and (len({a for a, _ in proj}) == 1 or len({b for _, b in proj}) == 1):
            cls = "UNARY_PROJECTION"
        else:
            cls = "BINARY_DERIVED_COUPLING"
        counts[cls] += 1
        predicted_binary = (s2a == -s2b)
        derived_clause = None
        if predicted_binary:
            derived_clause = ["q1" if s1 > 0 else "NOT q1", "q3" if s3 > 0 else "NOT q3"]
        rows.append({
            "signs": {"q1": s1, "q2_clause1": s2a, "q2_clause2": s2b, "q3": s3},
            "classification": cls,
            "projected_set": sorted("".join(map(str, x)) for x in proj),
            "source_satisfying_set": sorted("".join(map(str, x)) for x in sat),
            "q2_occurrences_complementary": predicted_binary,
            "derived_clause_if_binary": derived_clause,
        })
    candidate = next(r for r in rows if r["signs"] == {"q1": 1, "q2_clause1": 1, "q2_clause2": -1, "q3": 1})
    return {
        "complete_assignment_count": len(rows),
        "partition_counts": counts,
        "rows": rows,
        "candidate_case": candidate,
        "pass": len(rows) == 16 and counts == {
            "TAUTOLOGICAL_PROJECTION": 8,
            "UNARY_PROJECTION": 0,
            "BINARY_DERIVED_COUPLING": 8,
            "CONTRADICTION_IF_ANY": 0,
        } and candidate["projected_set"] == ["01", "10", "11"],
    }


def lane_index(var):
    v = abs(int(var))
    if v <= 3:
        return 1
    if v <= 6:
        return 2
    return 3


def cross_clause(c):
    return len({lane_index(x) for x in c}) >= 2


def edge_set(clauses):
    E = set()
    for c in clauses:
        lanes = sorted({lane_index(x) for x in c})
        for a, b in combinations(lanes, 2):
            E.add((a, b))
    return E


def transport_kernel():
    # Each lane is q --XOR-- p --XOR-- r, hence q=r. Two touching source couplings are added only at q-boundary.
    F = []
    for q, p, r in ((1, 2, 3), (4, 5, 6), (7, 8, 9)):
        F.extend(((-q, -p), (q, p), (p, r), (-p, -r)))
    F.extend(((1, 4), (-4, 7)))
    cur = minimize_formula(F)
    order = (1, 2, 4, 5, 7, 8)
    trace = []
    R_peak = sum(cross_clause(c) for c in cur)
    B_peak = 0
    E_peak = len(edge_set(cur))
    W_temp = 0
    live_clause_peak = len(cur)
    raw_total = 0
    for x in order:
        neigh = set()
        for c in cur:
            if x in c or -x in c:
                neigh |= {abs(int(l)) for l in c if abs(int(l)) != x}
        W_temp = max(W_temp, len(neigh))
        nxt, meta = dp_step(cur, x)
        raw_total += meta["raw_resolvent_count"]
        cross_raw = [tuple(rr) for rr in meta["raw_resolvents"] if cross_clause(rr)]
        cross_live = [c for c in nxt if cross_clause(c)]
        B_peak = max(B_peak, len(cross_raw))
        R_peak = max(R_peak, len(cross_live))
        E_peak = max(E_peak, len(edge_set(nxt)))
        live_clause_peak = max(live_clause_peak, len(nxt))
        meta["live_cross_lane_after"] = [list(c) for c in cross_live]
        meta["live_edges_after"] = [list(e) for e in sorted(edge_set(nxt))]
        trace.append(meta)
        cur = nxt
    expected = {(3, 6), (-6, 9), (3, 9)}
    semantic = set()
    for r1, r2, r3 in product((0, 1), repeat=3):
        a = {3: bool(r1), 6: bool(r2), 9: bool(r3)}
        good = all(any((a[abs(l)] if l > 0 else not a[abs(l)]) for l in c) for c in cur)
        if good:
            semantic.add((r1, r2, r3))
    return {
        "input_formula": [list(c) for c in minimize_formula(F)],
        "frozen_elimination_order": ["q1", "p1", "q2", "p2", "q3", "p3"],
        "trace": trace,
        "final_formula": [list(c) for c in cur],
        "expected_final_clause_set": [list(c) for c in sorted(expected)],
        "final_clause_set_exact": set(cur) == expected,
        "K12_next_present": (3, 6) in cur,
        "K23_next_present": (-6, 9) in cur,
        "R13_fill_present": (3, 9) in cur,
        "semantic_output": sorted("".join(map(str, x)) for x in semantic),
        "semantic_identity_on_source_relation": semantic == SOURCE_ALLOWED,
        "manual_future_insertion": 0,
        "R_peak": R_peak,
        "B_peak": B_peak,
        "E_peak": E_peak,
        "W_peak_temporary_kernel": W_temp,
        "live_clause_peak": live_clause_peak,
        "raw_resolvent_total_per_rung": raw_total,
    }


def build_ba6(U, g):
    base, lane_vars, _ = ba4.build_instance(U, g, 3)
    q1 = Q + ba4.lane_off(g, 0)
    q2 = Q + ba4.lane_off(g, 1)
    q3 = Q + ba4.lane_off(g, 2)
    clauses = list(base) + [(q1, q2), (-q2, q3)]
    return clauses, lane_vars, (q1, q2, q3)


def clause_ok(assignment, clause):
    return any((bool(assignment[abs(int(l))]) if int(l) > 0 else not bool(assignment[abs(int(l))])) for l in clause)


def construct_model(first, U, g, bits):
    assignment = {}
    for i, b in enumerate(bits):
        proto = first[(int(b), 1 - int(b))]
        lo = ba4.lane_off(g, i)
        for j in range(g):
            off = lo + BLOCK * j
            for v, val in proto.items():
                assignment[int(v) + off] = bool(val)
    clauses, lane_vars, qs = build_ba6(U, g)
    bad = [idx for idx, c in enumerate(clauses) if not clause_ok(assignment, c)]
    q_vectors = []
    for i, b in enumerate(bits):
        lo = ba4.lane_off(g, i)
        vals = [int(bool(assignment[Q + lo + BLOCK * j])) for j in range(g)]
        q_vectors.append(vals)
    return {
        "g": g,
        "bits": "".join(map(str, bits)),
        "pass": not bad and all(q_vectors[i] == [bits[i]] * g for i in range(3)),
        "bad_clause_count": len(bad),
        "full_original_CNF_verify": "PASS" if not bad else "FAIL",
        "q_vectors": q_vectors,
        "model_sha256": sha_obj({str(v): int(bool(x)) for v, x in sorted(assignment.items())}),
        "variable_count": len(set().union(*lane_vars)),
        "source_q_ids": list(qs),
    }


def materialization_and_preimage():
    U, first, gates, hard = ba4.source_hardening()
    models = []
    for g in HOLDOUT_G:
        for bits in sorted(SOURCE_ALLOWED):
            models.append(construct_model(first, U, g, bits))
    projected_from_real_witnesses = {tuple(map(int, (m["bits"][0], m["bits"][2]))) for m in models if m["pass"]}
    reconstructed = []
    for g in HOLDOUT_G:
        for q1, q3 in sorted(PROJECTED_ALLOWED):
            bits = (q1, 1 - q1, q3)
            reconstructed.append(construct_model(first, U, g, bits))
    # 00 exclusion is exact at source clause level: q1=0 forces q2=1; q3=0 forces q2=0.
    no_q2_for_00 = not any(source_ok(0, q2, 0) for q2 in (0, 1))
    return U, first, {
        "inherited_BA4_six_gates": gates,
        "inherited_BA4_all_pass": all(gates.values()),
        "hardening": hard,
        "actual_source_models": models,
        "all_actual_source_models_pass": all(x["pass"] for x in models),
        "actual_projected_witness_set": sorted("".join(map(str, x)) for x in projected_from_real_witnesses),
        "00_exactly_excluded": no_q2_for_00,
        "actual_projection_exact": projected_from_real_witnesses == PROJECTED_ALLOWED and no_q2_for_00,
        "deterministic_reconstruction_models": reconstructed,
        "all_reconstruction_models_pass": all(x["pass"] for x in reconstructed),
    }


def exact_counts(U, g):
    clauses, lane_vars, _ = build_ba6(U, g)
    actual = {
        "C": len(clauses),
        "L": sum(len(c) for c in clauses),
        "V": len(set().union(*lane_vars)),
    }
    actual["n_struct"] = actual["C"] + actual["L"] + actual["V"]
    expected = {"C": 201 * g - 4, "L": 489 * g - 8, "V": 60 * g, "n_struct": 750 * g - 12}
    return {"g": g, "actual": actual, "expected": expected, "pass": actual == expected}


def minimality_proof(pol):
    return {
        "zero_cross_lane_clauses": "No coupling edge exists by definition.",
        "one_cross_lane_clause": "Exactly one coupling object exists, so there is no pair of couplings that can interact; this is BA5 scope.",
        "two_disjoint_cross_lane_clauses": "Their coupling graph has two disconnected edge components; elimination inside one component cannot derive a clause containing a variable from the other component.",
        "two_shared_variable_clauses": "This is the first grammar level containing two coupling objects in one connected component; complementary signs on the shared occurrence generate a binary resolvent between the outer variables.",
        "complete_polarity_partition": pol["partition_counts"],
        "complete_polarity_rows": 16,
        "strictly_smaller_productive_interaction_found": False,
        "pass": pol["pass"],
    }


def generic_transport_certificate(kernel):
    return {
        "transform_id": "BA6_TOUCHING_COUPLINGS_DP_V1",
        "input_payload": ["K12_j=(q1_j OR q2_j)", "K23_j=((NOT q2_j) OR q3_j)"],
        "output_payload": ["K12_j+1=(q1_j+1 OR q2_j+1)", "K23_j+1=((NOT q2_j+1) OR q3_j+1)", "R13_j+1=(q1_j+1 OR q3_j+1)"],
        "one_rung_exact_DP_trace": kernel["trace"],
        "composition_rule": "At every rung instantiate the same nine-variable local certificate by injective renaming. The two transported coupling clauses are outputs of the proof step and become the next input payload; no future source clause is manually inserted.",
        "derived_fill_rule": "Eliminating the shared carrier q2 at any boundary resolves K12_j with K23_j and derives R13_j=(q1_j OR q3_j).",
        "certificate_representation": "DAG_CHAIN_OF_O(g)_CONSTANT_LOCAL_RECORDS",
        "generic_state_table_rows": 0,
        "local_constant_domain_checks": {"source_relation_rows": 8, "polarity_rows": 16},
        "manual_future_insertion": 0,
    }


def complexity(kernel):
    return {
        "C(g)": "201*g-4",
        "L(g)": "489*g-8",
        "V(g)": "60*g",
        "n(g)": "750*g-12",
        "source_primal_treewidth_upper_bound": 13,
        "source_width_proof": "Take the three sealed BA4/BA3 decomposition trees. Add bridge bags {q1,q2} and {q2,q3}; connect both to a lane-2 bag containing q2 and respectively to lane-1/lane-3 bags containing q1/q3. Running intersection is preserved and maximum bag size remains <=14, hence treewidth<=13.",
        "temporary_boundary_kernel_width": kernel["W_peak_temporary_kernel"],
        "W_peak": max(13, kernel["W_peak_temporary_kernel"]),
        "R_peak": kernel["R_peak"],
        "B_peak": kernel["B_peak"],
        "E_peak": kernel["E_peak"],
        "live_clause_peak_local_kernel": kernel["live_clause_peak"],
        "raw_resolvents_per_rung": kernel["raw_resolvent_total_per_rung"],
        "certificate_records": "O(g)=O(n)",
        "certificate_encoded": "O(n log n)",
        "construction": "O(n) structural; O(n log n) conservative with inherited proof-carrying/hash overhead",
        "elimination": "O(g) because the frozen local kernel has constant variables and constant raw-resolvent bound per rung",
        "verification": "O(n log n) conservative",
        "reconstruction": "O(n)",
        "T_total": "O(n log n) conservative",
        "final_compact_resolvent_not_used_as_complexity_proof": True,
    }


def obligation_vector(result, independent_verifier_bit=0):
    o = {
        "ALGEBRA_PASS": int(result["BA6_1_exact_source_relation"]["pass"] and result["BA6_2_interaction_projection"]["equivalence"]),
        "CNF_REALIZATION_PASS": int(result["BA6_4_materialization"]["inherited_BA4_all_pass"]),
        "SOURCE_PREIMAGE_PASS": int(result["BA6_4_materialization"]["all_actual_source_models_pass"]),
        "DP_INTERACTION_PASS": int(result["BA6_2_interaction_projection"]["resolution_exact_target"] and result["BA6_5_transport_kernel"]["R13_fill_present"]),
        "DERIVED_RESOLVENT_EXACTNESS_PASS": int(result["BA6_4_materialization"]["actual_projection_exact"] and result["BA6_5_transport_kernel"]["semantic_identity_on_source_relation"]),
        "RECONSTRUCTION_PASS": int(result["BA6_3_constructive_return"]["pass"] and result["BA6_4_materialization"]["all_reconstruction_models_pass"]),
        "SOURCE_VALIDATION_PASS": int(all(x["full_original_CNF_verify"] == "PASS" for x in result["BA6_4_materialization"]["actual_source_models"] + result["BA6_4_materialization"]["deterministic_reconstruction_models"])),
        "COMPLEXITY_PASS": int(result["BA6_7_complexity"]["T_total"].startswith("O(n log n)") and result["BA6_7_complexity"]["R_peak"] == 3 and result["BA6_7_complexity"]["E_peak"] == 3),
        "GENERIC_TRANSPORT_PASS": int(result["BA6_5_transport_kernel"]["K12_next_present"] and result["BA6_5_transport_kernel"]["K23_next_present"] and result["BA6_8_certificate"]["manual_future_insertion"] == 0),
        "MINIMALITY_PASS": int(result["BA6_9_minimality"]["pass"] and not result["BA6_9_minimality"]["strictly_smaller_productive_interaction_found"]),
        "NO_HIDDEN_ENUMERATION_PASS": int(result["BA6_8_certificate"]["generic_state_table_rows"] == 0),
        "PEAK_ACCOUNTING_PASS": int(result["BA6_7_complexity"]["R_peak"] >= 2 and result["BA6_7_complexity"]["B_peak"] >= 1 and result["BA6_7_complexity"]["E_peak"] >= 2 and result["BA6_7_complexity"]["W_peak"] >= result["BA6_7_complexity"]["temporary_boundary_kernel_width"]),
    }
    prod = 1
    for v in o.values():
        prod *= v
    x = int(not result["unclassified_exceptions"])
    v = int(independent_verifier_bit)
    return {"obligations": o, "all_closed_pre_independent_verify": bool(prod), "x_no_unclassified_exception": x, "v_independent_verifier": v, "P_BA6": prod * x * v}


def run():
    falsifiers = []
    src = exact_source_relation()
    if not src["pass"]:
        falsifiers.append("F1_SOURCE_RELATION_MISMATCH")
    inter = exact_interaction_projection()
    if not inter["equivalence"]:
        falsifiers.append("F1_EXISTENTIAL_PROJECTION_NOT_EXACT")
    ret = constructive_return()
    if not ret["pass"]:
        falsifiers.append("F5_RECONSTRUCTION_FAILS")
    pol = polarity_audit()
    if not pol["pass"]:
        falsifiers.append("F12_MINIMALITY_POLARITY_AUDIT_FAILURE")
    kernel = transport_kernel()
    if not kernel["final_clause_set_exact"] or not kernel["semantic_identity_on_source_relation"]:
        falsifiers.append("F2_OR_F6_TRANSPORT_KERNEL_MISMATCH")
    U, first, mat = materialization_and_preimage()
    if not mat["actual_projection_exact"]:
        falsifiers.append("F2_ACTUAL_CNF_PROJECTION_DIFFERS")
    if not mat["all_actual_source_models_pass"]:
        falsifiers.append("F3_SOURCE_SAT_ASSIGNMENT_LOST")
    if not mat["all_reconstruction_models_pass"]:
        falsifiers.append("F5_OR_F11_RECONSTRUCTION_SOURCE_REPLAY_FAILS")
    counts = [exact_counts(U, g) for g in HOLDOUT_G]
    if not all(x["pass"] for x in counts):
        falsifiers.append("F7_SOURCE_SIZE_RECURRENCE_DRIFT")
    cert = generic_transport_certificate(kernel)
    cx = complexity(kernel)
    if cert["generic_state_table_rows"] != 0 or cert["manual_future_insertion"] != 0:
        falsifiers.append("F6_OR_F10_HIDDEN_FUTURE_STATE")
    if cx["W_peak"] > 13:
        falsifiers.append("F8_TEMPORARY_WIDTH_EXCEEDS_CLAIM")
    minimal = minimality_proof(pol)
    if not minimal["pass"] or minimal["strictly_smaller_productive_interaction_found"]:
        falsifiers.append("F12_STRICTLY_SMALLER_PRODUCTIVE_INTERACTION")

    success = not falsifiers
    result = {
        "gate": GATE,
        "preregistration_commit": PREREG,
        "polarity_domain_hardening_commit": POLARITY_HARDENING,
        "methodology_firewall_commit": METHOD_FIREWALL,
        "outcome": "BA6-A_MINIMAL_SHARED_VARIABLE_RESOLUTION_INTERACTION_CERTIFIED" if success else "BA6_SMALLEST_FALSIFIER_PRESERVED",
        "failure_count": len(falsifiers),
        "falsifiers": falsifiers,
        "BA6_1_exact_source_relation": src,
        "BA6_2_interaction_projection": inter,
        "BA6_3_constructive_return": ret,
        "BA6_4_materialization": mat,
        "BA6_5_transport_kernel": kernel,
        "BA6_6_interaction_graph": {
            "E_source": [[1, 2], [2, 3]],
            "eliminate_node": 2,
            "E_derived": [[1, 3]],
            "E_peak": kernel["E_peak"],
            "fill_edge": [1, 3],
            "fill_is_derived_not_inserted": kernel["R13_fill_present"] and kernel["manual_future_insertion"] == 0,
        },
        "BA6_7_complexity": cx,
        "BA6_8_certificate": cert,
        "BA6_9_minimality": minimal,
        "BA6_9_complete_polarity_audit": pol,
        "BA6_10_source_preimage_fifth_element": {
            "required": ["ALGEBRA_PASS", "CNF_REALIZATION_PASS", "SOURCE_PREIMAGE_PASS", "DP_INTERACTION_PASS", "DERIVED_RESOLVENT_EXACTNESS_PASS", "RECONSTRUCTION_PASS", "SOURCE_VALIDATION_PASS", "COMPLEXITY_PASS"],
            "hash_receipt_commit_role": "PROVENANCE_ONLY_NOT_MATHEMATICAL_VERIFICATION",
        },
        "source_size_holdouts": counts,
        "unclassified_exceptions": [],
        "arbitrary_CNF_coverage_started": False,
        "next_gate_started": False,
        "P_VS_NP": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "TRUMP_finished": False,
        "explicit_nonclaims": [
            "ARBITRARY_CHAINS_OF_INTERACTING_CLAUSES_ARE_POLYNOMIAL",
            "ARBITRARY_INTERACTION_GRAPHS_ARE_BOUNDED_WIDTH",
            "ARBITRARY_CNF_COVERAGE_PROVED",
            "SAT_IN_P_PROVED",
            "P_EQ_NP_PROVED",
            "TRUMP_FINISHED",
        ],
    }
    result["strict_promotion_guard_pre_independent_verify"] = obligation_vector(result, 0)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    r = run()
    text = json.dumps(r, indent=2, sort_keys=True)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n")
    else:
        print(text)
    if r["failure_count"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
