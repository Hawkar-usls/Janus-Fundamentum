from __future__ import annotations
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import hashlib
import importlib.util

HERE = Path(__file__).resolve().parent
V11 = HERE.parent / "trump_apma_novel_composite_transfer"
TC_PATH = V11 / "transfer_core.py"
PINNED_TRANSFER_CRLF_SHA256 = "dba2dc94980081497f30870d962ffff3b536f6e8271176187b061b5fbe0e19dd"
PINNED_TRANSFER_LF_SHA256 = "e1e0f09c521e60d66b38e7adf059204827301adf448a1de4c7a2231a4bec6299"
MAX_RHO = 3

_spec = importlib.util.spec_from_file_location("frozen_v11_transfer_core", TC_PATH)
tc = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(tc)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_frozen_semantics() -> None:
    data = TC_PATH.read_bytes()
    lf = data.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    lf_hash = hashlib.sha256(lf).hexdigest()
    crlf_hash = hashlib.sha256(crlf).hexdigest()
    if lf_hash != PINNED_TRANSFER_LF_SHA256 or crlf_hash != PINNED_TRANSFER_CRLF_SHA256:
        raise RuntimeError(f"FROZEN_TRANSFER_HASH_DRIFT:lf={lf_hash}:crlf={crlf_hash}")


def _clause_key(clause):
    return tuple(sorted(set(int(x) for x in clause), key=lambda z: (abs(z), z < 0)))

def normalize_with_audit(raw):
    records = []
    seen = {}
    for source_index, clause in enumerate(raw):
        source = [int(x) for x in clause]
        s = set(source)
        if any(-x in s for x in s):
            records.append({"source_index": source_index, "source": source, "status": "TAUTOLOGY_DROPPED"})
            continue
        key = _clause_key(source)
        if key in seen:
            records.append({"source_index": source_index, "source": source, "status": "DUPLICATE_DROPPED", "normalized": list(key), "first_source_index": seen[key]})
        else:
            seen[key] = source_index
            records.append({"source_index": source_index, "source": source, "status": "NORMALIZED_RETAINED", "normalized": list(key)})
    normalized = [list(c) for c in tc.canon(raw)]
    rebuilt = sorted(seen, key=lambda c: (len(c), tuple((abs(x), x < 0) for x in c)))
    if normalized != [list(c) for c in rebuilt]:
        raise RuntimeError("FROZEN_CANON_AUDIT_MISMATCH")
    return normalized, {
        "source_clause_count": len(raw),
        "normalized_clause_count": len(normalized),
        "tautology_count": sum(r["status"] == "TAUTOLOGY_DROPPED" for r in records),
        "duplicate_count": sum(r["status"] == "DUPLICATE_DROPPED" for r in records),
        "records": records,
    }

class DSU:
    def __init__(self, values):
        self.parent = {x: x for x in values}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if ra < rb:
            self.parent[rb] = ra
        else:
            self.parent[ra] = rb


