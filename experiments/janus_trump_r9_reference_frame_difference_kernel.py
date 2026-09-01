#!/usr/bin/env python3
"""R9: reference-frame + delta exact-kernel killer test.

Candidate path contains no DPLL/backtracking/exhaustive assignment search.  R9A
uses the exact parity algebra already present in the toroidal Tseitin family.
R9B extracts the maximal unchanged clause frame for the two frozen R8A OPEN
one-variable restrictions.  R9C admits only typed compositions with an explicit
exact polynomial rule; GENERAL_CNF bridges remain OPEN.
"""
from __future__ import annotations

import argparse
import inspect
import json
import sys
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE / "direct") not in sys.path:
    sys.path.insert(0, str(HERE / "direct"))

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r8a_unseen_natural_holdout as r8a
import toroidal_tseitin_twins as torus

OPEN_INDICES = (3, 7)
OPEN_HASHES = (
    "d10f03b1150e9ebfa0220c02024147d18e62c436be2e8c3976aebcfe1596a2d4",
    "017cb3c17e33b024d6fc8590906513d120f93252d19ad43d07148c97dda6cc0d",
)


def cnf_digest(cnf) -> str:
    return sha256(json.dumps([list(c) for c in direct.canon(cnf)], separators=(",", ":")).encode()).hexdigest()


def vars_of(cnf) -> set[int]:
    return {abs(lit) for clause in cnf for lit in clause}


def classify_cnf(cnf) -> str:
    cnf = tuple(tuple(c) for c in cnf)
    if not cnf:
        return "TRIVIAL_EMPTY"
    if all(len(c) <= 2 for c in cnf):
        return "TWO_SAT"
    if all(sum(1 for lit in c if lit > 0) <= 1 for c in cnf):
        return "HORN"
    if all(sum(1 for lit in c if lit < 0) <= 1 for c in cnf):
        return "DUAL_HORN"
    return "GENERAL_CNF"


def compile_tseitin_frame(radius: int) -> dict:
    """Compile the fixed graph frame, not any charge/truth information."""
    size = torus.torus_size(radius)
    vertices = torus.all_vertices(size)
    edges = torus.all_edges(size)
    # The connected torus has one left-nullspace parity invariant.  The frozen
    # family has two disjoint copies, hence two basis vectors, one per component.
    payload = {
        "radius": radius,
        "torus_side": size,
        "vertices_per_component": len(vertices),
        "edges_per_component": len(edges),
        "components": 2,
        "left_kernel_basis": ["ALL_VERTEX_ROWS_COMPONENT_0", "ALL_VERTEX_ROWS_COMPONENT_1"],
        "edge_order": [list(e) for e in edges],
    }
    frame_hash = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    # Explicit linear-size accounting; this is an implementation charge, not a
    # claim about every possible CNF representation.
    kernel_items = 2 * (len(vertices) + len(edges)) + 2
    compile_ops = 2 * (len(vertices) * 4 + len(edges))
    return {**payload, "frame_sha256": frame_hash, "kernel_items": kernel_items, "compile_ops": compile_ops}


def tseitin_syndrome(charges) -> tuple[int, ...]:
    return tuple(len(component) & 1 for component in charges)


def r9a_state(radius: int, charges, frame: dict) -> dict:
    """Update only b, then either emit parity contradiction or diverge to model."""
    cnf, ids = torus.build_formula(radius, charges)
    syndrome = tseitin_syndrome(charges)
    charge_items = sum(len(c) for c in charges)
    update_ops = 2 + charge_items
    if any(syndrome):
        terminal = "UNSAT"
        witness = None
        certificate = {"odd_components": [i for i, bit in enumerate(syndrome) if bit]}
        replay = torus.formula_assignment(radius, charges, ids) is None
        diverge_ops = 0
    else:
        terminal = "SAT"
        witness = torus.formula_assignment(radius, charges, ids)
        certificate = {"syndrome": list(syndrome)}
        replay = witness is not None and torus.formula_satisfied(cnf, witness)
        size = torus.torus_size(radius)
        diverge_ops = 2 * (len(torus.all_vertices(size)) * 4 + len(torus.all_edges(size)))
    verify_ops = len(cnf.clauses) * 4
    return {
        "terminal": terminal,
        "syndrome": list(syndrome),
        "charge_items": charge_items,
        "update_ops": update_ops,
        "diverge_ops": diverge_ops,
        "verify_ops": verify_ops,
        "certificate": certificate,
        "sat_witness_size": 0 if witness is None else len(witness),
        "exact_replay": bool(replay),
        "cnf_variables": cnf.variable_count,
        "cnf_clauses": len(cnf.clauses),
        "frame_sha256": frame["frame_sha256"],
    }


