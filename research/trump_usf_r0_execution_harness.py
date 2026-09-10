from __future__ import annotations

"""JANUS/TRUMP USF R0 proof-carrying execution harness.

This file freezes the future causal pipeline. It is inert on import. The
freeze gate may run only --synthetic-self-test or --print-schedule; any actual
scheduled instance requires the explicit --run-scheduled switch in a later
gate.
"""

import argparse
import hashlib
import importlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

SCHEMA = "TRUMP_USF_R0_EXECUTION_HARNESS"
VERSION = "1.0"

INFRASTRUCTURE_PARENT_HEAD = "33446263c7780d151dc9131bf4f8ae5d7ee10f60"
USF_R0_PREREG_COMMIT = "542422a741c151cafc03191aaa5808ab46dfa9a0"
TRUTH_PINNING_COMMIT = "08d34d7dde07188eb82ad8dc7c87281a38559c46"
BINARY_COMPLETION_COMMIT = "194143902497e65c225b76ba1f2b267d8b3114e7"
MANDATORY_SELF_TEST_COMPLETION_COMMIT = "33446263c7780d151dc9131bf4f8ae5d7ee10f60"

GENERATOR_PATH = "research/trump_usf_r0_frozen_generators.py"
GENERATOR_GIT_BLOB = "fe33883dc08e7e1eacadf287093aa0bb1f16c19a"

FROZEN_SOURCE_BLOBS = {
    "R37B_CONTROLLER": (
        "experiments/janus_trump_r37b_fixed_certified_portfolio_restart_cycle.py",
        "f37da1c2e1696e35695096a2c748a222af7920cc",
    ),
    "R33": (
        "experiments/janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics.py",
        "c9234a1ef639a009cc6cb4c8a6098fd09bf9affe",
    ),
    "R34": (
        "experiments/janus_trump_r34_affine_xor_terminal_against_tseitin_core.py",
        "7f9bec920fa47af066570d874fe9127dc4b9b968",
    ),
    "R35": (
        "experiments/janus_trump_r35_nonaffine_core_freeze_structure_intake.py",
        "ad237e341d9659d33da0568f134815776c1f95d8",
    ),
    "R35B": (
        "experiments/janus_trump_r35b_single_literal_rup_vivification.py",
        "259d2e38947d09b0c058963ad825a57f2e734203",
    ),
    "R38_TERMINALS": (
        "experiments/janus_trump_r38_portfolio_fixpoint_freeze_structure_intake.py",
        "816b53c390d78af415e580eaf358acf191796205",
    ),
    "WIDTH_REFERENCE": (
        "experiments/trump_r38_fixpoint_to_ba25_factor_graph_diagnostic.py",
        "ea36a6b69f8c6034aa00ae4c4217bbd4d7735750",
    ),
    "BA25": (
        "research/janus_trump_r50g25ba25.py",
        "cad9c5f837d9d3c4e1c4bd4abef40976f2bb36ff",
    ),
    "PREREG": (
        "research/TRUMP_UNIVERSAL_STRUCTURAL_FUNNEL_ADVERSARIAL_FAMILY_PREREGISTRATION_2026-09-10.json",
        "fda7092ec377b18abc0bc192d36610cca2e9f904",
    ),
    "SELF_TEST_RECEIPT": (
        "research/TRUMP_USF_R0_MANDATORY_INFRASTRUCTURE_SELF_TEST_COMPLETION_2026-09-10.json",
        "69e5f73b8dae8be98bab549c88762c5794e80ba0",
    ),
    "GENERATOR": (GENERATOR_PATH, GENERATOR_GIT_BLOB),
}

CADICAL_EXECUTABLE = "/usr/bin/cadical"
CADICAL_SHA256 = "d258dc72e4ec52d434a29f3b2c44dcfd800c10f898cce783f2bf6755b711fb39"
LRAT_CHECK_EXECUTABLE = "/usr/bin/lrat-check"
LRAT_CHECK_SHA256 = "35caa09cb09bc24178ccbddafaedac1f5774190e3ac3d8c9f03cf11e133dee8c"

CADICAL_PACKAGE_VERSION = "1.7.4-1+b1"
CADICAL_RUNTIME_VERSION_FROZEN_OBSERVATION = "1.7.3"
CADICAL_RUNTIME_VERSION_MISMATCH_CLASSIFICATION = (
    "PRESERVED_RUNTIME_VERSION_STRING_MISMATCH_NOT_A_PACKAGE_HASH_FAILURE"
)
CHECKER_ROBUSTNESS_OBSERVATION = {
    "class": "CHECKER_ROBUSTNESS_OBSERVATION",
    "self_test_corrupted_lrat_checker_exit": -11,
    "signal": "SIGSEGV",
    "mathematical_falsifier": False,
    "sealed_infrastructure_rewrite_authorized": False,
    "real_execution_policy": "ANY_NONZERO_OR_CRASHED_CHECKER=>PROOF_CHECKER_FAILURE;NEVER_UNSAT",
}