def _split_by_separator(cnf, sep):
    sep = tuple(sorted(int(x) for x in sep))
    sep_set = set(sep)
    nonsep = sorted({abs(lit) for clause in cnf for lit in clause if abs(lit) not in sep_set})
    if not nonsep:
        return None, "NO_NON_SEPARATOR_VARIABLES"
    dsu = DSU(nonsep)
    for clause in cnf:
        xs = sorted({abs(lit) for lit in clause if abs(lit) not in sep_set})
        for x in xs[1:]:
            dsu.union(xs[0], x)
    roots = defaultdict(list)
    for v in nonsep:
        roots[dsu.find(v)].append(v)
    components = sorted((tuple(sorted(vs)) for vs in roots.values()), key=lambda vs: vs)
    if len(components) < 2:
        return None, "LT2_COMPONENTS"
    component_id = {v: i for i, vs in enumerate(components) for v in vs}
    groups = [[] for _ in components]
    for clause in cnf:
        ids = {component_id[abs(lit)] for lit in clause if abs(lit) not in sep_set}
        if len(ids) != 1:
            return None, "CLAUSE_NOT_OWNED_BY_EXACTLY_ONE_CHILD"
        groups[next(iter(ids))].append(list(clause))
    if len(groups) < 2 or any(not group for group in groups):
        return None, "LT2_NONEMPTY_CHILDREN"
    if any(len(group) >= len(cnf) for group in groups):
        return None, "NON_PROPER_CHILD"
    for s in sep:
        touches = sum(any(any(abs(lit) == s for lit in clause) for clause in group) for group in groups)
        if touches < 2:
            return None, "SEPARATOR_TOUCH_LT2"
    flattened = [tuple(c) for group in groups for c in group]
    if Counter(flattened) != Counter(tuple(c) for c in cnf):
        raise RuntimeError("SPLIT_CLAUSE_COVERAGE_BROKEN")
    return groups, None


def _separator_score(sep, groups):
    sizes = sorted(len(group) for group in groups)
    return (sizes[0], -sizes[-1], -len(groups), tuple(-x for x in sep))


def find_separator(cnf, max_w):
    if not 1 <= int(max_w) <= MAX_RHO:
        return None, "RHO_OUT_OF_RANGE", None
    variables = tc.vars_of(cnf)
    trace = {"candidate_count": 0, "accepted_candidate_count": 0, "widths_considered": []}
    for width in range(1, int(max_w) + 1):
        best = None
        best_score = None
        trace["widths_considered"].append(width)
        for sep in combinations(variables, width):
            trace["candidate_count"] += 1
            groups, reason = _split_by_separator(cnf, sep)
            if groups is None:
                continue
            trace["accepted_candidate_count"] += 1
            score = _separator_score(sep, groups)
            if best is None or score > best_score:
                best, best_score = (tuple(sep), groups), score
        if best is not None:
            trace["selected_width"] = width
            trace["selected_separator"] = list(best[0])
            trace["selected_score"] = [best_score[0], best_score[1], best_score[2], list(best_score[3])]
            return best, None, trace
    return None, "NO_SEPARATOR", trace


def _frozen_leaf_admitter(cnf):
    result = tc.solve_leaf(cnf, {})
    return bool(result.get("admitted")), result


def _discover(cnf, max_w, admitter, initial_clause_count, trace, depth=0):
    admitted, local = admitter(cnf)
    node = {"depth": depth, "clause_count": len(cnf), "local_admitted": admitted}
    trace.append(node)
    if admitted:
        node["terminal"] = True
        node["local_decision"] = local.get("decision") if isinstance(local, dict) else None
        return [cnf], None
    if depth >= initial_clause_count:
        return None, "DECOMPOSITION_DEPTH_BOUND_BROKEN"
    hit, error, sep_trace = find_separator(cnf, max_w)
    node["separator_search"] = sep_trace
    if hit is None:
        return None, error or "NO_SEPARATOR_OR_LOCAL_ADMISSION"
    sep, groups = hit
    node["separator"] = list(sep)
    node["child_clause_counts"] = [len(group) for group in groups]
    leaves = []
    for child_index, group in enumerate(groups):
        child, child_error = _discover(group, max_w, admitter, initial_clause_count, trace, depth + 1)
        if child_error:
            node["failed_child_index"] = child_index
            return None, child_error
        leaves.extend(child)
    return leaves, None

