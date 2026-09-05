from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g13_v7_single_external_support_hub_cycle as r50g13
import janus_trump_r50g14_v7_hub_cycle_ancestry_bifurcation as r50g14

GATE = "JANUS_TRUMP_R50G22_ALL_DIRECT5_V7_CYCLE_REALIZER_OR_REJECTION"
VARS = tuple(range(1, 8))
GEOMETRIES = ("4x3_DISJOINT", "3x4_DISJOINT", "4x4_OVERLAP1")
ROTATIONS = tuple(range(5))
DECLARED_FAMILY_SIZE = 6 * 128 * len(GEOMETRIES) * len(ROTATIONS)


def canon(formula):
    return r33.canonical_formula(formula)


def max_width(formula):
    return max((len(c) for c in canon(formula)), default=0)


def global_literal(v: int, sign_mask: int) -> int:
    bit = (int(sign_mask) >> (int(v) - 1)) & 1
    return int(v) if bit else -int(v)


def hub_map_for_cycle_length(k: int):
    k = int(k)
    if not 2 <= k <= 7:
        raise ValueError("cycle length must be 2..7")
    h = {}
    for v in range(1, k):
        h[v] = v + 1
    h[k] = 1
    for v in range(k + 1, 8):
        h[v] = 1
    return h


def rotate(xs, amount: int):
    xs = list(xs)
    q = int(amount) % len(xs)
    return xs[q:] + xs[:q]


def direct5_pair(v: int, hub: int, sign_mask: int, geometry: str, rotation: int):
    target_vars = [u for u in VARS if u not in {int(v), int(hub)}]
    target = [global_literal(u, int(sign_mask)) for u in target_vars]
    target = rotate(target, int(rotation))

    if geometry == "4x3_DISJOINT":
        pos_res = target[:3]
        neg_res = target[3:]
    elif geometry == "3x4_DISJOINT":
        pos_res = target[:2]
        neg_res = target[2:]
    elif geometry == "4x4_OVERLAP1":
        pos_res = target[:3]
        neg_res = [target[2], target[3], target[4]]
    else:
        raise ValueError(geometry)

    pos = r33.canonical_clause([int(v), *pos_res])
    neg = r33.canonical_clause([-int(v), *neg_res])
    target_clause = r33.canonical_clause(target)
    g = r50g14.parent_geometry(pos, neg, int(v))
    if g.get("tautological") or tuple(g["resolvent"]) != target_clause or int(g["resolvent_width"]) != 5:
        raise AssertionError(("R50G22_PAIR_CONSTRUCTION_DRIFT", v, hub, geometry, rotation, pos, neg, target_clause, g))
    if abs(int(hub)) in {abs(x) for x in pos + neg}:
        raise AssertionError(("R50G22_DESIGNATED_PARENT_CONTAINS_HUB", v, hub, pos, neg))
    return pos, neg, target_clause


def build_source(k: int, sign_mask: int, geometry: str, rotation: int):
    hmap = hub_map_for_cycle_length(int(k))
    clauses = []
    designated = {}
    for v in VARS:
        p, n, c = direct5_pair(v, hmap[v], int(sign_mask), geometry, int(rotation))
        clauses.extend([p, n])
        designated[str(v)] = {
            "pivot": int(v),
            "hub": int(hmap[v]),
            "positive_parent": list(p),
            "negative_parent": list(n),
            "target_clause": list(c),
        }
    f = canon(clauses)
    return f, hmap, designated


def designated_ancestry_audit(source, hmap, designated):
    f = canon(source)
    rows = {}
    for v in VARS:
        row = designated[str(v)]
        p = tuple(row["positive_parent"])
        n = tuple(row["negative_parent"])
        c = tuple(row["target_clause"])
        if p not in f or n not in f:
            raise AssertionError(("R50G22_DESIGNATED_PARENT_LOST_BY_CANON", v, p, n))
        classified = r50g14.classify_hub_edge_ancestor(f, int(v), c, int(hmap[v]))
        direct = [x for x in classified if x["type"] == "DIRECT5"]
        if not direct:
            raise AssertionError(("R50G22_DESIGNATED_DIRECT5_NOT_REPLAYED", v, hmap[v], c, classified))
        rows[str(v)] = {
            "hub": int(hmap[v]),
            "target_clause": list(c),
            "direct5_certificate_count": len(direct),
            "first_direct5_certificate": direct[0],
        }
    return rows


def candidate_spec(k, sign_mask, geometry, rotation):
    return {
        "cycle_length": int(k),
        "sign_mask": int(sign_mask),
        "geometry": geometry,
        "split_rotation": int(rotation),
    }


