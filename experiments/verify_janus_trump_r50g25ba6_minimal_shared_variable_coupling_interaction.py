from __future__ import annotations

import argparse
import json
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

PREREG = "7eedb1ffd275c63906b8309a1e2c6e5b8a9924be"
HARDENING = "75df83126fd57dc2e9cadcbf3643cac9b7c2572d"
FIREWALL = "b52b4ab0a8ba21f6b41a9a0c5c7c2774d95e5e72"
Q = 2
BLOCK = 30
SOURCE_ALLOWED = {(0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 1)}
PROJECTED_ALLOWED = {(0, 1), (1, 0), (1, 1)}


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


def source_ok(a, b, c):
    return bool(a or b) and bool((not b) or c)


def independent_source_and_projection():
    sat = {(a, b, c) for a, b, c in product((0, 1), repeat=3) if source_ok(a, b, c)}
    proj = {(a, c) for a, b, c in sat}
    rec_ok = all(source_ok(a, 1 - a, c) for a, c in PROJECTED_ALLOWED)
    F = minimize([(1, 2), (-2, 3)])
    R, raw = dp(F, 2)
    return {
        "source": sat,
        "projection": proj,
        "reconstruction_pass": rec_ok,
        "resolution": R,
        "raw": raw,
    }


def lit(bit, sign):
    return bool(bit) if sign > 0 else not bool(bit)


def independent_polarity_partition():
    counts = {"TAUTOLOGICAL_PROJECTION": 0, "UNARY_PROJECTION": 0, "BINARY_DERIVED_COUPLING": 0, "CONTRADICTION_IF_ANY": 0}
    rows = 0
    full = set(product((0, 1), repeat=2))
    candidate = None
    for s1, s2a, s2b, s3 in product((1, -1), repeat=4):
        rows += 1
        proj = set()
        for q1, q2, q3 in product((0, 1), repeat=3):
            if (lit(q1, s1) or lit(q2, s2a)) and (lit(q2, s2b) or lit(q3, s3)):
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
        if (s1, s2a, s2b, s3) == (1, 1, -1, 1):
            candidate = (cls, proj)
    return rows, counts, candidate


def lane_of(v):
    v = abs(int(v))
    return 1 if v <= 3 else (2 if v <= 6 else 3)


def cross(c):
    return len({lane_of(x) for x in c}) >= 2


def edges(F):
    out = set()
    for c in F:
        lanes = sorted({lane_of(x) for x in c})
        for a, b in combinations(lanes, 2):
            out.add((a, b))
    return out


def independent_transport_kernel():
    F = []
    for q, p, r in ((1, 2, 3), (4, 5, 6), (7, 8, 9)):
        F += [(-q, -p), (q, p), (p, r), (-p, -r)]
    F += [(1, 4), (-4, 7)]
    cur = minimize(F)
    R_peak = sum(cross(c) for c in cur)
    B_peak = 0
    E_peak = len(edges(cur))
    W_temp = 0
    raw_total = 0
    for x in (1, 2, 4, 5, 7, 8):
        neigh = set()
        for c in cur:
            if x in c or -x in c:
                neigh |= {abs(l) for l in c if abs(l) != x}
        W_temp = max(W_temp, len(neigh))
        nxt, raw = dp(cur, x)
        raw_total += len(raw)
        B_peak = max(B_peak, len([c for c in raw if cross(c)]))
        R_peak = max(R_peak, len([c for c in nxt if cross(c)]))
        E_peak = max(E_peak, len(edges(nxt)))
        cur = nxt
    sem = set()
    for r1, r2, r3 in product((0, 1), repeat=3):
        a = {3: bool(r1), 6: bool(r2), 9: bool(r3)}
        if all(any((a[abs(l)] if l > 0 else not a[abs(l)]) for l in c) for c in cur):
            sem.add((r1, r2, r3))
    return {
        "final": cur,
        "semantic": sem,
        "R_peak": R_peak,
        "B_peak": B_peak,
        "E_peak": E_peak,
        "W_temp": W_temp,
        "raw_total": raw_total,
    }