def discover_leaves(raw, max_w=MAX_RHO, test_only_admitter=None):
    assert_frozen_semantics()
    cnf = [list(c) for c in tc.canon(raw)]
    if not cnf:
        admitted, local = _frozen_leaf_admitter(cnf)
        if not admitted:
            return None, "EMPTY_NORMALIZED_CNF_NOT_ADMITTED", []
        row = {"depth": 0, "clause_count": 0, "local_admitted": True, "terminal": True, "local_decision": local.get("decision")}
        return [cnf], None, [row]
    trace = []
    admitter = _frozen_leaf_admitter if test_only_admitter is None else test_only_admitter
    leaves, error = _discover(cnf, int(max_w), admitter, len(cnf), trace)
    if leaves is not None:
        flattened = [tuple(c) for leaf in leaves for c in leaf]
        if Counter(flattened) != Counter(tuple(c) for c in cnf):
            raise RuntimeError("LEAF_CLAUSE_COVERAGE_BROKEN")
        if len(trace) > 2 * len(cnf) - 1:
            raise RuntimeError("DECOMPOSITION_NODE_BOUND_BROKEN")
    return leaves, error, trace

def complete_boundary_scopes(leaves, max_w=MAX_RHO):
    relation_ids = [f"R{i:04d}" for i in range(len(leaves))]
    leaf_vars = [set(tc.vars_of(leaf)) for leaf in leaves]
    by_variable = defaultdict(list)
    for i, variables in enumerate(leaf_vars):
        for variable in sorted(variables):
            by_variable[variable].append(i)
    shared = {v: tuple(ids) for v, ids in sorted(by_variable.items()) if len(ids) >= 2}
    scopes = {}
    for i, relation_id in enumerate(relation_ids):
        scope = tuple(sorted(v for v in leaf_vars[i] if v in shared))
        if len(scope) > int(max_w):
            detail = {"relation_id": relation_id, "scope": list(scope)}
            return None, "COMPONENT_BOUNDARY_GT_3", detail
        scopes[relation_id] = scope
    data = {"relation_ids": relation_ids, "scopes": scopes, "shared_occurrences": shared}
    return data, None, None

def deterministic_gyo(scopes):
    original = {rid: set(scope) for rid, scope in scopes.items()}
    reduced = {rid: set(scope) for rid, scope in scopes.items()}
    active = set(scopes)
    parents = {}
    trace = []
    if not active:
        return {"alpha_acyclic": True, "root": None, "parents": {}, "edges": [], "trace": trace}
    while len(active) > 1:
        while True:
            degree = Counter(v for rid in active for v in reduced[rid])
            removable_vertices = sorted(v for v, count in degree.items() if count <= 1)
            if not removable_vertices:
                break
            changed = False
            for variable in removable_vertices:
                holders = sorted(rid for rid in active if variable in reduced[rid])
                if not holders:
                    continue
                rid = holders[0]
                reduced[rid].remove(variable)
                trace.append({"op": "VERTEX_REMOVE", "variable": variable, "relation": rid})
                changed = True
            if not changed:
                break
        candidates = []
        for child in sorted(active):
            for parent in sorted(active):
                if child == parent or not reduced[child].issubset(reduced[parent]):
                    continue
                key = (len(reduced[child]), tuple(sorted(reduced[child])), child,
                       len(reduced[parent]), tuple(sorted(reduced[parent])), parent)
                candidates.append((key, child, parent))
        if not candidates:
            residual = {rid: sorted(reduced[rid]) for rid in sorted(active)}
            trace.append({"op": "STUCK_NON_ALPHA_ACYCLIC", "residual": residual})
            return {"alpha_acyclic": False, "root": None, "parents": parents, "edges": [], "trace": trace, "residual": residual}
        _, child, parent = min(candidates, key=lambda item: item[0])
        parents[child] = parent
        trace.append({
            "op": "EDGE_SUBSET_REMOVE",
            "child": child,
            "parent": parent,
            "child_reduced_scope": sorted(reduced[child]),
            "parent_reduced_scope": sorted(reduced[parent]),
        })
        active.remove(child)
    root = min(active)
    parents[root] = None
    edges = []
    for child in sorted(rid for rid in parents if parents[rid] is not None):
        parent = parents[child]
        separator = sorted(original[child] & original[parent])
        edges.append((child, parent, separator))
    return {"alpha_acyclic": True, "root": root, "parents": parents, "edges": edges, "trace": trace}