def rejection_key_from_certificate(cert):
    if not cert.get("applicable"):
        return str(cert.get("reason", "NOT_APPLICABLE"))
    if cert.get("all_doors_closed"):
        return "ALL_DOORS_CLOSED"
    if "first_open_R47J" in cert:
        return f"OPEN_R47J_PIVOT_{int(cert['first_open_R47J'])}"
    if "first_open_alternate" in cert:
        return f"OPEN_ALTERNATE_PIVOT_{int(cert['first_open_alternate'])}"
    return "APPLICABLE_NOT_ALL_CLOSED_OTHER"


def exact_actual_direct5_audit(source, all_closed_cert):
    f = canon(source)
    out = {}
    for key, prof in all_closed_cert["profiles"].items():
        if not prof.get("unsafe"):
            raise AssertionError(("R50G22_ALL_CLOSED_PROFILE_NOT_UNSAFE", key, prof))
        v = int(prof["pivot"])
        hub = int(prof["hub"])
        c = tuple(int(x) for x in prof["canonical_width5_clause"])
        rows = r50g14.classify_hub_edge_ancestor(f, v, c, hub)
        direct = [r for r in rows if r["type"] == "DIRECT5"]
        if not direct:
            raise AssertionError(("R50G22_ALL_CLOSED_EDGE_NOT_DIRECT5", v, hub, c, rows))
        out[str(v)] = {
            "hub": hub,
            "clause": list(c),
            "direct5_certificate_count": len(direct),
            "first_direct5": direct[0],
        }
    return out


def run_frozen_family():
    tested = 0
    preclean = 0
    immediate_x = 0
    rejection = Counter()
    first_examples = {}
    strongest = None
    strongest_score = -1
    found = None

    for k in range(2, 8):
        for sign_mask in range(128):
            for geometry in GEOMETRIES:
                for rotation in ROTATIONS:
                    tested += 1
                    spec = candidate_spec(k, sign_mask, geometry, rotation)
                    f, hmap, designated = build_source(k, sign_mask, geometry, rotation)
                    if set(r33.variables(f)) != set(VARS) or max_width(f) > 4:
                        raise AssertionError(("R50G22_FROZEN_SOURCE_DOMAIN_DRIFT", spec, r33.variables(f), max_width(f)))
                    ancestry = designated_ancestry_audit(f, hmap, designated)

                    if not r50g10.exact_pre_bve_clean(f):
                        key = "NOT_PRE_BVE_CLEAN"
                        rejection[key] += 1
                        first_examples.setdefault(key, {"spec": spec, "source": [list(c) for c in f]})
                        continue
                    preclean += 1

                    micro = r50g4.micro_r33_status(f)
                    direct = r50g4.first_r33_micro_candidate(f)
                    if not (
                        micro["status"] == "IMMEDIATE_BVE_W4_ESCAPE"
                        and direct["kind"] == "PROPOSAL"
                        and direct["rule"] == "BOUNDED_VARIABLE_ELIMINATION"
                        and int(direct["var"]) == 1
                    ):
                        key = "NOT_IMMEDIATE_BVE_ESCAPE_ON_1"
                        rejection[key] += 1
                        first_examples.setdefault(key, {
                            "spec": spec,
                            "micro": micro,
                            "first_r33": direct,
                            "source": [list(c) for c in f],
                        })
                        continue
                    immediate_x += 1

                    cert = r50g13.all_closed_v7_hub_certificate(f, 1)
                    key = rejection_key_from_certificate(cert)
                    rejection[key] += 1
                    first_examples.setdefault(key, {
                        "spec": spec,
                        "source": [list(c) for c in f],
                        "certificate": cert,
                    })

                    score = len(cert.get("profiles", {}))
                    if score > strongest_score:
                        strongest_score = score
                        strongest = {
                            "score_profiled_pivots_before_first_open": score,
                            "spec": spec,
                            "source": [list(c) for c in f],
                            "declared_hub_map": {str(a): int(b) for a, b in sorted(hmap.items())},
                            "designated_ancestry": ancestry,
                            "certificate": cert,
                        }

                    if cert.get("all_doors_closed"):
                        actual = exact_actual_direct5_audit(f, cert)
                        found = {
                            "spec": spec,
                            "source": [list(c) for c in f],
                            "source_CLV": list(r33.measure(f)),
                            "declared_hub_map": {str(a): int(b) for a, b in sorted(hmap.items())},
                            "designated_ancestry": ancestry,
                            "all_closed_certificate": cert,
                            "actual_surviving_direct5_ancestry": actual,
                            "reachability": "NOT_ESTABLISHED",
                        }
                        return {
                            "tested": tested,
                            "full_family_size": DECLARED_FAMILY_SIZE,
                            "stopped_early_on_counterexample": True,
                            "pre_bve_clean": preclean,
                            "immediate_bve_escape_on_1": immediate_x,
                            "rejection_histogram": dict(sorted(rejection.items())),
                            "first_examples": first_examples,
                            "strongest_partial": strongest,
                            "local_all_doors_closed_counterexample": found,
                        }

    if tested != DECLARED_FAMILY_SIZE:
        raise AssertionError(("R50G22_FAMILY_SIZE_DRIFT", tested, DECLARED_FAMILY_SIZE))
    return {
        "tested": tested,
        "full_family_size": DECLARED_FAMILY_SIZE,
        "stopped_early_on_counterexample": False,
        "pre_bve_clean": preclean,
        "immediate_bve_escape_on_1": immediate_x,
        "rejection_histogram": dict(sorted(rejection.items())),
        "first_examples": first_examples,
        "strongest_partial": strongest,
        "local_all_doors_closed_counterexample": None,
    }