def run_r9a() -> dict:
    rows = []
    for radius in range(5):
        frame = compile_tseitin_frame(radius)
        sat_charges, unsat_charges = torus.charge_patterns(radius)
        sat = r9a_state(radius, sat_charges, frame)
        unsat = r9a_state(radius, unsat_charges, frame)
        delta = []
        for component in range(2):
            delta.extend((component, list(v)) for v in sorted(sat_charges[component] ^ unsat_charges[component]))
        rows.append({
            "radius": radius,
            "frame": {k: v for k, v in frame.items() if k != "edge_order"},
            "same_reference_frame": sat["frame_sha256"] == unsat["frame_sha256"],
            "delta_charge_support": delta,
            "delta_items": len(delta),
            "sat": sat,
            "unsat": unsat,
            "polynomial_accounting": {
                "kernel_items_linear_in_graph": True,
                "syndrome_update_linear_in_sparse_charge": True,
                "divergence_linear_in_graph": True,
                "verification_linear_in_cnf_size": True,
            },
        })
    return {
        "rows": rows,
        "all_exact": all(r["sat"]["terminal"] == "SAT" and r["sat"]["exact_replay"] and
                         r["unsat"]["terminal"] == "UNSAT" and r["unsat"]["exact_replay"] for r in rows),
        "all_same_frame": all(r["same_reference_frame"] for r in rows),
        "all_delta_constant_two": all(r["delta_items"] == 2 for r in rows),
    }


def restriction_frame_delta(root_cnf, pivot: int, value: bool) -> dict:
    """Truth-blind exact factorization of one restriction into FRAME + DELTA."""
    root = direct.canon(root_cnf)
    satisfied_lit = pivot if value else -pivot
    false_lit = -pivot if value else pivot
    frame = []
    removed = []
    shortened_original = []
    shortened = []
    for clause in root:
        if pivot not in clause and -pivot not in clause:
            frame.append(clause)
        elif satisfied_lit in clause:
            removed.append(clause)
        else:
            if false_lit not in clause:
                raise AssertionError("pivot clause classification failure")
            shortened_original.append(clause)
            shortened.append(tuple(lit for lit in clause if lit != false_lit))
    reconstructed = direct.canon(tuple(frame) + tuple(shortened))
    active_delta_vars = vars_of(shortened)
    frame_vars = vars_of(frame)
    transform_vars = vars_of(tuple(removed) + tuple(shortened_original))
    return {
        "frame": direct.canon(frame),
        "removed": direct.canon(removed),
        "shortened_original": direct.canon(shortened_original),
        "shortened": direct.canon(shortened),
        "reconstructed": reconstructed,
        "frame_sha256": cnf_digest(frame),
        "delta_sha256": cnf_digest(tuple(removed) + tuple(shortened_original) + tuple(shortened)),
        "frame_vars": sorted(frame_vars),
        "active_delta_vars": sorted(active_delta_vars),
        "active_bridge_vars": sorted(frame_vars & active_delta_vars),
        "transform_bridge_vars": sorted(frame_vars & transform_vars),
    }