def running_intersection(scopes, edges):
    nodes = sorted(scopes)
    adjacency = {rid: set() for rid in nodes}
    for a, b, _ in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    failures = []
    variables = sorted({v for scope in scopes.values() for v in scope})
    checked = 0
    for variable in variables:
        holders = sorted(rid for rid in nodes if variable in scopes[rid])
        if len(holders) < 2:
            continue
        checked += 1
        allowed = set(holders)
        seen = {holders[0]}
        stack = [holders[0]]
        while stack:
            current = stack.pop()
            for nxt in adjacency[current]:
                if nxt in allowed and nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        if seen != allowed:
            failures.append({"variable": variable, "holders": holders, "connected": sorted(seen)})
    return {"pass": not failures, "shared_variables_checked": checked, "failures": failures}

def _numeric_graph(relation_ids, gyo):
    index = {rid: i for i, rid in enumerate(relation_ids)}
    adjacency = {i: [] for i in range(len(relation_ids))}
    numeric_edges = []
    for a, b, separator in gyo["edges"]:
        ia, ib = index[a], index[b]
        sep = list(separator)
        adjacency[ia].append((ib, sep))
        adjacency[ib].append((ia, sep))
        numeric_edges.append((ia, ib, sep))
    for i in adjacency:
        adjacency[i].sort(key=lambda row: (row[0], tuple(row[1])))
    return {"adj": adjacency, "edges": numeric_edges}


def _extract_relations(leaves, boundary_data):
    relations = []
    for i, relation_id in enumerate(boundary_data["relation_ids"]):
        boundary = list(boundary_data["scopes"][relation_id])
        relation, error = tc.leaf_relation(leaves[i], boundary)
        if error:
            return None, error
        relations.append(relation)
    return relations, None

def solve_formula_candidate(raw, max_w=MAX_RHO):
    assert_frozen_semantics()
    if not 1 <= int(max_w) <= MAX_RHO:
        return {"admitted": False, "reason": "RHO_OUT_OF_RANGE"}
    normalized, normalization_audit = normalize_with_audit(raw)
    leaves, error, discovery_trace = discover_leaves(normalized, max_w)
    if error:
        return {"admitted": False, "reason": error, "normalization_audit": normalization_audit, "discovery_trace": discovery_trace}
    boundary_data, error, detail = complete_boundary_scopes(leaves, max_w)
    if error:
        return {"admitted": False, "reason": error, "detail": detail, "leaf_count": len(leaves), "discovery_trace": discovery_trace}
    scopes = boundary_data["scopes"]
    gyo = deterministic_gyo(scopes)
    if not gyo["alpha_acyclic"]:
        return {"admitted": False, "reason": "BOUNDARY_HYPERGRAPH_NOT_ALPHA_ACYCLIC", "leaf_count": len(leaves), "gyo": gyo}
    ri = running_intersection(scopes, gyo["edges"])
    if not ri["pass"]:
        return {"admitted": False, "reason": "RUNNING_INTERSECTION_FAIL", "leaf_count": len(leaves), "gyo": gyo, "running_intersection": ri}
    relations, error = _extract_relations(leaves, boundary_data)
    if error:
        return {"admitted": False, "reason": error, "leaf_count": len(leaves)}
    graph = _numeric_graph(boundary_data["relation_ids"], gyo)
    transfer = tc.transfer_join(normalized, leaves, graph, relations)
    if transfer["decision"] not in ("SAT", "UNSAT"):
        return {"admitted": False, "reason": transfer["decision"], "leaf_count": len(leaves)}
    assignment = transfer.get("assignment")
    source_replay = None
    if transfer["decision"] == "SAT":
        source_replay = bool(tc.replay(raw, assignment or {}))
        if not source_replay:
            return {"admitted": False, "reason": "SOURCE_ROOT_REPLAY_FAIL", "assignment": assignment}
    certificate = {
        "kind": "rho_alpha_acyclic_join_tree_transfer_freeze_prep_v0_3",
        "max_separator_width": int(max_w),
        "normalized": normalized,
        "normalization_audit": normalization_audit,
        "leaves": leaves,
        "relation_ids": boundary_data["relation_ids"],
        "boundary_scopes": {rid: list(scope) for rid, scope in scopes.items()},
        "shared_occurrences": {str(v): list(ids) for v, ids in boundary_data["shared_occurrences"].items()},
        "gyo": gyo,
        "running_intersection": ri,
        "graph_edges": [[a, b, list(sep)] for a, b, sep in graph["edges"]],
        "relations": relations,
        "transfer": transfer["certificate"],
        "source_root_replay": source_replay,
    }
    return {
        "admitted": True,
        "decision": transfer["decision"],
        "assignment": assignment,
        "leaf_count": len(leaves),
        "certificate": certificate,
    }