TERMINAL_CATALOGUE = (
    "EMPTY_CNF_SAT",
    "EMPTY_CLAUSE_UNSAT",
    "2CNF",
    "HORN",
    "AFFINE_XOR_COMPLETE_CNF_BUNDLE",
    "RENAMABLE_HORN",
    "DUAL_HORN",
    "BETA_ACYCLIC",
)

TRUTH_STATES = (
    "SAT_WITNESS_VERIFIED",
    "UNSAT_PROOF_VERIFIED",
    "UNKNOWN_RESOURCE_LIMIT",
    "PROOF_PRODUCER_FAILURE",
    "PROOF_CHECKER_FAILURE",
    "WITNESS_VALIDATION_FAILURE",
    "GENERATOR_INTEGRITY_FAIL",
    "OPEN_UNVERIFIED",
)

CAUSAL_ORDER = (
    "SCHEDULED_INSTANCE_ID",
    "GENERATE",
    "CANONICALIZE",
    "FREEZE_ORIGINAL_CNF_SHA256",
    "RUN_FROZEN_REDUCER",
    "CANONICALIZE_RESIDUAL",
    "FREEZE_RESIDUAL_SHA256",
    "MEASURE_WIDTH_EVIDENCE",
    "TERMINAL_RECOGNITION",
    "OPTIONAL_BA25_PEAK_STATE_DIAGNOSTIC",
    "TRUTH_ORACLE",
)

BA25_MAX_VERIFIED_TAU = 12
BA25_MAX_RESIDUAL_VARIABLES = 512
BA25_MAX_RESIDUAL_CLAUSES = 5000


class HarnessIntegrityError(RuntimeError):
    pass


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(path: str | Path) -> str:
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def assert_source_blobs(root: Path) -> dict[str, dict[str, str]]:
    receipt = {}
    for role, (rel, expected) in FROZEN_SOURCE_BLOBS.items():
        path = root / rel
        if not path.is_file():
            raise HarnessIntegrityError(f"PINNED_SOURCE_MISSING:{role}:{rel}")
        observed = git_blob_sha1(path)
        if observed != expected:
            raise HarnessIntegrityError(
                f"PINNED_SOURCE_BLOB_MISMATCH:{role}:expected={expected}:observed={observed}"
            )
        receipt[role] = {"path": rel, "expected_git_blob": expected, "observed_git_blob": observed}
    return receipt


def load_modules(root: Path):
    assertions = assert_source_blobs(root)
    for rel in ("experiments", "research"):
        p = str(root / rel)
        if p not in sys.path:
            sys.path.insert(0, p)
    gen = importlib.import_module("trump_usf_r0_frozen_generators")
    r33 = importlib.import_module("janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics")
    r34 = importlib.import_module("janus_trump_r34_affine_xor_terminal_against_tseitin_core")
    r35 = importlib.import_module("janus_trump_r35_nonaffine_core_freeze_structure_intake")
    r35b = importlib.import_module("janus_trump_r35b_single_literal_rup_vivification")
    r38 = importlib.import_module("janus_trump_r38_portfolio_fixpoint_freeze_structure_intake")
    width = importlib.import_module("trump_r38_fixpoint_to_ba25_factor_graph_diagnostic")
    ba25 = importlib.import_module("janus_trump_r50g25ba25")
    return assertions, gen, r33, r34, r35, r35b, r38, width, ba25


def _dimacs_sha(gen, formula) -> str:
    return gen.canonical_dimacs_sha256(formula)


def _clv(r33, formula) -> list[int]:
    return list(r33.measure(formula))


