from collections import defaultdict

from research.tools.apma_cycle_cut.cycle_cut import compile_canonical_cycle_cut
from research.tools.apma_ss_partial_mosaic.partial_mosaic import compile_source_mosaic
from research.tools.apma_typed_module_forest.module_forest import discover_modules
from research.tools.apma_ss_provenance.apma_ss_controller import solve_source
from research.tools.open_connected_query_message.open_query_message import (
    project_unate_factor,
    project_2cnf_factor,
)
from research.tools.query_factorized_quotient.query_factorized import UNSAT_STATE

SOLVER_KIND = {"2CNF": "2CNF", "HORN3": "HORN", "DUAL_HORN3": "DUAL_HORN"}


def _vars(clauses):
    return {abs(lit) for clause in clauses for lit in clause}


def _eval_cnf(source, assignment):
    return all(any(bool(assignment.get(abs(l), False)) == (l > 0) for l in c) for c in source)

def _module_boundaries(modules):
    var_to_modules = defaultdict(set)
    for module in modules:
        for v in module["vars"]:
            var_to_modules[v].add(module["id"])
    out = {}
    for module in modules:
        out[module["id"]] = tuple(sorted(v for v in module["vars"] if len(var_to_modules[v]) >= 2))
    return out


def _condition(clauses, fixed):
    out = []
    for clause in clauses:
        rem = []
        sat = False
        for lit in clause:
            v = abs(lit)
            if v in fixed:
                if bool(fixed[v]) == (lit > 0):
                    sat = True
                    break
            else:
                rem.append(lit)
        if sat:
            continue
        if not rem:
            return None
        out.append(tuple(rem))
    return tuple(out)

def build_symbolic_projection(source, n):
    mosaic = compile_source_mosaic(source, n)
    state = mosaic.get("state")
    if state is None or state.get("residual"):
        return {"status": "OPEN_MOSAIC_NOT_CLOSED"}
    modules = discover_modules(state)
    boundaries = _module_boundaries(modules)
    messages = []
    records = []
    for module in modules:
        clauses = tuple(module["clauses"])
        boundary = set(boundaries[module["id"]])
        internal = set(module["vars"]) - boundary
        projected = None
        stats = {}
        action = "PURE_BOUNDARY_KEEP"
        if internal:
            projected, stats = project_unate_factor(clauses, boundary)
            if projected is not None:
                action = "PROJECT_UNATE"
            elif module["kind"] == "2CNF":
                projected, stats = project_2cnf_factor(clauses, boundary)
                if projected is not None:
                    action = "PROJECT_2CNF"
            if projected is None:
                projected = clauses
                action = "KEPT_UNSUPPORTED"
        else:
            projected = clauses
        if projected == UNSAT_STATE:
            records.append({"module": module["id"], "kind": module["kind"], "action": action,
                            "boundary": tuple(sorted(boundary)), "internal": tuple(sorted(internal)), "stats": stats})
            return {"status": "CERTIFIED_UNSAT_BY_MODULE_PROJECTION", "modules": modules,
                    "boundaries": boundaries, "records": records}
        messages.extend(projected)
        records.append({"module": module["id"], "kind": module["kind"], "action": action,
                        "boundary": tuple(sorted(boundary)), "internal": tuple(sorted(internal)),
                        "projected_clauses": tuple(projected), "stats": stats})
    morphed = tuple(sorted(set(tuple(c) for c in messages)))
    return {"status": "PROJECTED", "modules": modules, "boundaries": boundaries,
            "records": records, "morphed_source": morphed, "original_source": tuple(source)}

def _merge(dst, src):
    out = dict(dst)
    for v, b in src.items():
        if v in out and out[v] != bool(b):
            return None
        out[v] = bool(b)
    return out


def recover_original_witness(projection, parent_witness, n):
    parent_witness = {int(k): bool(v) for k, v in (parent_witness or {}).items()}
    full = {}
    for module in projection["modules"]:
        boundary = set(projection["boundaries"][module["id"]])
        fixed = {v: parent_witness.get(v, False) for v in boundary}
        conditioned = _condition(module["clauses"], fixed)
        if conditioned is None:
            return None
        solved = solve_source(conditioned, n, SOLVER_KIND[module["kind"]])
        if solved["sat"] is not True:
            return None
        internal = set(module["vars"]) - boundary
        local = dict(fixed)
        for v in internal:
            local[v] = bool(solved["witness"].get(v, False))
        full = _merge(full, local)
        if full is None:
            return None
    for v in range(1, n + 1):
        full.setdefault(v, parent_witness.get(v, False))
    return full


def compile_symbolic_typed_boundary_projection(source, n):
    projection = build_symbolic_projection(source, n)
    if projection["status"] == "CERTIFIED_UNSAT_BY_MODULE_PROJECTION":
        return {"status": "CERTIFIED_UNSAT_SYMBOLIC_PROJECTION", "projection": projection}
    if projection["status"] != "PROJECTED":
        return projection
    parent = compile_canonical_cycle_cut(projection["morphed_source"], n)
    st = parent["status"]
    if st in {"CERTIFIED_UNSAT_CANONICAL_CYCLE_CUT", "CERTIFIED_UNSAT_MODULE_FOREST"}:
        return {"status": "CERTIFIED_UNSAT_SYMBOLIC_PROJECTION", "projection": projection, "parent": parent}
    if st in {"CERTIFIED_SAT_CANONICAL_CYCLE_CUT", "CERTIFIED_SAT_MODULE_FOREST"}:
        witness = recover_original_witness(projection, parent.get("witness"), n)
        if witness is None or not _eval_cnf(source, witness):
            return {"status": "FAIL_WITNESS_RECOVERY", "projection": projection, "parent": parent}
        return {"status": "CERTIFIED_SAT_SYMBOLIC_PROJECTION", "witness": witness,
                "projection": projection, "parent": parent}
    return {"status": "OPEN_AFTER_SYMBOLIC_PROJECTION", "parent_status": st,
            "projection": projection, "parent": parent}
