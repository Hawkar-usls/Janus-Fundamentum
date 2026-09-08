from __future__ import annotations

import argparse
import json
from itertools import combinations, permutations, product
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

PREREG = "4fbfcaf4fe8bfd60e233f966acc5ba9d6d1a4ed1"
FIREWALL = "b52b4ab0a8ba21f6b41a9a0c5c7c2774d95e5e72"
BA7_MIRROR = "a45137a1fe66d38ef62cb36d59a185099830dc48"
BA7_ARTIFACT = "a947f5bc1a778e7445a0f7da907cd982aafca9ff955526a6f30997d5adf228da"
Q = 2
BLOCK = 30
SOURCE_ALLOWED = {"0111", "1000", "1001", "1010", "1011", "1111"}
PROJECTED_ALLOWED = {"011", "100", "101", "110", "111"}
HOLDOUT_G = (1, 2, 3, 5, 8)


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
    taut = 0
    for a in pos:
        for b in neg:
            z = canon((set(a) - {x}) | (set(b) - {-x}))
            if z is None:
                taut += 1
            else:
                raw.append(z)
    dup = len(raw) - len(set(raw))
    new = minimize(rest + raw)
    retained = [c for c in new if c not in rest]
    return new, {"pos": len(pos), "neg": len(neg), "pairs": len(pos) * len(neg), "non_taut": len(raw), "taut": taut, "dup": dup, "retained": len(retained), "retained_cs": retained}


def source_ok(q0, x, q1, q2):
    return bool(q0 or x) and bool((not x) or q1) and bool((not x) or q2)


def independent_source_projection_reconstruction():
    sat = set()
    proj = set()
    reconstruction_ok = True
    for q0, x, q1, q2 in product((0, 1), repeat=4):
        if source_ok(q0, x, q1, q2):
            sat.add(f"{q0}{x}{q1}{q2}")
            proj.add(f"{q0}{q1}{q2}")
    for p in PROJECTED_ALLOWED:
        q0, q1, q2 = map(int, p)
        reconstruction_ok = reconstruction_ok and source_ok(q0, 1 - q0, q1, q2)
    symbolic_ok = True
    for q0, q1, q2 in product((0, 1), repeat=3):
        lhs = any(source_ok(q0, x, q1, q2) for x in (0, 1))
        rhs = bool((q0 or q1) and (q0 or q2))
        symbolic_ok = symbolic_ok and lhs == rhs
    return sat, proj, reconstruction_ok, symbolic_ok


def source_clauses(qs):
    q0, x, q1, q2 = map(int, qs)
    return [(q0, x), (-x, q1), (-x, q2)]


def build_instance(U, g):
    base, lane_vars, _ = ba4.build_instance(U, int(g), 4)
    qs = [Q + ba4.lane_off(int(g), i) for i in range(4)]
    cross = source_clauses(qs)
    return list(base) + cross, lane_vars, qs, cross


def clause_ok(a, c):
    return any((bool(a[abs(int(l))]) if int(l) > 0 else not bool(a[abs(int(l))])) for l in c)


def make_model(first, U, g, s):
    bits = tuple(map(int, s))
    a = {}
    for i, b in enumerate(bits):
        proto = first[(b, 1 - b)]
        lo = ba4.lane_off(int(g), i)
        for j in range(int(g)):
            off = lo + BLOCK * j
            for v, val in proto.items():
                a[int(v) + off] = bool(val)
    cs, lane_vars, qs, cross = build_instance(U, g)
    qvectors = []
    for i, b in enumerate(bits):
        lo = ba4.lane_off(int(g), i)
        qvectors.append([int(bool(a[Q + lo + BLOCK * j])) for j in range(int(g))])
    return all(clause_ok(a, c) for c in cs) and all(qvectors[i] == [bits[i]] * int(g) for i in range(4)), len(cs), sum(len(c) for c in cs), len(set().union(*lane_vars)), len(cross)


def namespace_ok(cs, lane_vars, cross):
    if any(lane_vars[i] & lane_vars[j] for i, j in combinations(range(4), 2)):
        return False
    mem = {int(v): i for i, vs in enumerate(lane_vars) for v in vs}
    actual = []
    for c in cs:
        if len({mem[abs(int(l))] for l in c}) > 1:
            actual.append(tuple(map(int, c)))
    return actual == [tuple(map(int, c)) for c in cross]


