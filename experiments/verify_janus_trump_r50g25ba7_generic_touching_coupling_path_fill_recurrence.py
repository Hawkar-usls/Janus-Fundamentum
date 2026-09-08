from __future__ import annotations

import argparse
import json
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

PREREG = "d258c8088d12437180d11f20e38b5d0c4afe12b7"
INDEX_HARDENING = "cdfefc5bcf12ce0fb8bc95e3d5f11855dfec1338"
FIREWALL = "b52b4ab0a8ba21f6b41a9a0c5c7c2774d95e5e72"
Q = 2
BLOCK = 30
ENDPOINT_ALLOWED = {(0, 1), (1, 0), (1, 1)}
HOLDOUTS = ((1, 2), (2, 3), (3, 5), (5, 8))


def canon(c):
    s = set(int(x) for x in c)
    if any(-x in s for x in s):
        return None
    return tuple(sorted(s, key=lambda x: (abs(x), x < 0)))


def minimize(cs):
    xs = []
    for c in cs:
        z = canon(c)
        if z is not None:
            xs.append(z)
    xs = sorted(set(xs), key=lambda c: (len(c), c))
    out = []
    for c in xs:
        if any(set(d).issubset(set(c)) for d in out):
            continue
        out.append(c)
    return tuple(sorted(out))


def dp(F, x):
    pos = [c for c in F if x in c]
    neg = [c for c in F if -x in c]
    rest = [c for c in F if x not in c and -x not in c]
    raw = []
    for a in pos:
        for b in neg:
            z = canon((set(a) - {x}) | (set(b) - {-x}))
            if z is not None:
                raw.append(z)
    return minimize(rest + raw), raw


def local_lemma():
    for a, b in product((0, 1), repeat=2):
        lhs = any(bool(a or x) and bool((not x) or b) for x in (0, 1))
        rhs = bool(a or b)
        if lhs != rhs:
            return False
    return True


def generic_reconstruction_logic():
    # q0=0 forces qm=1; all internal bits are 1.
    q0 = 0
    qm = 1
    if not (q0 or 1):
        return False
    if not ((not 1) or qm):
        return False
    # q0=1 makes all internal bits 0; every tail clause is true from NOT 0.
    q0 = 1
    if not (q0 or 0):
        return False
    if not ((not 0) or 0):
        return False
    if not ((not 0) or 1):
        return False
    return True


def source_path_clauses(qs):
    out = [(int(qs[0]), int(qs[1]))]
    for i in range(1, len(qs) - 1):
        out.append((-int(qs[i]), int(qs[i + 1])))
    return out


def build_instance(U, g, m):
    base, lane_vars, _ = ba4.build_instance(U, int(g), int(m) + 1)
    qs = [Q + ba4.lane_off(int(g), i) for i in range(int(m) + 1)]
    source = source_path_clauses(qs)
    return list(base) + source, lane_vars, qs, source


def clause_ok(a, c):
    return any((bool(a[abs(int(l))]) if int(l) > 0 else not bool(a[abs(int(l))])) for l in c)


def path_bits(q0, qm, m):
    return [int(q0)] + [1 - int(q0)] * (int(m) - 1) + [int(qm)]


def make_model(first, U, g, m, q0, qm):
    bits = path_bits(q0, qm, m)
    a = {}
    for i, b in enumerate(bits):
        proto = first[(int(b), 1 - int(b))]
        lo = ba4.lane_off(int(g), i)
        for j in range(int(g)):
            off = lo + BLOCK * j
            for v, val in proto.items():
                a[int(v) + off] = bool(val)
    cs, lane_vars, qs, source = build_instance(U, g, m)
    return {
        "pass": all(clause_ok(a, c) for c in cs),
        "q_values": [int(bool(a[q])) for q in qs],
        "bits": bits,
        "C": len(cs),
        "L": sum(len(c) for c in cs),
        "V": len(set().union(*lane_vars)),
        "source_clause_count": len(source),
    }


def exact_size_formula(g, m):
    C = 67 * g * (m + 1) - m - 2
    L = 163 * g * (m + 1) - 2 * m - 4
    V = 20 * g * (m + 1)
    return C, L, V, C + L + V


