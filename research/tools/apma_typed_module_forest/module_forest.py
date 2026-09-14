import itertools, math
from collections import defaultdict, deque

from research.tools.apma_ss_partial_mosaic.partial_mosaic import (
    MORPH_SEQUENCE,
    compile_source_mosaic,
)
from research.tools.apma_ss_provenance.apma_ss_controller import solve_source

SOLVER_KIND = {"2CNF": "2CNF", "HORN3": "HORN", "DUAL_HORN3": "DUAL_HORN"}


def _norm_clause(c):
    return tuple(sorted((int(x) for x in c), key=lambda x: (abs(x), x)))


def _vars(clauses):
    return {abs(l) for c in clauses for l in c}


def encoding_size(source, n):
    return 1 + int(n) + len(source) + sum(len(c) for c in source)


def _connected_components(clauses):
    clauses = tuple(sorted(_norm_clause(c) for c in clauses))
    if not clauses:
        return []
    parent = list(range(len(clauses)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b)] = min(a, b)
    seen = {}
    for i, c in enumerate(clauses):
        for v in {abs(l) for l in c}:
            if v in seen:
                union(i, seen[v])
            else:
                seen[v] = i
    groups = defaultdict(list)
    for i, c in enumerate(clauses):
        groups[find(i)].append(c)
    return [tuple(sorted(g)) for _, g in sorted(groups.items(), key=lambda kv: min(kv[1]))]


def discover_modules(state):
    modules = []
    for kind in MORPH_SEQUENCE:
        for idx, comp in enumerate(_connected_components(state["carriers"].get(kind, ()))):
            modules.append({
                "id": f"{kind}:{idx}",
                "kind": kind,
                "clauses": comp,
                "vars": tuple(sorted(_vars(comp))),
            })
    return modules


def build_interaction(modules):
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
    seen = set()
    for start in sorted(adj):
        if start in seen:
            continue
        stack = [(start, None)]
        while stack:
            u, p = stack.pop()
            if u in seen:
                return {"status": "OPEN_MODULE_CYCLE", "edge_vars": edge_vars, "adj": adj}
            seen.add(u)
            for w in sorted(adj[u], reverse=True):
                if w != p:
                    stack.append((w, u))
    return {"status": "FOREST", "edge_vars": edge_vars, "adj": adj}


def _condition(clauses, assignment):
    out = []
    for c in clauses:
        rem = []
        satisfied = False
        for lit in c:
            v = abs(lit)
            if v in assignment:
                if bool(assignment[v]) == (lit > 0):
                    satisfied = True; break
            else:
                rem.append(lit)
        if satisfied:
            continue
        if not rem:
            return None
        out.append(tuple(rem))
    return tuple(out)


def _native_solve(module, n, assignment):
    conditioned = _condition(module["clauses"], assignment)
    if conditioned is None:
        return {"sat": False, "witness": None}
    solved = solve_source(conditioned, n, SOLVER_KIND[module["kind"]])
    if not solved["sat"]:
        return {"sat": False, "witness": None}
    keep = set(module["vars"])
    witness = {v: bool(solved["witness"][v]) for v in keep}
    witness.update({v: bool(b) for v, b in assignment.items() if v in keep})
    return {"sat": True, "witness": witness}


def _assignments(vars_):
    vars_ = tuple(sorted(vars_))
    for bits in itertools.product((False, True), repeat=len(vars_)):
        yield dict(zip(vars_, bits))


def _key(vars_, assignment):
    return tuple(bool(assignment[v]) for v in sorted(vars_))


def _assignment_from_key(vars_, key):
    return dict(zip(sorted(vars_), key))


def _forest_parent_order(adj):
    parent, order, roots = {}, [], []
    for root in sorted(adj):
        if root in parent:
            continue
        roots.append(root); parent[root] = None
        q = deque([root])
        while q:
            u = q.popleft(); order.append(u)
            for v in sorted(adj[u]):
                if v == parent[u]:
                    continue
                if v in parent:
                    continue
                parent[v] = u; q.append(v)
    return parent, order, roots


def _merge_witness(dst, src):
    out = dict(dst)
    for v, b in src.items():
        if v in out and out[v] != b:
            return None
        out[v] = b
    return out


def solve_module_forest(modules, interaction, source, n):
    edge_vars, adj = interaction["edge_vars"], interaction["adj"]
    L = encoding_size(source, n)
    budget = int(math.floor(math.log2(max(2, L))))
    boundary = {m["id"]: set() for m in modules}
    for (a, b), vs in edge_vars.items():
        boundary[a].update(vs); boundary[b].update(vs)
    too_wide = {m: sorted(vs) for m, vs in boundary.items() if len(vs) > budget}
    if too_wide:
        return {"status": "OPEN_INTERFACE_WIDTH", "budget": budget, "too_wide": too_wide}
    by_id = {m["id"]: m for m in modules}
    parent, order, roots = _forest_parent_order(adj)
    tables = {}
    row_count = 0
    for mid in reversed(order):
        m = by_id[mid]
        p = parent[mid]
        psep = set() if p is None else set(edge_vars[tuple(sorted((mid, p)))])
        children = [v for v in sorted(adj[mid]) if parent.get(v) == mid]
        table = {}
        for pa in _assignments(boundary[mid]):
            row_count += 1
            local = _native_solve(m, n, pa)
            if not local["sat"]:
                continue
            ok = True
            for ch in children:
                sep = set(edge_vars[tuple(sorted((mid, ch)))])
                ck = _key(sep, pa)
                if ck not in tables[ch]:
                    ok = False; break
            if not ok:
                continue
            pk = _key(psep, pa)
            if pk not in table:
                table[pk] = {"boundary": dict(pa), "witness": local["witness"]}
        tables[mid] = table

    for root in roots:
        if () not in tables[root]:
            return {
                "status": "CERTIFIED_UNSAT_MODULE_FOREST",
                "root": root,
                "budget": budget,
                "row_count": row_count,
                "module_count": len(modules),
            }
    def recover(mid, key):
        row = tables[mid][key]
        out = dict(row["witness"])
        for ch in sorted(adj[mid]):
            if parent.get(ch) != mid:
                continue
            sep = set(edge_vars[tuple(sorted((mid, ch)))])
            ck = _key(sep, row["boundary"])
            cw = recover(ch, ck)
            out = _merge_witness(out, cw)
            if out is None:
                raise AssertionError("witness merge mismatch")
        return out

    witness = {}
    for root in roots:
        rw = recover(root, ())
        witness = _merge_witness(witness, rw)
        if witness is None:
            raise AssertionError("forest root witness mismatch")
    return {
        "status": "CERTIFIED_SAT_MODULE_FOREST",
        "witness": witness,
        "budget": budget,
        "row_count": row_count,
        "module_count": len(modules),
        "max_boundary": max((len(v) for v in boundary.values()), default=0),
    }


def compile_typed_module_forest(source, n):
    mosaic = compile_source_mosaic(source, n)
    state = mosaic.get("state")
    if state is None or state.get("residual"):
        return {"status": "OPEN_MOSAIC_NOT_CLOSED"}
    modules = discover_modules(state)
    interaction = build_interaction(modules)
    if interaction["status"] != "FOREST":
        return {"status": interaction["status"], "interaction": interaction, "modules": modules}
    solved = solve_module_forest(modules, interaction, tuple(state["source"]), n)
    solved["modules"] = modules
    solved["edge_vars"] = {f"{a}|{b}": sorted(vs) for (a, b), vs in interaction["edge_vars"].items()}
    return solved