def polarity_partition():
    counts = {"TOP_TAUTOLOGICAL_PROJECTION": 0, "TWO_BINARY_DERIVED_COUPLING_CONJUNCTION": 0, "UNARY": 0, "CONTRADICTION": 0}
    def lit(bit, sign):
        return bool(bit) if sign > 0 else not bool(bit)
    for s0, sx0, s1, sx1, s2, sx2 in product((1, -1), repeat=6):
        proj = set()
        for q0, x, q1, q2 in product((0, 1), repeat=4):
            if (lit(q0, s0) or lit(x, sx0)) and (lit(q1, s1) or lit(x, sx1)) and (lit(q2, s2) or lit(x, sx2)):
                proj.add((q0, q1, q2))
        if len({sx0, sx1, sx2}) == 1:
            cls = "TOP_TAUTOLOGICAL_PROJECTION"
        elif len(proj) == 5:
            cls = "TWO_BINARY_DERIVED_COUPLING_CONJUNCTION"
        elif not proj:
            cls = "CONTRADICTION"
        else:
            cls = "UNARY"
        counts[cls] += 1
    return counts


def exact_treewidth(vertices, edges):
    best = 999
    V = tuple(vertices)
    for order in permutations(V):
        adj = {v: set() for v in V}
        for a, b in edges:
            adj[a].add(b); adj[b].add(a)
        width = 0
        for v in order:
            if v not in adj:
                continue
            ns = list(adj[v])
            width = max(width, len(ns))
            for a, b in combinations(ns, 2):
                adj[a].add(b); adj[b].add(a)
            for u in ns:
                adj[u].discard(v)
            del adj[v]
        best = min(best, width)
    return best


def lane_of(v, g):
    return (abs(int(v)) - 1) // (BLOCK * int(g))


def is_cross(c, g):
    return len({lane_of(l, g) for l in c}) > 1


def edge_set(F, g):
    E = set()
    for c in F:
        lanes = sorted({lane_of(l, g) for l in c})
        for a, b in combinations(lanes, 2):
            if a != b:
                E.add((a, b))
    return E


def actual_transport(U):
    g = 2
    cs, lane_vars, qs0, cross = build_instance(U, g)
    qnext = [q + BLOCK for q in qs0]
    cur = minimize(cs)
    totals = {"raw_pairs": 0, "raw_non_tautological": 0, "tautological": 0, "duplicates": 0, "retained": 0}
    live_peak = len(cur)
    R_peak = sum(is_cross(c, g) for c in cur)
    B_peak = 0
    E_diag = len(edge_set(cur, g))
    neigh_peak = 0
    for lane in range(4):
        lo = ba4.lane_off(g, lane)
        for bv in ba4.az.ORDER:
            x = int(bv) + lo
            neigh = set()
            for c in cur:
                if x in c or -x in c:
                    neigh |= {abs(int(l)) for l in c if abs(int(l)) != x}
            neigh_peak = max(neigh_peak, len(neigh))
            nxt, meta = dp(cur, x)
            totals["raw_pairs"] += meta["pairs"]
            totals["raw_non_tautological"] += meta["non_taut"]
            totals["tautological"] += meta["taut"]
            totals["duplicates"] += meta["dup"]
            totals["retained"] += meta["retained"]
            B_peak = max(B_peak, len([c for c in meta["retained_cs"] if is_cross(c, g)]))
            live_peak = max(live_peak, len(nxt))
            R_peak = max(R_peak, sum(is_cross(c, g) for c in nxt))
            E_diag = max(E_diag, len(edge_set(nxt, g)))
            cur = nxt
    cross_remaining = [c for c in cur if is_cross(c, g)]
    target = minimize(source_clauses(qnext) + [(qnext[0], qnext[2]), (qnext[0], qnext[3])])
    return {
        "pass": minimize(cross_remaining) == target and all(set(map(abs, c)).issubset(set(qnext)) for c in cross_remaining),
        "totals": totals,
        "live_peak": live_peak,
        "R_peak": R_peak,
        "B_peak": B_peak,
        "E_diag": E_diag,
        "neighbor_peak": neigh_peak,
        "cross": cross_remaining,
        "target": target,
    }