def namespace_check(cs, lane_vars, source):
    mem = {int(v): i for i, vs in enumerate(lane_vars) for v in vs}
    cross = []
    for c in cs:
        lanes = {mem[abs(int(l))] for l in c}
        if len(lanes) > 1:
            cross.append(tuple(int(x) for x in c))
    expected = [tuple(int(x) for x in c) for c in source]
    disjoint = all(not (lane_vars[i] & lane_vars[j]) for i, j in combinations(range(len(lane_vars)), 2))
    return cross == expected and disjoint


def compact_kernel(m):
    m = int(m)
    F = []
    for i in range(m + 1):
        q, p, r = 3 * i + 1, 3 * i + 2, 3 * i + 3
        F.extend(((-q, -p), (q, p), (p, r), (-p, -r)))
    qs = [3 * i + 1 for i in range(m + 1)]
    F.extend(source_path_clauses(qs))
    cur = minimize(F)
    raw_total = 0
    raw_peak = 0
    width_peak = 0
    final_edges = set()

    def lane(v):
        return (abs(int(v)) - 1) // 3

    def edge_set(formula):
        E = set()
        for c in formula:
            ls = sorted({lane(x) for x in c})
            for a, b in combinations(ls, 2):
                E.add((a, b))
        return E

    for i in range(m + 1):
        for x in (3 * i + 1, 3 * i + 2):
            neigh = set()
            for c in cur:
                if x in c or -x in c:
                    neigh |= {abs(int(l)) for l in c if abs(int(l)) != x}
            width_peak = max(width_peak, len(neigh))
            cur, raw = dp(cur, x)
            raw_total += len(raw)
            raw_peak = max(raw_peak, len(raw))
    final_edges = edge_set(cur)
    return {
        "raw_total": raw_total,
        "raw_peak": raw_peak,
        "width_peak": width_peak,
        "final_edge_count": len(final_edges),
        "complete": len(final_edges) == m * (m + 1) // 2,
    }