def source_reduction_control():
    f, hmap, designated = build_source(7, 127, "4x3_DISJOINT", 0)
    audit = designated_ancestry_audit(f, hmap, designated)
    if len(audit) != 7:
        raise AssertionError(("R50G22_SOURCE_REDUCTION_CONTROL_FAIL", audit))
    for v in VARS:
        row = designated[str(v)]
        hub = int(row["hub"])
        for parent_name in ("positive_parent", "negative_parent"):
            if hub in {abs(int(x)) for x in row[parent_name]}:
                raise AssertionError(("R50G22_PARENT_OMISSION_FAIL", v, hub, row))
    return {
        "source_CLV": list(r33.measure(f)),
        "hub_map": {str(a): int(b) for a, b in sorted(hmap.items())},
        "all_seven_designated_direct5_certificates": True,
        "all_designated_parent_pairs_omit_declared_hub": True,
    }


def run():
    reduction = source_reduction_control()
    search = run_frozen_family()
    found = search["local_all_doors_closed_counterexample"] is not None
    if found:
        verdict = "EXPLICIT_LOCAL_V7_ALL_DIRECT5_ALL_DOORS_CLOSED_COUNTEREXAMPLE_FOUND__REACHABILITY_NOT_ESTABLISHED"
        local_status = "REFUTED_LOCAL"
    else:
        verdict = "NO_ALL_DOORS_CLOSED_REALIZER_IN_FROZEN_ALL_DIRECT5_PARENT_OMISSION_FAMILY__UNIVERSAL_ALL_DIRECT5_IMPOSSIBILITY_OPEN"
        local_status = "OPEN"
    return {
        "gate": GATE,
        "mode": "SOURCE_PARENT_OMISSION_REDUCTION_PLUS_FROZEN_DETERMINISTIC_COUNTEREXAMPLE_HUNT",
        "proved_from_frozen_source_definitions": [
            "DIRECT5_EDGE_v_TO_h_HAS_EXACT_OPPOSITE_v_PARENT_PAIR_WITH_BOTH_PARENTS_OMITTING_h",
            "DIRECT5_PARENT_RESIDUAL_UNION_IS_EXACTLY_THE_OTHER_FIVE_VARIABLES",
            "DIRECT5_PARENT_GEOMETRY_IS_EXACTLY_4x3_DISJOINT_OR_3x4_DISJOINT_OR_4x4_OVERLAP1",
            "ALL_DIRECT5_HUB_CYCLE_IS_A_PARENT_OMISSION_CYCLE",
        ],
        "source_reduction_control": reduction,
        "frozen_family": search,
        "critical_next_obligation": (
            "IF_COUNTEREXAMPLE_FOUND__ATTACK_REACHABILITY_OR_USE_EXACT_LEDGER_TO_REPAIR_THEOREM;_"
            "IF_NO_FIND__ATTACK_DOMINANT_REJECTION_CLASS_SYMBOLICALLY_WITHOUT_PROMOTING_FINITE_NO_FIND"
        ),
        "verdict": verdict,
        "firewall": {
            "FINITE_NO_FIND_IMPLIES_ALL_DIRECT5_IMPOSSIBLE": False,
            "LOCAL_COUNTEREXAMPLE_IMPLIES_REACHABLE_COUNTEREXAMPLE": False,
            "LOCAL_ALL_DIRECT5_IMPOSSIBILITY": local_status,
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
            "V7_IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
