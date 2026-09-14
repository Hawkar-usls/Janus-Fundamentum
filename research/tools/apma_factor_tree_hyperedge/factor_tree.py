import itertools, math
import itertools, math
from collections import defaultdict, deque

from research.tools.apma_ss_partial_mosaic.partial_mosaic import compile_source_mosaic
from research.tools.apma_typed_module_forest.module_forest import (
    discover_modules,
    encoding_size,
    _native_solve,
)


def _shared_variable_membership(modules):
    out = defaultdict(list)
    for m in modules:
        for v in m["vars"]:
            out[v].append(m["id"])
    return {v: tuple(sorted(ms)) for v, ms in out.items() if len(ms) >= 2}


def build_factor_graph(modules):
    shared = _shared_variable_membership(modules)
    adj = {"M:" + m["id"]: set() for m in modules}
    for v, mids in shared.items():
        vnode = f"V:{v}"
        adj[vnode] = set()
        for mid in mids:
            mnode = "M:" + mid
            adj[mnode].add(vnode)
            adj[vnode].add(mnode)
    return shared, adj


def _forest_parent_order(adj):
    parent, order, roots = {}, [], []
    for start in sorted(adj):
        if start in parent:
            continue
        roots.append(start)
        parent[start] = None
        q = deque([start])
        while q:
            u = q.popleft()
            order.append(u)
            for w in sorted(adj[u]):
                if w == parent[u]:
                    continue
                if w in parent:
                    return None, None, None
                parent[w] = u
                q.append(w)
    return parent, order, roots


def _assignments(vars_):
    vars_ = tuple(sorted(vars_))
    for bits in itertools.product((False, True), repeat=len(vars_)):
        yield dict(zip(vars_, bits))


def _merge(dst, src):
    out = dict(dst)
    for v, b in src.items():
        if v in out and out[v] != b:
            return None
        out[v] = b
    return out


def solve_factor_tree(modules, source, n):
    shared, adj = build_factor_graph(modules)
    parent, order, roots = _forest_parent_order(adj)
    if parent is None:
        return {"status": "OPEN_FACTOR_GRAPH_CYCLE"}

    L = encoding_size(source, n)
    budget = int(math.floor(math.log2(max(2, L))))
    boundary = {m["id"]: {v for v, mids in shared.items() if m["id"] in mids} for m in modules}
    too_wide = {mid: sorted(vs) for mid, vs in boundary.items() if len(vs) > budget}
    if too_wide:
        return {"status": "OPEN_INTERFACE_WIDTH", "budget": budget, "too_wide": too_wide}

    by_id = {m["id"]: m for m in modules}
    messages = {}
    row_count = 0
    for node in reversed(order):
        p = parent[node]
        children = [w for w in sorted(adj[node]) if parent.get(w) == node]
        if node.startswith("V:"):
            v = int(node.split(":", 1)[1])
            allowed = {}
            for b in (False, True):
                if all(b in messages[ch] for ch in children):
                    allowed[b] = True
            messages[node] = allowed
            continue

        mid = node[2:]
        module = by_id[mid]
        pvar = None if p is None else int(p.split(":", 1)[1])
        table = {}
        for a in _assignments(boundary[mid]):
            row_count += 1
            local = _native_solve(module, n, a)
            if not local["sat"]:
                continue
            if any(a[int(ch.split(":", 1)[1])] not in messages[ch] for ch in children):
                continue
            key = () if pvar is None else bool(a[pvar])
            if key not in table:
                table[key] = {"boundary": dict(a), "witness": local["witness"]}
        messages[node] = table

    for root in roots:
        if not root.startswith("M:") or () not in messages[root]:
            return {
                "status": "CERTIFIED_UNSAT_FACTOR_TREE",
                "root": root,
                "budget": budget,
                "row_count": row_count,
                "module_count": len(modules),
            }

    def recover_module(node, key):
        row = messages[node][key]
        out = dict(row["witness"])
        for vnode in sorted(adj[node]):
            if parent.get(vnode) != node:
                continue
            v = int(vnode.split(":", 1)[1])
            out = _merge(out, recover_variable(vnode, bool(row["boundary"][v])))
            if out is None:
                raise AssertionError("factor-tree witness mismatch")
        return out

    def recover_variable(vnode, value):
        v = int(vnode.split(":", 1)[1])
        out = {v: bool(value)}
        for mnode in sorted(adj[vnode]):
            if parent.get(mnode) != vnode:
                continue
            out = _merge(out, recover_module(mnode, bool(value)))
            if out is None:
                raise AssertionError("variable-node witness mismatch")
        return out

    witness = {}
    for root in roots:
        witness = _merge(witness, recover_module(root, ()))
        if witness is None:
            raise AssertionError("factor-tree root witness mismatch")
    return {
        "status": "CERTIFIED_SAT_FACTOR_TREE",
        "witness": witness,
        "budget": budget,
        "row_count": row_count,
        "module_count": len(modules),
        "shared_variable_count": len(shared),
        "max_variable_degree": max((len(ms) for ms in shared.values()), default=0),
        "max_module_boundary": max((len(vs) for vs in boundary.values()), default=0),
    }


def compile_factor_tree_hyperedge(source, n):
    mosaic = compile_source_mosaic(source, n)
    state = mosaic.get("state")
    if state is None or state.get("residual"):
        return {"status": "OPEN_MOSAIC_NOT_CLOSED"}
    modules = discover_modules(state)
    solved = solve_factor_tree(modules, tuple(state["source"]), n)
    solved["modules"] = modules
    return solved