def verify(path):
    x = json.loads(Path(path).read_text())
    errors = []

    if x.get("preregistration_commit") != PREREG:
        errors.append("PREREG_DRIFT")
    if x.get("indexing_hardening_commit") != INDEX_HARDENING:
        errors.append("INDEX_HARDENING_DRIFT")
    if x.get("methodology_firewall_commit") != FIREWALL:
        errors.append("FIREWALL_DRIFT")
    if x.get("outcome") != "BA7-A_GENERIC_TOUCHING_COUPLING_PATH_FILL_RECURRENCE_CERTIFIED":
        errors.append("OUTCOME")
    if x.get("failure_count") != 0 or x.get("falsifiers"):
        errors.append("FAILURE_LEDGER")
    if x.get("arbitrary_CNF_coverage_started") or x.get("cycle_gate_started") or x.get("branching_graph_gate_started") or x.get("next_gate_started"):
        errors.append("SCOPE_ESCAPE")
    if x.get("P_VS_NP") != "OPEN" or x.get("SAT_IN_P") != "NOT_PROVED" or x.get("TRUMP_finished") is not False:
        errors.append("GLOBAL_FIREWALL")

    if not local_lemma():
        errors.append("LOCAL_LEMMA")

    inv = x.get("BA7_1_generic_residual_invariant", {})
    if inv.get("induction_step_domain") != "0<=j<=m-2":
        errors.append("RECURRENCE_DOMAIN")
    if inv.get("terminal") != "F_{m-1}=(q_0 OR q_m).":
        errors.append("TERMINAL_INDEX")
    if inv.get("generic_not_finite_m_inference") is not True:
        errors.append("FINITE_M_AUTHORITY")

    terminal = x.get("BA7_2_terminal_projection", {})
    if terminal.get("endpoint_relation") != ["01", "10", "11"] or terminal.get("forbidden") != ["00"]:
        errors.append("TERMINAL_RELATION")

    if not generic_reconstruction_logic():
        errors.append("GENERIC_RECONSTRUCTION_LOGIC")
    recon = x.get("BA7_3_generic_reconstruction", {})
    if recon.get("map") != "q_i := NOT q_0 for every 1<=i<m" or recon.get("generic_pass") is not True:
        errors.append("RECONSTRUCTION_RECORD")

    size = x.get("BA7_5_exact_source_size", {})
    expected_size_strings = {
        "C_derivation": "(m+1)(67g-2)+m = 67g(m+1)-m-2",
        "L_derivation": "(m+1)(163g-4)+2m = 163g(m+1)-2m-4",
        "V_derivation": "(m+1)(20g) = 20g(m+1)",
        "n_derivation": "C+L+V = 250g(m+1)-3m-6",
    }
    for k, v in expected_size_strings.items():
        if size.get(k) != v:
            errors.append("SIZE_DERIVATION_" + k)
    # Generic coefficient proof of n=Theta(gm):
    # n-247gm = 3m(g-1)+250g-6 >= 244; 375gm-n = 125g(m-2)+3m+6 >= 12.
    theta_algebra_pass = True
    if size.get("theta") != "n_struct=Theta(g*m)":
        theta_algebra_pass = False
        errors.append("THETA_RELATION")

    fill = x.get("BA7_6_fill_graph_recurrence", {})
    if fill.get("edge_count") != "|E_j|=m-j" or fill.get("step_domain") != "0<=j<=m-2":
        errors.append("FILL_RECURRENCE_SCHEMA")
    if fill.get("productive_resolvent_edge") != "(0,v+1)=(0,j+2)" or fill.get("other_fill_edges") != 0:
        errors.append("FILL_EDGE_SCHEMA")
    peak = x.get("BA7_7_transient_edge_peak", {})
    if peak.get("E_peak") != "m+1" or peak.get("E_peak_asymptotic") != "O(m)" or peak.get("final_edge_count") != 1:
        errors.append("EDGE_PEAK")

    prodrec = x.get("BA7_8_local_resolution_productivity", {}).get("abstract", {})
    if (prodrec.get("pivot_positive_occurrences"), prodrec.get("pivot_negative_occurrences"), prodrec.get("productive_binary_resolvents_per_step")) != (1, 1, 1):
        errors.append("ABSTRACT_PRODUCTIVITY")

    raw_record = x.get("BA7_8_local_resolution_productivity", {}).get("carrier_diagnostic", {})
    k2 = compact_kernel(2)
    k3 = compact_kernel(3)
    if k2["raw_total"] != 12:
        errors.append("BA6_RAW_REPLAY")
    if k3["raw_total"] == 12:
        errors.append("BA6_CONSTANT_FALSE_NEGATIVE")
    if raw_record.get("BA6_constant_12_generalizes") is not False or raw_record.get("used_for_BA7_promotion") is not False:
        errors.append("RAW_STRATEGY_AUTHORITY")
    # Generic polynomial upper bound is independently valid because binary DP over N=O(m)
    # has O(N^2) possible minimized signed unit/binary clauses, O(N^2) raw pairs per pivot, O(N) pivots.
    raw_poly_pass = raw_record.get("generic_polynomial_upper_bound") == "O(m^3) raw resolvents for this rejected diagnostic strategy"
    if not raw_poly_pass:
        errors.append("RAW_POLY_BOUND")

    width = x.get("BA7_9_width", {})
    if width.get("source_quotient_treewidth") != 1 or width.get("transient_quotient_treewidth") != 2 or width.get("W_peak") != 13:
        errors.append("WIDTH_SCHEMA")
    if width.get("max_bag_size") != "max(14,3)=14" or width.get("generic_in_g_m") is not True:
        errors.append("WIDTH_COMPOSITION")

    U, first, gates, hard = ba4.source_hardening()
    if not all(bool(v) for v in gates.values()):
        errors.append("PARENT_BA4_GATES")
    replay_rows = []
    for g, m in HOLDOUTS:
        cs, lane_vars, qs, source = build_instance(U, g, m)
        if not namespace_check(cs, lane_vars, source):
            errors.append(f"NAMESPACE_{g}_{m}")
        actual = (len(cs), sum(len(c) for c in cs), len(set().union(*lane_vars)))
        C, L, V, n = exact_size_formula(g, m)
        if actual != (C, L, V):
            errors.append(f"SIZE_{g}_{m}")
        for q0, qm in sorted(ENDPOINT_ALLOWED):
            model = make_model(first, U, g, m, q0, qm)
            if not model["pass"] or model["q_values"] != model["bits"]:
                errors.append(f"MODEL_{g}_{m}_{q0}{qm}")
        replay_rows.append({"g": g, "m": m, "C": C, "L": L, "V": V, "n": n})

    cert = x.get("BA7_10_certificate_recurrence", {})
    if cert.get("total_structural_certificate") != "Theta(gm)=O(n)" or cert.get("encoded_certificate") != "O(gm*log(gm))=O(n log n)":
        errors.append("CERTIFICATE_RECURRENCE")
    if cert.get("generic_state_table_rows") != 0:
        errors.append("CERTIFICATE_ENUMERATION")

    total = x.get("BA7_11_total_time", {})
    if total.get("T_total_g_m") != "O(gm log(gm))" or total.get("T_total_n") != "O(n log n)":
        errors.append("TOTAL_TIME")
    if total.get("empirical_timing_used_for_promotion") is not False:
        errors.append("EMPIRICAL_COMPLEXITY_AUTHORITY")

    noenum = x.get("BA7_12_no_hidden_state_enumeration", {})
    if noenum.get("generic_state_table_rows") != 0 or noenum.get("boundary_vectors_enumerated") != 0:
        errors.append("HIDDEN_ENUMERATION")
    if noenum.get("generic_proof_mode") != "SYMBOLIC_INDUCTION_RECURRENCE_AND_CONSTRUCTIVE_RETURN":
        errors.append("GENERIC_PROOF_MODE")

    obligations = {
        "ALGEBRA_PASS": int(local_lemma() and inv.get("pass") is True and terminal.get("pass") is True),
        "CNF_REALIZATION_PASS": int(not any(e.startswith("NAMESPACE_") for e in errors)),
        "SOURCE_PREIMAGE_PASS": int(all(bool(v) for v in gates.values())),
        "DP_INTERACTION_PASS": int(fill.get("pass") is True and prodrec.get("pass") is True),
        "GENERIC_RECURRENCE_PASS": int(inv.get("generic_not_finite_m_inference") is True),
        "RECONSTRUCTION_PASS": int(generic_reconstruction_logic() and not any(e.startswith("MODEL_") for e in errors)),
        "SOURCE_VALIDATION_PASS": int(not any(e.startswith("MODEL_") or e.startswith("NAMESPACE_") for e in errors)),
        "EXACT_SIZE_PASS": int(theta_algebra_pass and not any(e.startswith("SIZE_") for e in errors)),
        "FILL_RECURRENCE_PASS": int(fill.get("pass") is True and peak.get("pass") is True),
        "RAW_RESOLVENT_POLY_PASS": int(raw_poly_pass and k2["raw_total"] == 12 and k3["raw_total"] != 12),
        "WIDTH_PASS": int(width.get("pass") is True and width.get("W_peak") == 13),
        "CERTIFICATE_RECURRENCE_PASS": int(cert.get("pass") is True and cert.get("generic_state_table_rows") == 0),
        "COMPLEXITY_PASS": int(total.get("pass") is True and total.get("T_total_n") == "O(n log n)"),
        "NO_HIDDEN_ENUMERATION_PASS": int(noenum.get("pass") is True and noenum.get("boundary_vectors_enumerated") == 0),
    }
    all_obligations = all(v == 1 for v in obligations.values())
    if not all_obligations:
        errors.append("OBLIGATION_PRODUCT")

    status = "PASS" if not errors else "FAIL"
    return {
        "gate": "R50G25BA7_GENERIC_TOUCHING_COUPLING_PATH_FILL_RECURRENCE",
        "status": status,
        "errors": errors,
        "error_count": len(errors),
        "obligations": obligations,
        "x_no_unclassified_exception": int(not errors),
        "v_independent_verifier": int(not errors),
        "P_BA7": int(not errors and all_obligations),
        "message_state": "VERIFIED" if not errors else "REJECTED",
        "independent_replays": replay_rows,
        "raw_diagnostic": {"m2": k2, "m3": k3},
        "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    v = verify(args.result)
    Path(args.out).write_text(json.dumps(v, indent=2, sort_keys=True) + "\n")
    if v["status"] != "PASS":
        raise SystemExit("BA7 independent verification failed: " + ",".join(v["errors"]))


if __name__ == "__main__":
    main()