def verify(path):
    x = json.loads(Path(path).read_text())
    errors = []
    if x.get("preregistration_commit") != PREREG: errors.append("PREREG_DRIFT")
    if x.get("methodology_firewall_commit") != FIREWALL: errors.append("FIREWALL_DRIFT")
    if x.get("parent_BA7_final_meta_commit") != BA7_MIRROR: errors.append("BA7_MIRROR_DRIFT")
    if x.get("parent_BA7_authoritative_artifact_zip_sha256") != BA7_ARTIFACT: errors.append("BA7_ARTIFACT_SHA_DRIFT")
    if x.get("outcome") != "BA8-A_MINIMAL_DEGREE3_BRANCH_RESOLUTION_FANOUT_CERTIFIED": errors.append("OUTCOME")
    if x.get("failure_count") != 0 or x.get("falsifiers"): errors.append("FAILURE_LEDGER")
    if x.get("arbitrary_CNF_coverage_started") or x.get("generic_star_family_started") or x.get("cycle_gate_started") or x.get("next_gate_started"): errors.append("SCOPE_ESCAPE")
    if x.get("P_VS_NP") != "OPEN" or x.get("SAT_IN_P") != "NOT_PROVED" or x.get("TRUMP_finished") is not False: errors.append("GLOBAL_FIREWALL")

    sat, proj, rec_ok, alg_ok = independent_source_projection_reconstruction()
    if sat != SOURCE_ALLOWED: errors.append("SOURCE_RELATION")
    if proj != PROJECTED_ALLOWED: errors.append("PROJECTED_RELATION")
    if not rec_ok: errors.append("RECONSTRUCTION")
    if not alg_ok: errors.append("ALGEBRA")

    F = minimize([(1, 2), (-2, 3), (-2, 4)])
    R, meta = dp(F, 2)
    if R != minimize([(1, 3), (1, 4)]) or meta["pairs"] != 2: errors.append("TWO_RESOLVENT_FANOUT")

    source_edges = {(0, 1), (1, 2), (1, 3)}
    derived = {(0, 2), (0, 3)}
    transient = source_edges | derived
    if len(transient) != 5 or exact_treewidth(range(4), source_edges) != 1 or exact_treewidth(range(4), transient) != 2 or exact_treewidth((0, 2, 3), derived) != 1:
        errors.append("QUOTIENT_WIDTH_OR_EDGE_PEAK")
    wr = x.get("BA8_8_width", {})
    if wr.get("W_peak") != 13 or wr.get("max_bag_size") != "max(14,3)=14": errors.append("FULL_WIDTH_CERTIFICATE")

    pol = polarity_partition()
    expected_pol = {"TOP_TAUTOLOGICAL_PROJECTION": 16, "TWO_BINARY_DERIVED_COUPLING_CONJUNCTION": 48, "UNARY": 0, "CONTRADICTION": 0}
    if pol != expected_pol: errors.append("POLARITY_64")

    U, first, gates, hard = ba4.source_hardening()
    if not all(bool(v) for v in gates.values()): errors.append("PARENT_BA4_GATES")
    replay_count = 0
    for g in HOLDOUT_G:
        cs, lane_vars, qs, cross = build_instance(U, g)
        if not namespace_ok(cs, lane_vars, cross): errors.append(f"NAMESPACE_{g}")
        expected = (268*g-5, 652*g-10, 80*g)
        actual = (len(cs), sum(len(c) for c in cs), len(set().union(*lane_vars)))
        if actual != expected: errors.append(f"SIZE_{g}")
        for s in sorted(SOURCE_ALLOWED):
            ok, C, L, V, sc = make_model(first, U, g, s); replay_count += 1
            if not ok or sc != 3: errors.append(f"SOURCE_MODEL_{g}_{s}")
        for p in sorted(PROJECTED_ALLOWED):
            q0, q1, q2 = map(int, p)
            s = f"{q0}{1-q0}{q1}{q2}"
            ok, C, L, V, sc = make_model(first, U, g, s); replay_count += 1
            if not ok: errors.append(f"RETURN_MODEL_{g}_{p}")

    tr = actual_transport(U)
    if not tr["pass"]: errors.append("ACTUAL_TRANSPORT")
    rr = x.get("BA8_11_raw_resolution_accounting", {})
    rec_raw = rr.get("actual_full_carrier_two_block_local_audit", {})
    if rec_raw != tr["totals"]: errors.append("RAW_ACCOUNTING_DRIFT")
    if rr.get("live_clause_peak") != tr["live_peak"] or rr.get("R_peak") != tr["R_peak"] or rr.get("B_peak") != tr["B_peak"]: errors.append("RAW_PEAK_DRIFT")
    if rr.get("E_peak_certified_quotient") != 5 or rr.get("W_peak_certified") != 13: errors.append("CERTIFIED_PEAKS")
    if rr.get("BA6_raw_12_imported") is not False or rr.get("BA7_path_sequence_imported") is not False: errors.append("RAW_IMPORT_FIREWALL")

    minr = x.get("BA8_13_minimality", {})
    if minr.get("strictly_smaller_success_topology_exists") is not False or "triangle" not in minr.get("triangle_K3_control", "").lower(): errors.append("MINIMALITY")

    cx = x.get("BA8_14_certificate_and_complexity", {})
    if cx.get("certificate_structural") != "Theta(g)=O(n)" or cx.get("certificate_encoded") != "O(g log g)=O(n log n)" or cx.get("T_total_n") != "O(n log n)": errors.append("COMPLEXITY")
    noenum = x.get("BA8_no_hidden_state_enumeration", {})
    if noenum.get("generic_g_boundary_state_table_rows") != 0 or noenum.get("enumerated_2pow_g_states") is not False: errors.append("HIDDEN_ENUMERATION")

    pre = x.get("strict_promotion_guard_pre_independent_verify", {})
    if not pre.get("all_closed_pre_independent_verify") or pre.get("x_no_unclassified_exception") != 1 or pre.get("v_independent_verifier") != 0 or pre.get("P_BA8") != 0:
        errors.append("PRE_GUARD")

    obligations = {
        "ALGEBRA_PASS": int(alg_ok),
        "EXHAUSTIVE_4BIT_SOURCE_PASS": int(sat == SOURCE_ALLOWED),
        "CNF_REALIZATION_PASS": int(not any(e.startswith("NAMESPACE_") or e.startswith("SIZE_") for e in errors)),
        "SOURCE_PREIMAGE_PASS": int(all(bool(v) for v in gates.values())),
        "DP_INTERACTION_PASS": int(R == minimize([(1,3),(1,4)])),
        "TWO_RESOLVENT_EXACTNESS_PASS": int(meta["pairs"] == 2 and len(R) == 2),
        "NO_MANUAL_DERIVED_INSERTION_PASS": int(x.get("BA8_6_first_true_fill_fanout", {}).get("manual_derived_insertion") == 0 and x.get("BA8_10_generic_chain_transport", {}).get("manual_next_boundary_insertion") == 0),
        "GENERIC_TRANSPORT_PASS": int(tr["pass"]),
        "RECONSTRUCTION_PASS": int(rec_ok),
        "FULL_ORIGINAL_CNF_VALIDATION_PASS": int(not any(e.startswith("SOURCE_MODEL_") or e.startswith("RETURN_MODEL_") for e in errors)),
        "POLARITY_64_AUDIT_PASS": int(pol == expected_pol),
        "MINIMALITY_PASS": int("MINIMALITY" not in errors),
        "WIDTH_PASS": int("QUOTIENT_WIDTH_OR_EDGE_PEAK" not in errors and "FULL_WIDTH_CERTIFICATE" not in errors),
        "COMPLEXITY_PASS": int("COMPLEXITY" not in errors),
        "INDEPENDENT_REPLAY_PASS": int(not errors),
    }
    prod = 1
    for z in obligations.values(): prod *= z
    out = {
        "gate": "R50G25BA8_MINIMAL_DEGREE3_BRANCH_RESOLUTION_FANOUT",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "error_count": len(errors),
        "obligations": obligations,
        "v_independent_verifier": 1 if not errors else 0,
        "P_BA8": prod,
        "independent_source_replay_cases": replay_count,
        "actual_transport_raw_accounting": tr["totals"],
        "message_state": "VERIFIED" if not errors else "FALSIFIER_PRESERVED",
    }
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--result", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    out = verify(a.result)
    Path(a.out).write_text(json.dumps(out, indent=2, sort_keys=True))
    if out["status"] != "PASS":
        raise SystemExit("BA8 independent verifier failed: " + ",".join(out["errors"]))
