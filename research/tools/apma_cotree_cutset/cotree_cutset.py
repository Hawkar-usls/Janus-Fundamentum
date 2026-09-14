import itertools, math
from collections import defaultdict, deque

from research.tools.apma_ss_partial_mosaic.partial_mosaic import compile_source_mosaic
from research.tools.apma_typed_module_forest.module_forest import (
    discover_modules,
    encoding_size,
    build_interaction,
    solve_module_forest,
)


def _vars(clauses):
    return {abs(l) for c in clauses for l in c}


def _raw_interaction(modules):
    var_to_modules = defaultdict(list)
    for m in modules:
        for v in m["vars"]:
            var_to_modules[v].append(m["id"])
    hyper = {v: tuple(sorted(ms)) for v, ms in var_to_modules.items() if len(ms) > 2}
    if hyper:
        return {"status": "OPEN_INTERFACE_HYPEREDGE", "hyperedges": hyper}
    edge_vars = defaultdict(set)
    for v, ms in var_to_modules.items():
        if len(ms) == 2:
            edge_vars[tuple(sorted(ms))].add(v)
    adj = {m["id"]: set() for m in modules}
    for (a, b), vs in edge_vars.items():
        adj[a].add(b); adj[b].add(a)
    return {"status": "GRAPH", "edge_vars": edge_vars, "adj": adj}


def _canonical_spanning_forest(adj):
    seen = set()
    tree_edges = set()
    for root in sorted(adj):
        if root in seen:
            continue
        seen.add(root)
        q = deque([root])
        while q:
            u = q.popleft()
            for v in sorted(adj[u]):
                e = tuple(sorted((u, v)))
                if v not in seen:
                    seen.add(v)
                    tree_edges.add(e)
                    q.append(v)
    all_edges = {tuple(sorted((u, v))) for u in adj for v in adj[u] if u < v}
    return tree_edges, all_edges - tree_edges


def _condition_clauses(clauses, assignment):
    out = []
    for clause in clauses:
        rem = []
        satisfied = False
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                if bool(assignment[v]) == (lit > 0):
                    satisfied = True
                    break
            else:
                rem.append(lit)
        if satisfied:
            continue
        if not rem:
            return None
        out.append(tuple(rem))
    return tuple(out)


def _condition_modules(modules, assignment):
    conditioned = []
    for module in modules:
        clauses = _condition_clauses(module["clauses"], assignment)
        if clauses is None:
            return {"status": "CONTRADICTION", "module": module["id"]}
        conditioned.append({
            "id": module["id"],
            "kind": module["kind"],
            "clauses": clauses,
            "vars": tuple(sorted(_vars(clauses))),
        })
    return {"status": "OK", "modules": conditioned}


def _assignments(vars_):
    vars_ = tuple(sorted(vars_))
    for bits in itertools.product((False, True), repeat=len(vars_)):
        yield dict(zip(vars_, bits))


def _merge_witness(base, extra):
    out = dict(base)
    for v, b in extra.items():
        b = bool(b)
        if v in out and out[v] != b:
            return None
        out[v] = b
    return out


def _complete_witness(witness, n):
    out = {i: False for i in range(1, n + 1)}
    out.update({int(v): bool(b) for v, b in witness.items()})
    return out


def compile_log_cotree_cutset(source, n):
    mosaic = compile_source_mosaic(source, n)
    state = mosaic.get("state")
    if state is None or state.get("residual"):
        return {"status": "OPEN_MOSAIC_NOT_CLOSED"}
    modules = discover_modules(state)
    raw = _raw_interaction(modules)
    if raw["status"] != "GRAPH":
        return {"status": raw["status"], "interaction": raw, "modules": modules}
    L = encoding_size(tuple(state["source"]), n)
    budget = int(math.floor(math.log2(max(2, L))))
    tree_edges, cotree_edges = _canonical_spanning_forest(raw["adj"])
    cutset = set()
    for edge in cotree_edges:
        cutset.update(raw["edge_vars"][edge])
    if len(cutset) > budget:
        return {
            "status": "OPEN_CYCLE_CUTSET_WIDTH",
            "budget": budget,
            "cutset_size": len(cutset),
            "cotree_edge_count": len(cotree_edges),
            "module_count": len(modules),
        }

    branch_count = 0
    total_rows = 0
    open_branches = []
    unsat_branches = []
    for cut_assignment in _assignments(cutset):
        branch_count += 1
        conditioned = _condition_modules(modules, cut_assignment)
        if conditioned["status"] == "CONTRADICTION":
            unsat_branches.append({"assignment": dict(cut_assignment), "reason": "LOCAL_CONTRADICTION", "module": conditioned["module"]})
            continue
        cmodules = conditioned["modules"]
        interaction = build_interaction(cmodules)
        if interaction["status"] != "FOREST":
            return {
                "status": "FAIL_CONDITIONED_INTERACTION_NOT_FOREST",
                "cut_assignment": dict(cut_assignment),
                "conditioned_status": interaction["status"],
            }
        solved = solve_module_forest(cmodules, interaction, tuple(state["source"]), n)
        total_rows += int(solved.get("row_count", 0))
        if solved["status"] == "CERTIFIED_SAT_MODULE_FOREST":
            witness = _merge_witness(cut_assignment, solved["witness"])
            if witness is None:
                return {"status": "FAIL_WITNESS_MERGE"}
            return {
                "status": "CERTIFIED_SAT_COTREE_CUTSET",
                "witness": _complete_witness(witness, n),
                "cutset": tuple(sorted(cutset)),
                "cutset_size": len(cutset),
                "budget": budget,
                "branch_count": branch_count,
                "total_rows": total_rows,
                "module_count": len(modules),
                "cotree_edge_count": len(cotree_edges),
            }
        if solved["status"] == "CERTIFIED_UNSAT_MODULE_FOREST":
            unsat_branches.append({"assignment": dict(cut_assignment), "reason": "FOREST_UNSAT"})
            continue
        open_branches.append({"assignment": dict(cut_assignment), "status": solved["status"]})

    if open_branches:
        return {
            "status": "OPEN_POST_CUTSET_FOREST",
            "cutset": tuple(sorted(cutset)),
            "cutset_size": len(cutset),
            "budget": budget,
            "branch_count": branch_count,
            "total_rows": total_rows,
            "open_branches": open_branches,
            "module_count": len(modules),
            "cotree_edge_count": len(cotree_edges),
        }
    return {
        "status": "CERTIFIED_UNSAT_COTREE_CUTSET",
        "cutset": tuple(sorted(cutset)),
        "cutset_size": len(cutset),
        "budget": budget,
        "branch_count": branch_count,
        "total_rows": total_rows,
        "unsat_branch_count": len(unsat_branches),
        "module_count": len(modules),
        "cotree_edge_count": len(cotree_edges),
        "row_bound": len(modules) * L * L,
    }