def _replay_r33_history(gen, r33, before_formula, result, cycle_index: int):
    active = r33.canonical_formula(before_formula)
    ledger = []
    for step, rec in enumerate(result["history"], 1):
        before = active
        before_sha = _dimacs_sha(gen, before)
        rule = rec["rule"]

        if rule == "TAUTOLOGY_DELETION":
            target = tuple(rec["clause"])
            if target not in active or not r33.is_tautology(target):
                raise HarnessIntegrityError("R33_REPLAY_TAUTOLOGY_CERT_FAIL")
            removed = False
            out = []
            for c in active:
                if not removed and c == target:
                    removed = True
                else:
                    out.append(c)
            active = r33.canonical_formula(out)

        elif rule == "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE":
            lit = int(rec["literal"])
            if (lit,) not in active:
                raise HarnessIntegrityError("R33_REPLAY_UNIT_CERT_FAIL")
            out = []
            for c in active:
                if lit in c:
                    continue
                out.append(tuple(x for x in c if x != -lit))
            active = r33.canonical_formula(out)

        elif rule == "PURE_LITERAL_AUTARKY":
            lit = int(rec["literal"])
            if any(-lit in c for c in active):
                raise HarnessIntegrityError("R33_REPLAY_PURE_CERT_FAIL")
            active = r33.canonical_formula(c for c in active if lit not in c)

        elif rule == "SUBSUMPTION":
            deleted = tuple(rec["deleted"])
            witness = tuple(rec["witness_subclause"])
            if deleted not in active or witness not in active or not set(witness) <= set(deleted):
                raise HarnessIntegrityError("R33_REPLAY_SUBSUMPTION_CERT_FAIL")
            removed = False
            out = []
            for c in active:
                if not removed and c == deleted:
                    removed = True
                else:
                    out.append(c)
            active = r33.canonical_formula(out)

        elif rule == "BLOCKED_CLAUSE_ELIMINATION":
            clause = tuple(rec["clause"])
            lit = int(rec["blocking_literal"])
            if clause not in active or lit not in clause:
                raise HarnessIntegrityError("R33_REPLAY_BLOCKED_SOURCE_FAIL")
            for other in active:
                if -lit not in other:
                    continue
                resolvent = (set(clause) - {lit}) | (set(other) - {-lit})
                if not any(-x in resolvent for x in resolvent):
                    raise HarnessIntegrityError("R33_REPLAY_BLOCKING_CERT_FAIL")
            active = r33.canonical_formula(c for c in active if c != clause)

        elif rule == "BOUNDED_VARIABLE_ELIMINATION":
            x = int(rec["var"])
            pos = tuple(tuple(c) for c in rec["positive"])
            neg = tuple(tuple(c) for c in rec["negative"])
            observed_pos = tuple(c for c in active if x in c)
            observed_neg = tuple(c for c in active if -x in c)
            if pos != observed_pos or neg != observed_neg:
                raise HarnessIntegrityError("R33_REPLAY_BVE_PARENT_CLAUSES_FAIL")
            resolvents = []
            for p in pos:
                for n in neg:
                    r = (set(p) - {x}) | (set(n) - {-x})
                    if any(-l in r for l in r):
                        continue
                    resolvents.append(r33.canonical_clause(r))
            expected_res = tuple(sorted(set(resolvents)))
            recorded_res = tuple(tuple(c) for c in rec["resolvents"])
            if expected_res != recorded_res or len(expected_res) > len(pos) + len(neg):
                raise HarnessIntegrityError("R33_REPLAY_BVE_RESOLVENT_CERT_FAIL")
            removed = set(pos + neg)
            active = r33.canonical_formula([c for c in active if c not in removed] + list(expected_res))
        else:
            raise HarnessIntegrityError(f"R33_REPLAY_UNKNOWN_RULE:{rule}")

        if list(r33.measure(before)) != list(rec["measure_before"]):
            raise HarnessIntegrityError("R33_REPLAY_MEASURE_BEFORE_FAIL")
        if list(r33.measure(active)) != list(rec["measure_after"]):
            raise HarnessIntegrityError("R33_REPLAY_MEASURE_AFTER_FAIL")
        ledger.append({
            "cycle_index": cycle_index,
            "stage": "R33",
            "rule": rule,
            "step": step,
            "before_canonical_dimacs_sha256": before_sha,
            "after_canonical_dimacs_sha256": _dimacs_sha(gen, active),
            "before_CLV": _clv(r33, before),
            "after_CLV": _clv(r33, active),
            "certificate_replay_status": "R33_HISTORY_REPLAY_PASS",
        })

    final = r33.canonical_formula(result["final_formula"])
    if active != final:
        raise HarnessIntegrityError("R33_REPLAY_FINAL_FORMULA_FAIL")
    return active, ledger