def verify_candidate(raw, result):
    if not result.get("admitted"):
        return {"pass": False, "reason": "RESULT_NOT_ADMITTED"}
    cert = result.get("certificate") or {}
    normalized = [list(c) for c in tc.canon(raw)]
    if cert.get("normalized") != normalized:
        return {"pass": False, "reason": "NORMALIZED_ROOT_MISMATCH"}
    rho = int(cert.get("max_separator_width", MAX_RHO))
    replay_leaves, replay_error, _ = discover_leaves(normalized, rho)
    if replay_error:
        return {"pass": False, "reason": "DISCOVERY_REPLAY_FAILED", "detail": replay_error}
    leaves = cert.get("leaves") or []
    if replay_leaves != leaves:
        return {"pass": False, "reason": "DETERMINISTIC_DISCOVERY_MISMATCH"}
    if Counter(tuple(c) for leaf in leaves for c in leaf) != Counter(tuple(c) for c in normalized):
        return {"pass": False, "reason": "LEAF_COVERAGE_MISMATCH"}
    boundary_data, error, detail = complete_boundary_scopes(leaves, rho)
    if error:
        return {"pass": False, "reason": error, "detail": detail}
    expected_scopes = {rid: list(scope) for rid, scope in boundary_data["scopes"].items()}
    if cert.get("boundary_scopes") != expected_scopes:
        return {"pass": False, "reason": "BOUNDARY_SCOPE_MISMATCH"}
    gyo = deterministic_gyo(boundary_data["scopes"])
    if not gyo["alpha_acyclic"]:
        return {"pass": False, "reason": "RECOMPUTED_NON_ALPHA_ACYCLIC"}
    if cert.get("gyo", {}).get("edges") != gyo.get("edges"):
        return {"pass": False, "reason": "GYO_TREE_MISMATCH"}
    ri = running_intersection(boundary_data["scopes"], gyo["edges"])
    if not ri["pass"]:
        return {"pass": False, "reason": "RUNNING_INTERSECTION_FAIL", "detail": ri}
    relations, error = _extract_relations(leaves, boundary_data)
    if error:
        return {"pass": False, "reason": error}
    if cert.get("relations") != relations:
        return {"pass": False, "reason": "RELATION_REPLAY_MISMATCH"}
    graph = _numeric_graph(boundary_data["relation_ids"], gyo)
    transfer = tc.transfer_join(normalized, leaves, graph, relations)
    if transfer.get("decision") != result.get("decision"):
        return {"pass": False, "reason": "TRANSFER_DECISION_MISMATCH"}
    if result.get("decision") == "SAT" and not tc.replay(raw, result.get("assignment") or {}):
        return {"pass": False, "reason": "SOURCE_ROOT_REPLAY_FAIL"}
    return {"pass": True, "reason": None, "shared_variables_checked": ri["shared_variables_checked"]}
