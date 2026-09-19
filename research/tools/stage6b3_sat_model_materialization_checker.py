#!/usr/bin/env python3
"""Stage6B.3 sealed SAT-model materialization replay.

This checker never invokes RoundingSat. It consumes only the exact sealed
Stage6B.3 authority-run artifact and repairs one infrastructure-only syntax gap:
RoundingSat emits false Boolean assignments as -xN.

Scientific authority still requires:
  * exact sealed solver receipt/status/hash binding;
  * complete, conflict-free PB assignment;
  * exact repaired OPB model replay;
  * independent D/W0/W1/W2 mapping reconstruction;
  * independently reconstructed F-B q-Horn certificate replay;
  * frozen polynomial q-Horn terminal replay.

No smaller-k cascade, shrinking, optimization, or solver search occurs here.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from trump_stage6_qhorn_independent_checker import qhorn_terminal, verify_weights  # noqa: E402
from trump_stage6b_deletion_qhorn_independent_checker import deletion_projection  # noqa: E402

TERM_RE = re.compile(r"([+-]?\d+)\s+(x\d+)")
TARGETS = [1,2,3,4,5,6,7,9,10,11,12,13,14]


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_sha(obj) -> str:
    raw = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def independent_mapping(variable_set):
    mapping = {}
    n = 1
    for v in variable_set:
        mapping[str(v)] = {
            "D": f"x{n}",
            "W0": f"x{n+1}",
            "W1": f"x{n+2}",
            "W2": f"x{n+3}",
        }
        n += 4
    return mapping


def assign_once(assignments, name, value, conflicts, repeats):
    if name in assignments:
        repeats.append({"variable": name, "existing": assignments[name], "new": value})
        if assignments[name] != value:
            conflicts.append({"variable": name, "existing": assignments[name], "new": value})
        return
    assignments[name] = value


def parse_model_text(text: str, expected_vars):
    expected = set(expected_vars)
    v_payloads = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s.startswith("v"):
            continue
        payload = s[1:].strip()
        if payload:
            v_payloads.append(payload)

    if not v_payloads:
        return None, {
            "status": "NO_V_MODEL_LINES",
            "format": None,
            "missing": sorted(expected, key=lambda x: int(x[1:])),
            "extra": [],
            "conflicts": [],
            "repeats": [],
            "unrecognized_tokens": [],
        }

    # Retain compatibility with the frozen accepted binary-bitstring form.
    if len(v_payloads) == 1:
        toks = v_payloads[0].replace(";", " ").split()
        if (
            len(toks) == 1
            and set(toks[0]) <= set("01")
            and len(toks[0]) == len(expected)
        ):
            ordered = sorted(expected, key=lambda x: int(x[1:]))
            model = {name: bit == "1" for name, bit in zip(ordered, toks[0])}
            return model, {
                "status": "COMPLETE",
                "format": "BINARY_V_LINE",
                "missing": [],
                "extra": [],
                "conflicts": [],
                "repeats": [],
                "unrecognized_tokens": [],
            }

    assignments = {}
    conflicts = []
    repeats = []
    extras = []
    unrecognized = []
    formats = set()

    for payload in v_payloads:
        for tok in payload.replace(";", " ").split():
            if tok in ("0", "SAT", "SATISFIABLE"):
                continue

            # Explicit xN=0 / xN=1.
            if "=" in tok:
                name, val = tok.split("=", 1)
                if name in expected and val in ("0", "1"):
                    assign_once(assignments, name, val == "1", conflicts, repeats)
                    formats.add("EQUALS")
                else:
                    unrecognized.append(tok)
                continue

            # RoundingSat native false-literal syntax: -xN.
            if tok.startswith("-x") and tok[2:].isdigit():
                name = "x" + tok[2:]
                if name in expected:
                    assign_once(assignments, name, False, conflicts, repeats)
                    formats.add("ROUNDINGSAT_SIGNED_X")
                else:
                    extras.append(name)
                continue

            # Existing accepted literal syntax: xN / ~xN.
            if tok.startswith("~x") and tok[2:].isdigit():
                name = "x" + tok[2:]
                if name in expected:
                    assign_once(assignments, name, False, conflicts, repeats)
                    formats.add("TILDE_X")
                else:
                    extras.append(name)
                continue
            if tok.startswith("x") and tok[1:].isdigit():
                name = tok
                if name in expected:
                    assign_once(assignments, name, True, conflicts, repeats)
                    formats.add("POSITIVE_X")
                else:
                    extras.append(name)
                continue

            # Retain the previously frozen DIMACS-like integer form.
            try:
                n = int(tok)
            except Exception:
                unrecognized.append(tok)
                continue
            if n == 0:
                continue
            name = f"x{abs(n)}"
            if name in expected:
                assign_once(assignments, name, n > 0, conflicts, repeats)
                formats.add("SIGNED_INTEGER")
            else:
                extras.append(name)

    missing = sorted(expected - set(assignments), key=lambda x: int(x[1:]))
    extra_set = sorted(set(extras) | (set(assignments) - expected), key=lambda x: int(x[1:]))

    receipt = {
        "status": "COMPLETE" if not missing and not extra_set and not conflicts and not unrecognized else "INVALID",
        "format": "+".join(sorted(formats)) if formats else None,
        "assignment_count": len(assignments),
        "expected_assignment_count": len(expected),
        "missing": missing,
        "extra": extra_set,
        "conflicts": conflicts,
        "repeats": repeats,
        "unrecognized_tokens": unrecognized,
    }
    if receipt["status"] != "COMPLETE":
        return None, receipt
    return assignments, receipt


def parse_opb(opb_path: Path):
    constraints = []
    varset = set()
    for line in opb_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("*") or s.startswith(("min:", "max:")):
            continue
        if not s.endswith(";"):
            raise ValueError("OPB constraint missing semicolon")
        s = s[:-1].strip()
        if ">=" in s:
            lhs, rhs = s.rsplit(">=", 1)
            rel = ">="
        elif "=" in s:
            lhs, rhs = s.rsplit("=", 1)
            rel = "="
        elif "<=" in s:
            lhs, rhs = s.rsplit("<=", 1)
            rel = "<="
        else:
            raise ValueError("OPB relation missing")
        terms = []
        for coeff, name in TERM_RE.findall(lhs):
            terms.append((int(coeff), name))
            varset.add(name)
        residue = TERM_RE.sub("", lhs).strip()
        if residue not in ("", "0"):
            raise ValueError(f"unparsed OPB lhs residue {residue!r}")
        constraints.append((terms, rel, int(rhs.strip())))
    return constraints, varset


def replay_opb(constraints, model):
    failures = []
    for ci, (terms, rel, rhs) in enumerate(constraints):
        lhs = sum(coeff * (1 if model[name] else 0) for coeff, name in terms)
        good = lhs >= rhs if rel == ">=" else lhs <= rhs if rel == "<=" else lhs == rhs
        if not good:
            failures.append({
                "constraint_index": ci,
                "lhs": lhs,
                "relation": rel,
                "rhs": rhs,
            })
    return failures


def decode(mapping, model):
    B = []
    weights = {}
    states = {}
    for sv, state_map in mapping.items():
        v = int(sv)
        true_states = [state for state, name in state_map.items() if model[name]]
        if len(true_states) != 1:
            raise ValueError(f"state cardinality failure for original variable {v}: {true_states}")
        state = true_states[0]
        states[sv] = state
        if state == "D":
            B.append(v)
        elif state == "W0":
            weights[str(v)] = 0
            weights[str(-v)] = 2
        elif state == "W1":
            weights[str(v)] = 1
            weights[str(-v)] = 1
        elif state == "W2":
            weights[str(v)] = 2
            weights[str(-v)] = 0
        else:
            raise ValueError(state)
    return sorted(B), weights, states


def verify_one(canonical_path, generation_path, audit_path, opb_path, stdout_path, solver_receipt_path, output_path):
    ca = json.loads(Path(canonical_path).read_text(encoding="utf-8"))
    gr = json.loads(Path(generation_path).read_text(encoding="utf-8"))
    oa = json.loads(Path(audit_path).read_text(encoding="utf-8"))
    sr = json.loads(Path(solver_receipt_path).read_text(encoding="utf-8"))
    opbp = Path(opb_path)
    stdoutp = Path(stdout_path)

    out = {
        "schema": "janus.trump.stage6b3.sat_model_materialization_replay.v1",
        "authority": "SEALED_MODEL_MATERIALIZATION_REPLAY__NO_SOLVER_RERUN",
        "source_boundary_run_id": 35454747120,
        "source_boundary_artifact_id": 10587463384,
        "index": ca["index"],
        "boundary_k": ca["boundary_k"],
        "canonical_cnf_sha256": ca["canonical_cnf_sha256"],
        "OPB_sha256": file_sha(opbp),
        "solver_stdout_sha256": file_sha(stdoutp),
        "solver_receipt_sha256": file_sha(Path(solver_receipt_path)),
        "PB_MODEL_REPLAY_VERIFIED": False,
        "QHORN_WITNESS_REPLAY_VERIFIED": False,
        "solver_rerun": False,
        "smaller_k_tested": False,
        "shrink_executed": False,
        "optimization_executed": False,
    }

    independent_map = independent_mapping(list(ca["variable_set"]))
    failures = []

    if ca.get("status") != "CANONICALIZATION_AUDIT_PASS":
        failures.append("CANONICAL_AUDIT_NOT_PASS")
    if oa.get("status") != "OPB_SEMANTIC_AUDIT_PASS" or oa.get("PB24_SEMANTIC_AUDIT") != "PASS":
        failures.append("PB24_SEMANTIC_AUDIT_NOT_PASS")
    if gr.get("mapping") != independent_map:
        failures.append("GENERATOR_MAPPING_DISAGREES_WITH_INDEPENDENT_MAPPING")
    if gr.get("OPB_sha256") != out["OPB_sha256"] or oa.get("OPB_sha256") != out["OPB_sha256"]:
        failures.append("OPB_HASH_BINDING_MISMATCH")
    if sr.get("OPB_sha256") != out["OPB_sha256"]:
        failures.append("SOLVER_RECEIPT_OPB_HASH_MISMATCH")
    if sr.get("proof_producer_status") != "SAT":
        failures.append("SOURCE_SOLVER_STATUS_NOT_SAT")
    if sr.get("model_source_sha256") != out["solver_stdout_sha256"]:
        failures.append("SOLVER_STDOUT_HASH_MISMATCH")
    if sr.get("parser_rejection_markers"):
        failures.append("SOURCE_SOLVER_PARSER_REJECTION_PRESENT")

    if failures:
        out["failure"] = failures
    else:
        constraints, varset = parse_opb(opbp)
        expected_vars = set(independent_map[state][kind] for state in independent_map for kind in independent_map[state])
        if varset != expected_vars:
            out["failure"] = {
                "OPB_VARIABLE_SET_MISMATCH": {
                    "missing": sorted(expected_vars - varset, key=lambda x: int(x[1:])),
                    "extra": sorted(varset - expected_vars, key=lambda x: int(x[1:])),
                }
            }
        else:
            model, parse_receipt = parse_model_text(
                stdoutp.read_text(encoding="utf-8", errors="replace"),
                expected_vars,
            )
            out["model_parse_receipt"] = parse_receipt
            if model is None:
                out["failure"] = "MODEL_MATERIALIZATION_PARSE_FAIL"
            else:
                out["model_assignment_sha256"] = stable_sha(model)
                opb_failures = replay_opb(constraints, model)
                out["PB_constraint_replay_failures"] = opb_failures
                out["PB_MODEL_REPLAY_VERIFIED"] = len(opb_failures) == 0

                if opb_failures:
                    out["failure"] = "PB_MODEL_REPLAY_FAIL"
                else:
                    try:
                        B, weights, states = decode(independent_map, model)
                        out["decoded_B"] = B
                        out["decoded_B_size"] = len(B)
                        out["decoded_B_sha256"] = stable_sha(B)
                        out["decoded_states_sha256"] = stable_sha(states)
                        out["qhorn_weights_sha256"] = stable_sha(weights)

                        if len(B) > int(ca["boundary_k"]):
                            out["failure"] = "DECODED_B_EXCEEDS_FROZEN_BOUNDARY"
                        else:
                            reduced = deletion_projection(ca["canonical_clauses"], set(B))
                            ok, detail = verify_weights(reduced, weights)
                            out["qhorn_certificate_verified"] = ok
                            if not ok:
                                out["failure"] = {"QHORN_WEIGHT_REPLAY_FAIL": detail}
                            else:
                                terminal = qhorn_terminal(reduced, detail["weights"])
                                out["terminal_replay"] = terminal
                                out["terminal_object_sha256"] = stable_sha(terminal)
                                out["QHORN_WITNESS_REPLAY_VERIFIED"] = bool(
                                    terminal.get("terminal_replay_verified")
                                )
                                if out["QHORN_WITNESS_REPLAY_VERIFIED"]:
                                    out["verdict"] = "VERIFIED_SMALLER_DELETION_QHORN_WITNESS"
                                    out["verified_upper_bound"] = len(B)
                                else:
                                    out["failure"] = "QHORN_TERMINAL_REPLAY_FAIL"
                    except Exception as exc:
                        out["failure"] = f"DECODE_OR_REPLAY_ERROR:{type(exc).__name__}:{exc}"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "index": out["index"],
        "boundary_k": out["boundary_k"],
        "PB_MODEL_REPLAY_VERIFIED": out["PB_MODEL_REPLAY_VERIFIED"],
        "QHORN_WITNESS_REPLAY_VERIFIED": out["QHORN_WITNESS_REPLAY_VERIFIED"],
        "decoded_B_size": out.get("decoded_B_size"),
        "verdict": out.get("verdict"),
        "failure": out.get("failure"),
    }, sort_keys=True))
    return out


def b2_row(b2, index):
    return next(row for row in b2["rows"] if int(row["target_index"]) == index)


def aggregate(root, b2_result, output):
    root = Path(root)
    b2 = json.loads(Path(b2_result).read_text(encoding="utf-8"))
    rows = []

    for index in TARGETS:
        p = root / f"r50g25x_{index:02d}.materialized.json"
        if not p.exists():
            rows.append({
                "index": index,
                "final_B3_verdict": "INFRASTRUCTURE_ERROR",
                "failure": "MISSING_MATERIALIZED_REPLAY",
            })
            continue

        replay = json.loads(p.read_text(encoding="utf-8"))
        prior = b2_row(b2, index)
        m = int(prior["final_B_star_size"])
        k = m - 1
        verdict = replay.get("verdict")

        row = {
            "index": index,
            "Stage6B2_m": m,
            "boundary_k": k,
            "source_solver_status": "SAT",
            "PB_MODEL_REPLAY_VERIFIED": replay.get("PB_MODEL_REPLAY_VERIFIED", False),
            "QHORN_WITNESS_REPLAY_VERIFIED": replay.get("QHORN_WITNESS_REPLAY_VERIFIED", False),
            "decoded_candidate_B": replay.get("decoded_B"),
            "decoded_candidate_B_size": replay.get("decoded_B_size"),
            "decoded_candidate_B_sha256": replay.get("decoded_B_sha256"),
            "qhorn_weights_sha256": replay.get("qhorn_weights_sha256"),
            "terminal_object_sha256": replay.get("terminal_object_sha256"),
            "OPB_sha256": replay.get("OPB_sha256"),
            "solver_stdout_sha256": replay.get("solver_stdout_sha256"),
            "materialized_replay_sha256": file_sha(p),
            "final_B3_verdict": verdict if verdict else "INFRASTRUCTURE_ERROR",
            "verified_upper_bound": replay.get("verified_upper_bound"),
            "exact_distance": None,
            "Stage6B2_B_star_proven_not_minimum_cardinality": (
                verdict == "VERIFIED_SMALLER_DELETION_QHORN_WITNESS"
                and replay.get("decoded_B_size") is not None
                and int(replay["decoded_B_size"]) < m
            ),
            "no_cascade_to_smaller_k": True,
        }
        if replay.get("failure") is not None:
            row["failure"] = replay["failure"]
        rows.append(row)

    counts = dict(collections.Counter(row["final_B3_verdict"] for row in rows))
    out = {
        "schema": "janus.trump.stage6b3.sat_model_materialization_gate.result.v1",
        "authority": "SEALED_STAGE6B3_BOUNDARY_SAT_MODELS_PLUS_INDEPENDENT_DUAL_REPLAY",
        "source_boundary_run_id": 35454747120,
        "source_boundary_artifact_id": 10587463384,
        "source_boundary_artifact_digest": "sha256:ca44eb8eeb8d40cb0a387ef4d08812f759af1164f6512bdef6ab6391f76fe111",
        "solver_rerun": False,
        "rows": rows,
        "verdict_counts": counts,
        "interpretation": {
            "exact_distance_verified_count": 0,
            "lower_bound_authority_obtained": False,
            "reason": "The frozen m-1 boundary instances were SAT, not UNSAT.",
            "new_smaller_witnesses_may_replace_upper_bounds": True,
            "Stage6B2_inclusion_minimal_backdoors_remain_valid_objects": True,
            "Stage6B2_inclusion_minimality_does_not_imply_minimum_cardinality": True,
        },
        "claim_ceiling": {
            "NEW_JANUS_CONTROLLER": "BLOCKED",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "EXACT_DELETION_QHORN_DISTANCE": "NOT_PROVED_BY_SAT_BOUNDARY_RESULTS",
            "FINITE_SMALLER_WITNESSES_IMPLY_ASYMPTOTIC_RESULT": False,
        },
    }
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict_counts": counts,
        "rows": [
            {
                "index": row["index"],
                "m": row.get("Stage6B2_m"),
                "k": row.get("boundary_k"),
                "B_size": row.get("decoded_candidate_B_size"),
                "verdict": row["final_B3_verdict"],
            }
            for row in rows
        ],
    }, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("verify")
    v.add_argument("canonical")
    v.add_argument("generation")
    v.add_argument("opb_audit")
    v.add_argument("opb")
    v.add_argument("solver_stdout")
    v.add_argument("solver_receipt")
    v.add_argument("output")

    a = sub.add_parser("aggregate")
    a.add_argument("materialized_root")
    a.add_argument("stage6b2_result")
    a.add_argument("output")

    ns = ap.parse_args()
    if ns.cmd == "verify":
        verify_one(
            ns.canonical,
            ns.generation,
            ns.opb_audit,
            ns.opb,
            ns.solver_stdout,
            ns.solver_receipt,
            ns.output,
        )
    else:
        aggregate(ns.materialized_root, ns.stage6b2_result, ns.output)


if __name__ == "__main__":
    main()