def run_frozen_reducer(gen, r33, r34, r35, r35b, formula):
    """Generic adapter of the byte-pinned R37B cycle; no new reduction rule."""
    formula = r33.canonical_formula(formula)
    initial = formula
    initial_clv = r33.measure(initial)
    m, _, n = initial_clv
    state_measure_bound = (m + 1) * (m * n + 1) * (n + 1) - 1
    transformations = []
    cycles = []
    r33_results = []
    terminal = None

    for cycle_index in range(state_measure_bound + 1):
        cycle_before = formula
        rr = r33.simplify(cycle_before)
        after_r33, r33_ledger = _replay_r33_history(gen, r33, cycle_before, rr, cycle_index)
        transformations.extend(r33_ledger)
        r33_results.append(rr)
        cycle = {
            "cycle_index": cycle_index,
            "before_canonical_dimacs_sha256": _dimacs_sha(gen, cycle_before),
            "before_CLV": _clv(r33, cycle_before),
            "R33_terminal": rr["terminal"],
            "R33_after_canonical_dimacs_sha256": _dimacs_sha(gen, after_r33),
            "R33_after_CLV": _clv(r33, after_r33),
        }

        if rr["terminal"] != "STALLED_STACK_LEAN_CORE":
            terminal = rr["terminal"]
            formula = after_r33
            cycle["stop"] = terminal
            cycles.append(cycle)
            break

        recognition = r34.recognize_complete_affine_cnf(after_r33)
        cycle["R34"] = {
            "recognized": bool(recognition["recognized"]),
            "reason": recognition["reason"],
        }
        if recognition["recognized"]:
            solution = r34.solve_gf2_with_certificate(recognition["equations"])
            cert = r34.verify_affine_certificate(after_r33, recognition, solution)
            if not cert["pass"]:
                raise HarnessIntegrityError("R34_AFFINE_CERTIFICATE_REPLAY_FAIL")
            terminal = "AFFINE_XOR_COMPLETE_CNF_BUNDLE"
            formula = after_r33
            cycle["R34"]["certificate_replay_status"] = "PASS"
            cycle["R34"]["sat_diagnostic_only"] = bool(solution["sat"])
            cycle["stop"] = terminal
            cycles.append(cycle)
            break

        rup = r35b.run_candidate(after_r33)
        whole_replay = r35b.independent_certificate_replay(after_r33, rup)
        if not whole_replay["pass"]:
            raise HarnessIntegrityError(f"R35B_INDEPENDENT_REPLAY_FAIL:{whole_replay}")
        active = after_r33
        for rec in rup["history"]:
            before = active
            source = tuple(rec["source_clause"])
            strengthened = tuple(rec["strengthened_clause"])
            assumptions = tuple(rec["assumptions"])
            if not r35b.independent_up_conflict_checker(active, assumptions):
                raise HarnessIntegrityError("R35B_PER_STEP_UP_REPLAY_FAIL")
            active = r35b.replace_clause_with_subclause(active, source, strengthened)
            transformations.append({
                "cycle_index": cycle_index,
                "stage": "R35B",
                "rule": "SINGLE_LITERAL_RUP_VIVIFICATION",
                "step": int(rec["step"]),
                "before_canonical_dimacs_sha256": _dimacs_sha(gen, before),
                "after_canonical_dimacs_sha256": _dimacs_sha(gen, active),
                "before_CLV": _clv(r33, before),
                "after_CLV": _clv(r33, active),
                "certificate_replay_status": "R35B_INDEPENDENT_UP_REPLAY_PASS",
                "internal_formula_hash_before": rec["formula_hash_before"],
                "internal_formula_hash_after": rec["formula_hash_after"],
            })
        after_rup = r33.canonical_formula(rup["final_formula"])
        if active != after_rup:
            raise HarnessIntegrityError("R35B_REPLAY_FINAL_FORMULA_FAIL")
        cycle["R35B"] = {
            "status": rup["status"],
            "successful_strengthenings": rup["successful_strengthenings"],
            "whole_certificate_replay": whole_replay,
            "after_canonical_dimacs_sha256": _dimacs_sha(gen, after_rup),
            "after_CLV": _clv(r33, after_rup),
        }
        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            terminal = "RUP_UNSAT_DIAGNOSTIC"
            formula = after_rup
            cycle["stop"] = terminal
            cycles.append(cycle)
            break
        if _dimacs_sha(gen, after_rup) == _dimacs_sha(gen, after_r33):
            terminal = "STALLED_PORTFOLIO_FIXPOINT"
            formula = after_rup
            cycle["stop"] = terminal
            cycles.append(cycle)
            break
        if not (r33.measure(after_rup) < r33.measure(cycle_before)):
            raise HarnessIntegrityError("R37B_GLOBAL_CLV_DESCENT_FAIL")
        cycle["restart"] = True
        cycles.append(cycle)
        formula = after_rup
    else:
        raise HarnessIntegrityError("R37B_POLYNOMIAL_STATE_BOUND_EXHAUSTED")

    return {
        "controller": "R37B_FIXED_CERTIFIED_PORTFOLIO_RESTART_CYCLE_GENERIC_ADAPTER",
        "new_reduction_rule_added": False,
        "source_controller_blob_asserted": FROZEN_SOURCE_BLOBS["R37B_CONTROLLER"][1],
        "initial_CLV": list(initial_clv),
        "initial_canonical_dimacs_sha256": _dimacs_sha(gen, initial),
        "residual_formula": formula,
        "residual_CLV": _clv(r33, formula),
        "residual_canonical_dimacs_sha256": _dimacs_sha(gen, formula),
        "terminal_status_from_reducer": terminal,
        "cycle_count": len(cycles),
        "cycles": cycles,
        "transformation_ledger": transformations,
        "state_measure_domain_upper_bound": state_measure_bound,
        "_r33_results": r33_results,
    }


def terminal_recognition(r33, r34, r38, formula) -> dict[str, Any]:
    formula = r33.canonical_formula(formula)
    if not formula:
        return {"classification": "TERMINAL_MEMBER", "terminal": "EMPTY_CNF_SAT"}
    if any(len(c) == 0 for c in formula):
        return {"classification": "TERMINAL_MEMBER", "terminal": "EMPTY_CLAUSE_UNSAT"}
    if r33.is_2cnf(formula):
        return {"classification": "TERMINAL_MEMBER", "terminal": "2CNF"}
    if r33.is_horn(formula):
        return {"classification": "TERMINAL_MEMBER", "terminal": "HORN"}
    affine = r34.recognize_complete_affine_cnf(formula)
    if affine["recognized"]:
        return {"classification": "TERMINAL_MEMBER", "terminal": "AFFINE_XOR_COMPLETE_CNF_BUNDLE"}
    rh = r38.renamable_horn_recognition(formula)
    if rh["recognized"]:
        return {"classification": "TERMINAL_MEMBER", "terminal": "RENAMABLE_HORN", "recognizer_receipt": rh}
    dh = r38.dual_horn_recognition(formula)
    if dh["recognized"]:
        return {"classification": "TERMINAL_MEMBER", "terminal": "DUAL_HORN", "recognizer_receipt": dh}
    ba = r38.beta_acyclic_recognition(formula)
    if ba["recognized"]:
        return {"classification": "TERMINAL_MEMBER", "terminal": "BETA_ACYCLIC", "recognizer_receipt": ba}
    return {"classification": "OPEN_CORE", "terminal": None}