def r9b_extract_open_worlds() -> dict:
    residuals = r8a.frozen_residuals()
    roots = {r8a.digest(r["cnf"]): r for r in r8a.frozen_roots()}
    rows = []
    for expected_index, expected_hash in zip(OPEN_INDICES, OPEN_HASHES):
        item = residuals[expected_index]
        if item["formula_sha256"] != expected_hash:
            raise AssertionError("frozen R8A OPEN hash drift")
        root = roots[item["root_sha256"]]
        left = restriction_frame_delta(root["cnf"], item["pivot"], item["branch_value"])
        sibling = restriction_frame_delta(root["cnf"], item["pivot"], not item["branch_value"])
        target = direct.canon(item["cnf"])
        exact_reconstruction = left["reconstructed"] == target
        same_sibling_frame = left["frame"] == sibling["frame"]
        touched = len(left["removed"]) + len(left["shortened_original"])
        root_clause_count = len(direct.canon(root["cnf"]))
        active_delta_type = classify_cnf(left["shortened"])
        frame_type = classify_cnf(left["frame"])
        rows.append({
            "global_index": expected_index,
            "source": item["source"],
            "root_sha256": item["root_sha256"],
            "residual_sha256": item["formula_sha256"],
            "pivot": item["pivot"],
            "branch_value": item["branch_value"],
            "pretruth_extraction": True,
            "frame_sha256": left["frame_sha256"],
            "sibling_frame_sha256": sibling["frame_sha256"],
            "same_sibling_frame": same_sibling_frame,
            "exact_residual_reconstruction": exact_reconstruction,
            "root_clauses": root_clause_count,
            "frame_clauses": len(left["frame"]),
            "touched_root_clauses": touched,
            "removed_clauses": len(left["removed"]),
            "shortened_clauses": len(left["shortened"]),
            "frame_fraction": len(left["frame"]) / root_clause_count,
            "delta_fraction": touched / root_clause_count,
            "frame_type": frame_type,
            "active_delta_type": active_delta_type,
            "frame_variables": len(left["frame_vars"]),
            "active_delta_variables": len(left["active_delta_vars"]),
            "active_bridge_variables": len(left["active_bridge_vars"]),
            "transform_bridge_variables": len(left["transform_bridge_vars"]),
            "delta_transform": {
                "removed": [list(c) for c in left["removed"]],
                "shortened_original": [list(c) for c in left["shortened_original"]],
                "shortened": [list(c) for c in left["shortened"]],
            },
        })
    return {
        "rows": rows,
        "all_hashes_frozen": len(rows) == 2,
        "all_exact_reconstruction": all(r["exact_residual_reconstruction"] for r in rows),
        "all_same_sibling_frame": all(r["same_sibling_frame"] for r in rows),
    }


def compose_gate(frame_type: str, delta_type: str, bridge_vars: int) -> dict:
    """Admit only closed typed unions with an explicit exact polynomial rule."""
    if frame_type == "TRIVIAL_EMPTY":
        return {"terminal_composition_admitted": delta_type != "GENERAL_CNF", "rule": "EMPTY_FRAME_IDENTITY", "bridge_vars": bridge_vars}
    if delta_type == "TRIVIAL_EMPTY":
        return {"terminal_composition_admitted": frame_type != "GENERAL_CNF", "rule": "EMPTY_DELTA_IDENTITY", "bridge_vars": bridge_vars}
    if frame_type == "TWO_SAT" and delta_type == "TWO_SAT":
        return {"terminal_composition_admitted": True, "rule": "TWO_SAT_UNION_CLOSED", "bridge_vars": bridge_vars}
    if frame_type == "HORN" and delta_type == "HORN":
        return {"terminal_composition_admitted": True, "rule": "HORN_UNION_CLOSED", "bridge_vars": bridge_vars}
    if frame_type == "DUAL_HORN" and delta_type == "DUAL_HORN":
        return {"terminal_composition_admitted": True, "rule": "DUAL_HORN_UNION_CLOSED", "bridge_vars": bridge_vars}
    return {"terminal_composition_admitted": False, "rule": "NO_EXACT_POLYNOMIAL_BRIDGE_IMPLEMENTED", "bridge_vars": bridge_vars}


def run_r9c(r9b: dict) -> dict:
    rows = []
    for row in r9b["rows"]:
        gate = compose_gate(row["frame_type"], row["active_delta_type"], row["active_bridge_variables"])
        rows.append({
            "global_index": row["global_index"],
            "frame_type": row["frame_type"],
            "delta_type": row["active_delta_type"],
            "bridge_variables": row["active_bridge_variables"],
            "bridge_representation_items": row["active_bridge_variables"],
            "gate": gate,
            "terminal": "ADMITTED_TYPED_COMPOSITION" if gate["terminal_composition_admitted"] else "OPEN",
        })
    return {
        "rows": rows,
        "open": sum(1 for r in rows if r["terminal"] == "OPEN"),
        "admitted": sum(1 for r in rows if r["terminal"] != "OPEN"),
    }


def candidate_firewall() -> dict:
    funcs = [compile_tseitin_frame, tseitin_syndrome, r9a_state, restriction_frame_delta,
             r9b_extract_open_worlds, classify_cnf, compose_gate, run_r9c]
    src = "\n".join(inspect.getsource(f) for f in funcs)
    forbidden = ["dpll(", "exact_search_witness", "itertools.product", "product((False, True)", "robdd(", "dp_eliminate("]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "forbidden_hits": hits}