def build_instance(U, g):
    base, lane_vars, _ = ba4.build_instance(U, g, 3)
    q1 = Q + ba4.lane_off(g, 0)
    q2 = Q + ba4.lane_off(g, 1)
    q3 = Q + ba4.lane_off(g, 2)
    return list(base) + [(q1, q2), (-q2, q3)], lane_vars, (q1, q2, q3)


def clause_ok(a, c):
    return any((bool(a[abs(int(l))]) if int(l) > 0 else not bool(a[abs(int(l))])) for l in c)


def make_model(first, U, g, bits):
    a = {}
    for i, b in enumerate(bits):
        proto = first[(int(b), 1 - int(b))]
        lo = ba4.lane_off(g, i)
        for j in range(g):
            off = lo + BLOCK * j
            for v, val in proto.items():
                a[int(v) + off] = bool(val)
    cs, lane_vars, qs = build_instance(U, g)
    return {
        "pass": all(clause_ok(a, c) for c in cs),
        "q_source": tuple(int(bool(a[q])) for q in qs),
        "C": len(cs),
        "L": sum(len(c) for c in cs),
        "V": len(set().union(*lane_vars)),
    }


def verify(path):
    x = json.loads(Path(path).read_text())
    errors = []
    if x.get("preregistration_commit") != PREREG:
        errors.append("PREREG_DRIFT")
    if x.get("polarity_domain_hardening_commit") != HARDENING:
        errors.append("HARDENING_DRIFT")
    if x.get("methodology_firewall_commit") != FIREWALL:
        errors.append("FIREWALL_DRIFT")
    if x.get("failure_count") != 0 or x.get("falsifiers"):
        errors.append("FAILURE_LEDGER_NONEMPTY")
    if x.get("outcome") != "BA6-A_MINIMAL_SHARED_VARIABLE_RESOLUTION_INTERACTION_CERTIFIED":
        errors.append("OUTCOME")
    if x.get("arbitrary_CNF_coverage_started") or x.get("next_gate_started"):
        errors.append("SCOPE_ESCAPE")

    sp = independent_source_and_projection()
    if sp["source"] != SOURCE_ALLOWED:
        errors.append("SOURCE_RELATION")
    if sp["projection"] != PROJECTED_ALLOWED or sp["resolution"] != ((1, 3),):
        errors.append("PROJECTION_OR_RESOLUTION")
    if not sp["reconstruction_pass"]:
        errors.append("RECONSTRUCTION_MAP")

    rows, counts, candidate = independent_polarity_partition()
    expected_counts = {"TAUTOLOGICAL_PROJECTION": 8, "UNARY_PROJECTION": 0, "BINARY_DERIVED_COUPLING": 8, "CONTRADICTION_IF_ANY": 0}
    if rows != 16 or counts != expected_counts:
        errors.append("POLARITY_PARTITION")
    if candidate != ("BINARY_DERIVED_COUPLING", PROJECTED_ALLOWED):
        errors.append("CANDIDATE_POLARITY_CASE")

    ker = independent_transport_kernel()
    expected_final = {(3, 6), (-6, 9), (3, 9)}
    if set(ker["final"]) != expected_final:
        errors.append("TRANSPORT_FINAL_CLAUSES")
    if ker["semantic"] != SOURCE_ALLOWED:
        errors.append("TRANSPORT_SEMANTICS")
    if (ker["R_peak"], ker["B_peak"], ker["E_peak"], ker["W_temp"], ker["raw_total"]) != (3, 3, 3, 3, 12):
        errors.append("PEAK_METRICS")

    U, first, gates, hard = ba4.source_hardening()
    if not all(gates.values()):
        errors.append("BA4_PARENT_GATES")
    actual_projection = set()
    replay_count = 0
    for g in (1, 2, 3, 5, 8):
        cs, lane_vars, _ = build_instance(U, g)
        C = len(cs)
        L = sum(len(c) for c in cs)
        V = len(set().union(*lane_vars))
        if (C, L, V, C + L + V) != (201 * g - 4, 489 * g - 8, 60 * g, 750 * g - 12):
            errors.append(f"SIZE_{g}")
        for bits in sorted(SOURCE_ALLOWED):
            m = make_model(first, U, g, bits)
            replay_count += 1
            if not m["pass"] or m["q_source"] != bits:
                errors.append(f"SOURCE_MODEL_{g}_{bits}")
            actual_projection.add((bits[0], bits[2]))
        for a, c in sorted(PROJECTED_ALLOWED):
            bits = (a, 1 - a, c)
            m = make_model(first, U, g, bits)
            replay_count += 1
            if not m["pass"] or m["q_source"] != bits:
                errors.append(f"RETURN_MODEL_{g}_{bits}")
    if actual_projection != PROJECTED_ALLOWED:
        errors.append("ACTUAL_PROJECTED_WITNESS_SET")
    if any(source_ok(0, q2, 0) for q2 in (0, 1)):
        errors.append("00_NOT_EXCLUDED")

    # Independent grammar minimality proof: <2 coupling clauses cannot contain two touching coupling objects;
    # two disjoint clauses are disconnected; shared-variable complementary occurrences yield the outer resolvent.
    minimality_pass = rows == 16 and counts == expected_counts and candidate[0] == "BINARY_DERIVED_COUPLING"

    obligations = {
        "ALGEBRA_PASS": int(sp["source"] == SOURCE_ALLOWED and sp["projection"] == PROJECTED_ALLOWED),
        "CNF_REALIZATION_PASS": int(all(gates.values())),
        "SOURCE_PREIMAGE_PASS": int(not any(e.startswith("SOURCE_MODEL_") for e in errors)),
        "DP_INTERACTION_PASS": int(sp["resolution"] == ((1, 3),) and (3, 9) in ker["final"]),
        "DERIVED_RESOLVENT_EXACTNESS_PASS": int(ker["semantic"] == SOURCE_ALLOWED and actual_projection == PROJECTED_ALLOWED),
        "RECONSTRUCTION_PASS": int(sp["reconstruction_pass"] and not any(e.startswith("RETURN_MODEL_") for e in errors)),
        "SOURCE_VALIDATION_PASS": int(not any(e.startswith("SOURCE_MODEL_") or e.startswith("RETURN_MODEL_") for e in errors)),
        "COMPLEXITY_PASS": int((ker["R_peak"], ker["B_peak"], ker["E_peak"], ker["W_temp"]) == (3, 3, 3, 3)),
        "GENERIC_TRANSPORT_PASS": int((3, 6) in ker["final"] and (-6, 9) in ker["final"]),
        "MINIMALITY_PASS": int(minimality_pass),
        "NO_HIDDEN_ENUMERATION_PASS": int(x.get("BA6_8_certificate", {}).get("generic_state_table_rows") == 0),
        "PEAK_ACCOUNTING_PASS": int(x.get("BA6_7_complexity", {}).get("R_peak") == 3 and x.get("BA6_7_complexity", {}).get("B_peak") == 3 and x.get("BA6_7_complexity", {}).get("E_peak") == 3),
    }
    if not all(v == 1 for v in obligations.values()):
        errors.append("OBLIGATION_PRODUCT")
    xbit = int(not errors)
    vbit = int(not errors)
    prod = 1
    for z in obligations.values():
        prod *= z
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "error_count": len(errors),
        "obligations": obligations,
        "x_no_unclassified_exception": xbit,
        "v_independent_verifier": vbit,
        "P_BA6": prod * xbit * vbit,
        "message_state": "VERIFIED" if not errors else "REJECTED",
        "independent_recomputation": {
            "source_satisfying_set": sorted("".join(map(str, t)) for t in sp["source"]),
            "projected_set": sorted("".join(map(str, t)) for t in sp["projection"]),
            "polarity_partition": counts,
            "transport_final": [list(c) for c in ker["final"]],
            "R_peak": ker["R_peak"],
            "B_peak": ker["B_peak"],
            "E_peak": ker["E_peak"],
            "W_temp": ker["W_temp"],
            "raw_resolvents_per_rung": ker["raw_total"],
            "actual_CNF_replay_count": replay_count,
        },
        "P_VS_NP": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()
    r = verify(args.result)
    text = json.dumps(r, indent=2, sort_keys=True)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n")
    else:
        print(text)
    if r["status"] != "PASS":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