def _incidence_graph(formula):
    variables = sorted({abs(l) for c in formula for l in c})
    remap = {v: f"x{i}" for i, v in enumerate(variables)}
    verts = {f"x{i}" for i in range(len(variables))}
    verts |= {f"c{j}" for j in range(len(formula))}
    edges = set()
    for j, clause in enumerate(formula):
        for lit in clause:
            edges.add(tuple(sorted((remap[abs(lit)], f"c{j}"))))
    return verts, edges


def independent_validate_td(vertices, edges, bags, td_edges) -> dict:
    nodes = set(bags)
    if not nodes:
        ok = not vertices and not edges
        return {"pass": ok, "tree": ok, "vertex_coverage": ok, "edge_coverage": ok,
                "running_intersection": ok, "width": -1 if ok else None}
    adj = {n: set() for n in nodes}
    for a, b in td_edges:
        if a not in nodes or b not in nodes or a == b:
            return {"pass": False, "why": "bad_td_edge"}
        adj[a].add(b); adj[b].add(a)
    seen = set(); stack = [min(nodes)]
    while stack:
        x = stack.pop()
        if x in seen: continue
        seen.add(x); stack.extend(adj[x] - seen)
    tree = seen == nodes and len(td_edges) == len(nodes) - 1
    cover = set().union(*bags.values()) if bags else set()
    vertex_coverage = cover == set(vertices)
    edge_coverage = all(any(a in bag and b in bag for bag in bags.values()) for a, b in edges)
    running = True
    if tree and vertex_coverage:
        for v in vertices:
            holders = {n for n, bag in bags.items() if v in bag}
            reached = set(); st = [min(holders)]
            while st:
                x = st.pop()
                if x in reached: continue
                reached.add(x); st.extend((adj[x] & holders) - reached)
            if reached != holders:
                running = False; break
    else:
        running = False
    ok = tree and vertex_coverage and edge_coverage and running
    width = max((len(b) - 1 for b in bags.values()), default=-1) if ok else None
    return {"pass": ok, "tree": tree, "vertex_coverage": vertex_coverage,
            "edge_coverage": edge_coverage, "running_intersection": running, "width": width}


def replay_degeneracy(vertices, edges, certificate) -> dict:
    adj = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    bound = 0
    for rec in certificate:
        v = rec["vertex"]
        if v not in adj:
            return {"pass": False, "why": "missing_vertex"}
        d = len(adj[v])
        if d != rec["degree_at_deletion"] or d != min(len(x) for x in adj.values()):
            return {"pass": False, "why": "degree_or_minimum_mismatch"}
        bound = max(bound, d)
        for u in list(adj[v]): adj[u].discard(v)
        del adj[v]
    return {"pass": not adj, "lower_bound": bound}


def replay_mmw(vertices, edges, certificate) -> dict:
    adj = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    lb = 0
    for rec in certificate:
        v = rec["v"]
        if v not in adj:
            return {"pass": False, "why": "missing_vertex"}
        d = len(adj[v])
        if d != rec["minimum_degree"] or d != min(len(x) for x in adj.values()):
            return {"pass": False, "why": "minimum_degree_mismatch"}
        lb = max(lb, d)
        if rec["operation"] == "DELETE_ISOLATED":
            if d != 0:
                return {"pass": False, "why": "nonisolated_delete"}
            del adj[v]
        elif rec["operation"] == "CONTRACT":
            u = rec["into"]
            if u not in adj[v]:
                return {"pass": False, "why": "contract_nonedge"}
            nv = (adj[v] | adj[u]) - {v, u}
            for w in list(adj[v]): adj[w].discard(v)
            for w in list(adj[u]): adj[w].discard(u)
            del adj[v]
            adj[u] = set(nv)
            for w in nv: adj[w].add(u)
        else:
            return {"pass": False, "why": "unknown_operation"}
    return {"pass": not adj, "lower_bound": lb}