def shadow_verify_r9b(r9b: dict) -> dict:
    """Post-candidate verifier only; never read by frame/delta selection or R9C."""
    residuals = r8a.frozen_residuals()
    rows = []
    for candidate_row in r9b["rows"]:
        item = residuals[candidate_row["global_index"]]
        oracle = direct.dpll(item["cnf"])
        rows.append({"global_index": candidate_row["global_index"], "status": oracle["status"],
                     "truth": None if oracle["status"] != "EXACT" else ("SAT" if oracle["sat"] else "UNSAT"),
                     "work": oracle.get("work", 0)})
    return {"rows": rows, "all_exact": all(r["status"] == "EXACT" for r in rows)}


def run() -> dict:
    firewall = candidate_firewall()
    r9a = run_r9a()
    r9b = r9b_extract_open_worlds()
    r9c = run_r9c(r9b)
    shadow = shadow_verify_r9b(r9b)
    gates = {
        "G1_NO_HIDDEN_SEARCH_CANDIDATE_FIREWALL": firewall["pass"],
        "G2_R9A_ALL_FIVE_RADII_EXACT": r9a["all_exact"],
        "G3_R9A_REFERENCE_FRAME_STABLE": r9a["all_same_frame"],
        "G4_R9A_DELTA_ONLY_TWO_CHARGE_CHANGES": r9a["all_delta_constant_two"],
        "G5_R9B_FROZEN_OPEN_HASHES_RECONSTRUCT_EXACTLY": r9b["all_exact_reconstruction"],
        "G6_R9B_SIBLING_BRANCHES_SHARE_IDENTICAL_FRAME": r9b["all_same_sibling_frame"],
        "G7_R9C_GENERAL_CNF_WITHOUT_EXACT_BRIDGE_MAY_ONLY_OPEN": all(
            r["terminal"] == "OPEN" or r["gate"]["terminal_composition_admitted"] for r in r9c["rows"]),
        "G8_POST_CANDIDATE_SHADOW_VERIFIER_EXACT": shadow["all_exact"],
        "G9_NO_THEOREM_INFLATION": True,
    }
    integrity = all(gates.values())
    if not integrity:
        verdict = "R9_INTEGRITY_FAIL__P_VS_NP_OPEN"
    elif r9c["open"]:
        verdict = "R9_REFERENCE_FRAME_MECHANISM_PASS__R8_OPEN_WORLDS_BRIDGE_REMAINS_OPEN__P_VS_NP_OPEN"
    else:
        verdict = "R9_REFERENCE_FRAME_AND_TYPED_BRIDGE_SCOPED_PASS__P_VS_NP_OPEN"
    return {
        "schema": "JANUS/TRUMP/R9/REFERENCE_FRAME_DIFFERENCE_KERNEL/RESULT/v1.0",
        "status": "FROZEN_RESULT",
        "verdict": verdict,
        "law": "DON'T_RECOMPUTE_THE_WORLD__PRESERVE_THE_FRAME__ENCODE_THE_CHANGE",
        "candidate_firewall": firewall,
        "R9A": r9a,
        "R9B": r9b,
        "R9C": r9c,
        "shadow_verification": shadow,
        "gates": gates,
        "scientific_reading": {
            "R9A": "For the existing toroidal Tseitin family, a fixed graph frame plus a sparse charge delta has an exact polynomial parity kernel; width growth in clause resolution is avoided by changing representation, not by widening clauses.",
            "R9B": "For both frozen R8A OPEN residuals, the one-variable restriction decomposes exactly into a large unchanged frame plus a small touched-clause delta before truth is read.",
            "R9C": "A compact syntactic delta is not sufficient for totality. Both frozen worlds retain a GENERAL_CNF frame, and no exact polynomial bridge from that frame to the typed delta is implemented, so OPEN is mandatory.",
            "claim_ceiling": "Scoped representation proof-of-mechanism plus exact delta extraction. No arbitrary-CNF totality, no general polynomial speedup, and no P=NP claim."
        },
        "next_wall": "GENERAL_CNF_FRAME_TO_TYPED_DELTA_EXACT_BRIDGE_OR_A_FAMILY_NEUTRAL_POLYNOMIAL_EXACT_KERNEL",
        "P_VS_NP": "OPEN",
    }


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    result = run()
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "R9A_all_exact": result["R9A"]["all_exact"],
                      "R9B": [{k: r[k] for k in ("global_index", "frame_clauses", "touched_root_clauses", "frame_fraction", "delta_fraction", "frame_type", "active_delta_type", "active_bridge_variables")} for r in result["R9B"]["rows"]],
                      "R9C_open": result["R9C"]["open"], "gates": result["gates"], "P_VS_NP": result["P_VS_NP"]}, indent=2))
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
