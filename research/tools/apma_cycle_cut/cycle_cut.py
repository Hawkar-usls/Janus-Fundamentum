import itertools, math
from collections import deque

from research.tools.apma_ss_partial_mosaic.partial_mosaic import compile_source_mosaic
from research.tools.apma_typed_module_forest.module_forest import (
    build_interaction,
    compile_typed_module_forest,
    discover_modules,
    encoding_size,
)


def _condition_source(source, assignment):
    out = []
    for clause in source:
        rem = []
        satisfied = False
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                if bool(assignment[v]) == (lit > 0):
                    satisfied = True
                    break
            else:
                rem.append(int(lit))
        if satisfied:
            continue
        if not rem:
            return None
        out.append(tuple(rem))
    return tuple(out)


def _canonical_spanning_forest(adj):
    tree_edges = set()
    parent = {}
    for root in sorted(adj):
        if root in parent:
            continue
        parent[root] = None
        q = deque([root])
        while q:
            u = q.popleft()
            for v in sorted(adj[u]):
                if v in parent:
                    continue
                parent[v] = u
                tree_edges.add(tuple(sorted((u, v))))
                q.append(v)
    return tree_edges

def _cycle_cut(interaction):
    edge_vars = interaction["edge_vars"]
    adj = interaction["adj"]
    tree_edges = _canonical_spanning_forest(adj)
    all_edges = set(edge_vars)
    non_tree = tuple(sorted(all_edges - tree_edges))
    cut = set()
    for edge in non_tree:
        cut.update(edge_vars[edge])
    return {
        "tree_edges": tuple(sorted(tree_edges)),
        "non_tree_edges": non_tree,
        "cut_variables": tuple(sorted(cut)),
    }


def _cut_assignments(vars_):
    vars_ = tuple(vars_)
    for bits in itertools.product((False, True), repeat=len(vars_)):
        yield dict(zip(vars_, bits))


def _merge_fixed_witness(witness, fixed):
    out = {int(k): bool(v) for k, v in (witness or {}).items()}
    for v, b in fixed.items():
        if v in out and out[v] != bool(b):
            return None
        out[v] = bool(b)
    return out

def compile_canonical_cycle_cut(source, n):
    mosaic = compile_source_mosaic(source, n)
    state = mosaic.get("state")
    if state is None or state.get("residual"):
        return {"status": "OPEN_MOSAIC_NOT_CLOSED"}
    modules = discover_modules(state)
    interaction = build_interaction(modules)
    if interaction["status"] == "OPEN_INTERFACE_HYPEREDGE":
        return {"status": "OPEN_INTERFACE_HYPEREDGE", "interaction": interaction}
    if interaction["status"] == "FOREST":
        out = compile_typed_module_forest(source, n)
        out["route"] = "SEALED_FOREST_DELEGATION"
        out["cut_variables"] = ()
        out["cut_assignment_count"] = 1
        return out
    if interaction["status"] != "OPEN_MODULE_CYCLE":
        return {"status": interaction["status"]}

    cut_info = _cycle_cut(interaction)
    cut_vars = cut_info["cut_variables"]
    L = encoding_size(source, n)
    budget = int(math.floor(math.log2(max(2, L))))
    if len(cut_vars) > budget:
        return {
            "status": "OPEN_CYCLE_CUT_WIDTH",
            "cut_variables": cut_vars,
            "cut_width": len(cut_vars),
            "budget": budget,
            "non_tree_edges": cut_info["non_tree_edges"],
        }
    branches = []
    total_rows = 0
    saw_open = False
    for fixed in _cut_assignments(cut_vars):
        conditioned = _condition_source(source, fixed)
        if conditioned is None:
            branches.append({"assignment": fixed, "status": "CERTIFIED_UNSAT_BY_CONDITION"})
            continue
        result = compile_typed_module_forest(conditioned, n)
        st = result["status"]
        total_rows += int(result.get("row_count", 0))
        branches.append({"assignment": fixed, "status": st})
        if st == "CERTIFIED_SAT_MODULE_FOREST":
            witness = _merge_fixed_witness(result.get("witness"), fixed)
            if witness is None:
                return {"status": "FAIL_WITNESS_MERGE"}
            return {
                "status": "CERTIFIED_SAT_CANONICAL_CYCLE_CUT",
                "witness": witness,
                "cut_variables": cut_vars,
                "cut_width": len(cut_vars),
                "budget": budget,
                "cut_assignment_count": len(branches),
                "total_rows": total_rows,
                "non_tree_edges": cut_info["non_tree_edges"],
                "branches": branches,
            }
        if st != "CERTIFIED_UNSAT_MODULE_FOREST":
            saw_open = True

    if saw_open:
        return {
            "status": "OPEN_CONDITIONED_FOREST_CAPABILITY",
            "cut_variables": cut_vars,
            "cut_width": len(cut_vars),
            "budget": budget,
            "cut_assignment_count": 1 << len(cut_vars),
            "total_rows": total_rows,
            "branches": branches,
        }
    return {
        "status": "CERTIFIED_UNSAT_CANONICAL_CYCLE_CUT",
        "cut_variables": cut_vars,
        "cut_width": len(cut_vars),
        "budget": budget,
        "cut_assignment_count": 1 << len(cut_vars),
        "total_rows": total_rows,
        "non_tree_edges": cut_info["non_tree_edges"],
        "branches": branches,
    }