def width_evidence(width_module, formula, label: str) -> dict:
    cert = width_module.structural_certificate(formula, label)
    vertices, edges = _incidence_graph(formula)
    td = cert["_td"]
    independent_td = independent_validate_td(vertices, edges, td["bags"], td["edges"])
    if not independent_td["pass"] or independent_td["width"] != cert["verified_td_upper_bound"]:
        raise HarnessIntegrityError("INDEPENDENT_TD_VALIDATION_FAIL")
    deg = replay_degeneracy(vertices, edges, cert["degeneracy_certificate"])
    mmw = replay_mmw(vertices, edges, cert["minor_min_width_certificate"])
    if not deg["pass"] or not mmw["pass"]:
        raise HarnessIntegrityError("TREEWIDTH_LOWER_BOUND_REPLAY_FAIL")
    lb = max(deg["lower_bound"], mmw["lower_bound"])
    ub = independent_td["width"]
    if lb != cert["treewidth_lower_bound"]:
        raise HarnessIntegrityError("TREEWIDTH_LOWER_BOUND_VALUE_DRIFT")
    out = {k: v for k, v in cert.items() if not k.startswith("_")}
    out["independent_td_validation"] = independent_td
    out["independent_degeneracy_replay"] = deg
    out["independent_minor_min_width_replay"] = mmw
    out["treewidth_interval"] = [lb, ub]
    out["exact_treewidth"] = ub if lb == ub else None
    out["exact_treewidth_certified"] = lb == ub
    return out, cert


def ba25_diagnostic(ba25, width_module, r33, residual, width_private) -> dict:
    c, _, v = r33.measure(residual)
    tau = width_private["verified_td_upper_bound"]
    if tau > BA25_MAX_VERIFIED_TAU or v > BA25_MAX_RESIDUAL_VARIABLES or c > BA25_MAX_RESIDUAL_CLAUSES:
        return {
            "status": "NOT_RUN_RESOURCE_GUARD",
            "verified_tau": tau,
            "limits": {"tau": BA25_MAX_VERIFIED_TAU, "variables": BA25_MAX_RESIDUAL_VARIABLES,
                       "clauses": BA25_MAX_RESIDUAL_CLAUSES},
            "truth_authority": False,
        }
    orig_vars = width_private["_orig_vars"]
    clauses = width_private["_clauses"]
    inst = ba25.embed_cnf(len(orig_vars), clauses)
    factor_vertices, factor_edges = ba25.factor_graph(inst)
    factor_td = width_module.extend_incidence_td_to_ba25(
        width_private["_td"], len(orig_vars), len(clauses)
    )
    ok, td_receipt = ba25.validate_td(factor_vertices, factor_edges, factor_td, claimed_tau=tau)
    if not ok:
        raise HarnessIntegrityError(f"BA25_TD_VALIDATION_FAIL:{td_receipt}")
    dp = ba25.run_dp(inst, factor_td, proof=False)
    wr = ba25.witness_receipt(inst, dp["witness"])
    return {
        "status": "BA25_DIAGNOSTIC_COMPLETE",
        "verified_tau": tau,
        "peak_table_states": dp["max_states"],
        "state_bound": dp["state_bound"],
        "sat_diagnostic": dp["sat"],
        "model_count_diagnostic": dp["count"],
        "witness_receipt": wr,
        "truth_authority": False,
        "independent_truth_oracle_replaced": False,
    }


def parse_complete_assignment(stdout: str, nvars: int) -> dict[int, bool]:
    values = {}
    for raw in stdout.splitlines():
        line = raw.strip()
        if not line.startswith("v"):
            continue
        for tok in line[1:].strip().split():
            lit = int(tok)
            if lit == 0: continue
            v = abs(lit)
            if v < 1 or v > nvars:
                raise ValueError("ASSIGNMENT_LITERAL_OUT_OF_RANGE")
            val = lit > 0
            if v in values and values[v] != val:
                raise ValueError("ASSIGNMENT_CONTRADICTION")
            values[v] = val
    if set(values) != set(range(1, nvars + 1)):
        raise ValueError("ASSIGNMENT_NOT_COMPLETE")
    return values


def validate_original_cnf(formula, assignment) -> dict:
    bad = []
    for i, clause in enumerate(formula, 1):
        if not any(assignment[abs(l)] == (l > 0) for l in clause):
            bad.append(i)
    return {"pass": not bad, "bad_clause_indices_1_based": bad}


def truth_oracle(gen, original_formula) -> dict:
    if sha256_file(CADICAL_EXECUTABLE) != CADICAL_SHA256:
        raise HarnessIntegrityError("CADICAL_EXECUTABLE_HASH_MISMATCH")
    if sha256_file(LRAT_CHECK_EXECUTABLE) != LRAT_CHECK_SHA256:
        raise HarnessIntegrityError("LRAT_CHECK_EXECUTABLE_HASH_MISMATCH")
    dimacs = gen.canonical_dimacs_bytes(original_formula)
    nvars = max((abs(l) for c in original_formula for l in c), default=0)
    with tempfile.TemporaryDirectory(prefix="trump-usf-r0-") as td:
        d = Path(td)
        (d / "INSTANCE.cnf").write_bytes(dimacs)
        producer = [
            "timeout", "--signal=TERM", "--kill-after=30s", "900s",
            CADICAL_EXECUTABLE, "--lrat", "--binary=false", "--quiet",
            "INSTANCE.cnf", "INSTANCE.lrat",
        ]
        cp = subprocess.run(producer, cwd=d, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
        detail = {
            "producer_exit_code": cp.returncode,
            "producer_stdout_sha256": hashlib.sha256(cp.stdout.encode()).hexdigest(),
            "producer_stderr_sha256": hashlib.sha256(cp.stderr.encode()).hexdigest(),
            "solver_stdout_is_authority": False,
        }
        if cp.returncode in (124, 137, 143):
            return {"truth_state": "UNKNOWN_RESOURCE_LIMIT", **detail}
        if cp.returncode == 10:
            try:
                assignment = parse_complete_assignment(cp.stdout, nvars)
                validation = validate_original_cnf(original_formula, assignment)
            except Exception as exc:
                return {"truth_state": "WITNESS_VALIDATION_FAILURE",
                        "witness_error": f"{type(exc).__name__}:{exc}", **detail}
            if not validation["pass"]:
                return {"truth_state": "WITNESS_VALIDATION_FAILURE",
                        "direct_original_cnf_validation": validation, **detail}
            return {"truth_state": "SAT_WITNESS_VERIFIED",
                    "complete_original_assignment": {str(k): v for k, v in sorted(assignment.items())},
                    "direct_original_cnf_validation": validation, **detail}
        if cp.returncode == 20:
            proof = d / "INSTANCE.lrat"
            if not proof.is_file() or proof.stat().st_size == 0:
                return {"truth_state": "PROOF_PRODUCER_FAILURE",
                        "proof_exists": proof.is_file(), **detail}
            checker = [
                "timeout", "--signal=TERM", "--kill-after=30s", "900s",
                LRAT_CHECK_EXECUTABLE, "INSTANCE.cnf", "INSTANCE.lrat",
            ]
            ck = subprocess.run(checker, cwd=d, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, check=False)
            detail.update({
                "proof_exists": True,
                "proof_size_bytes": proof.stat().st_size,
                "proof_sha256": sha256_file(proof),
                "checker_exit_code": ck.returncode,
                "checker_stdout_sha256": hashlib.sha256(ck.stdout.encode()).hexdigest(),
                "checker_stderr_sha256": hashlib.sha256(ck.stderr.encode()).hexdigest(),
                "checker_robustness_observation": CHECKER_ROBUSTNESS_OBSERVATION,
            })
            if ck.returncode in (124, 137, 143):
                return {"truth_state": "UNKNOWN_RESOURCE_LIMIT", **detail}
            if ck.returncode != 0:
                return {"truth_state": "PROOF_CHECKER_FAILURE", **detail}
            return {"truth_state": "UNSAT_PROOF_VERIFIED", **detail}
        return {"truth_state": "PROOF_PRODUCER_FAILURE", **detail}


def instance_identity(gen, record, formula) -> dict:
    c, l, v = gen.formula_counts(formula)
    return {
        "scheduled_instance_id": record.scheduled_instance_id,
        "lane": record.lane,
        "family_id": record.family_id,
        "cohort": record.cohort,
        "variant": record.variant,
        "frozen_size_parameter": {record.size_parameter_name: record.size_parameter},
        "frozen_seed_string": record.frozen_seed_string,
        "canonical_DIMACS_bytes_SHA256": gen.canonical_dimacs_sha256(formula),
        "variable_count": v,
        "clause_count": c,
        "literal_count": l,
    }


def run_scheduled_instance(instance_id: str, root: Path, *, execute_truth: bool = True) -> dict:
    assertions, gen, r33, r34, r35, r35b, r38, width, ba25 = load_modules(root)
    record = gen.scheduled_instance(instance_id, allow_holdout=False)
    try:
        generated = gen.generate(record)
    except gen.GeneratorIntegrityError as exc:
        return {
            "schema": "TRUMP_USF_R0_INSTANCE_RESULT",
            "scheduled_instance_id": instance_id,
            "truth_state": "GENERATOR_INTEGRITY_FAIL",
            "generator_error": str(exc),
            "retained": True,
            "finite_experiment_is_asymptotic_authority": False,
            "H1": "OPEN", "H2": "OPEN", "H3": "OPEN",
            "SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "BA26_STARTED": False,
        }

    original = gen.canonical_formula(generated.formula)
    identity = instance_identity(gen, record, original)
    reducer = run_frozen_reducer(gen, r33, r34, r35, r35b, original)
    residual = gen.canonical_formula(reducer.pop("residual_formula"))
    residual_sha = gen.canonical_dimacs_sha256(residual)
    if residual_sha != reducer["residual_canonical_dimacs_sha256"]:
        raise HarnessIntegrityError("RESIDUAL_CANONICAL_HASH_DRIFT")

    before_width, before_private = width_evidence(width, original, "ORIGINAL")
    after_width, after_private = width_evidence(width, residual, "RESIDUAL")
    terminal = terminal_recognition(r33, r34, r38, residual)
    ba25_result = ba25_diagnostic(ba25, width, r33, residual, after_private)

    truth = truth_oracle(gen, original) if execute_truth else {"truth_state": "OPEN_UNVERIFIED"}
    if truth["truth_state"] not in TRUTH_STATES:
        raise HarnessIntegrityError("UNKNOWN_TRUTH_STATE")

    lb_before, ub_before = before_width["treewidth_interval"]
    lb_after, ub_after = after_width["treewidth_interval"]
    residual_v = after_width["variable_count"]
    n = record.size_parameter
    metrics = {
        "rho_n": (lb_after / residual_v) if residual_v > 0 else None,
        "r_n": (ub_after / math.log2(n)) if n is not None and n > 1 else None,
        "width_drop_certificate_condition_LBbefore_gt_UBafter": lb_before > ub_after,
        "width_drop_certificate_scope": "ONE_TRAJECTORY_ONLY_NOT_H1",
    }

    return {
        "schema": "TRUMP_USF_R0_INSTANCE_RESULT",
        "version": "1.0",
        "causal_order": list(CAUSAL_ORDER),
        "instance_identity_frozen_before_solver_output": identity,
        "generator_integrity_status": generated.generator_integrity_status,
        "generator_spec_version": generated.generator_spec_version,
        "source_blob_assertions": assertions,
        "original_canonical_dimacs_sha256": identity["canonical_DIMACS_bytes_SHA256"],
        "reducer": reducer,
        "residual_canonical_dimacs_sha256": residual_sha,
        "width_evidence": {"before": before_width, "after": after_width,
                           "interval_before": [lb_before, ub_before],
                           "interval_after": [lb_after, ub_after]},
        "terminal_recognition": terminal,
        "BA25_diagnostic": ba25_result,
        "truth_oracle": truth,
        "discovery_metrics_diagnostic_only": metrics,
        "retained": True,
        "postselection_allowed": False,
        "truth_may_influence_generation_reducer_width_terminal_retention_or_later_seed": False,
        "finite_experiment_is_asymptotic_authority": False,
        "finite_execution_allowed_roles": [
            "DISCOVER_CANDIDATE_FAMILY_THEOREM",
            "DISCOVER_CANDIDATE_HARD_CORE_FAMILY",
            "FALSIFY_INCORRECTLY_SPECIFIED_FINITE_IMPLEMENTATION_CLAIM",
        ],
        "H1": "OPEN", "H2": "OPEN", "H3": "OPEN",
        "SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "BA26_STARTED": False,
    }


def synthetic_self_test(root: Path) -> dict:
    assertions, gen, r33, r34, r35, r35b, r38, width, ba25 = load_modules(root)
    g = gen.synthetic_self_test()
    synthetic_formula = gen.canonical_formula(((1,), (-1, 2), (3, -3)))
    red = run_frozen_reducer(gen, r33, r34, r35, r35b, synthetic_formula)
    residual = gen.canonical_formula(red.pop("residual_formula"))
    w, _ = width_evidence(width, residual, "SYNTHETIC_INFRASTRUCTURE_ONLY")
    t = terminal_recognition(r33, r34, r38, residual)
    assert g["generated_real_USF_instances"] == 0
    return {
        "schema": "TRUMP_USF_R0_EXECUTION_HARNESS_SYNTHETIC_SELF_TEST",
        "pass": True,
        "source_blob_assertions": assertions,
        "generator_synthetic_self_test": g,
        "synthetic_reducer_terminal": red["terminal_status_from_reducer"],
        "synthetic_width_interval": w["treewidth_interval"],
        "synthetic_terminal_recognition": t,
        "truth_oracle_invoked": False,
        "scheduled_instance_generate_function_called": False,
        "generated_real_USF_instances": 0,
        "generated_lane_A_instances": 0,
        "generated_lane_B_instances": 0,
        "generated_lane_C_instances": 0,
        "discovery_execution_started": False,
        "holdout_execution_started": False,
        "finite_experiment_is_asymptotic_authority": False,
        "H1": "OPEN", "H2": "OPEN", "H3": "OPEN",
        "SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "BA26_STARTED": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--synthetic-self-test", action="store_true")
    parser.add_argument("--print-schedule", action="store_true")
    parser.add_argument("--run-scheduled")
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if args.synthetic_self_test:
        out = synthetic_self_test(root)
    elif args.print_schedule:
        _, gen, *_ = load_modules(root)
        out = {
            "discovery_order": [x.scheduled_instance_id for x in gen.DISCOVERY_SCHEDULE],
            "holdout_order_frozen_but_unopened": [
                x.scheduled_instance_id for x in gen.HOLDOUT_SCHEDULE_FROZEN_BUT_UNOPENED
            ],
            "generated_real_USF_instances": 0,
            "discovery_execution_started": False,
        }
    elif args.run_scheduled:
        out = run_scheduled_instance(args.run_scheduled, root, execute_truth=True)
    else:
        raise SystemExit("FREEZE_INERT: choose --synthetic-self-test, --print-schedule, or later --run-scheduled")

    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
