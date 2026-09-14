import math
from collections import defaultdict, deque


UNSAT = object()


def _norm_clause(clause):
    lits = {int(x) for x in clause if int(x) != 0}
    if any(-x in lits for x in lits):
        return None
    return tuple(sorted(lits, key=lambda x: (abs(x), x)))


def normalize_source(source):
    out = set()
    for clause in source:
        c = _norm_clause(clause)
        if c is None:
            continue
        if not c:
            return ((),)
        out.add(c)
    return tuple(sorted(out))


def encoding_size(source, n):
    norm = normalize_source(source)
    return max(2, int(n) + sum(1 + len(c) for c in norm))


def eval_source(source, witness):
    for clause in source:
        c = _norm_clause(clause)
        if c is None:
            continue
        if not c:
            return False
        if not any(bool(witness.get(abs(l), False)) == (l > 0) for l in c):
            return False
    return True


def _incidence_graph(source):
    adj = defaultdict(set)
    for ci, clause in enumerate(source):
        cnode = ("C", ci)
        adj[cnode]
        for lit in clause:
            vnode = ("V", abs(lit))
            adj[cnode].add(vnode)
            adj[vnode].add(cnode)
    return {k: set(v) for k, v in adj.items()}


def canonical_two_core_variables(source):
    adj = _incidence_graph(source)
    degree = {u: len(vs) for u, vs in adj.items()}
    alive = set(adj)
    q = deque(sorted((u for u in alive if degree[u] < 2), key=str))
    queued = set(q)
    while q:
        u = q.popleft()
        if u not in alive or degree[u] >= 2:
            continue
        alive.remove(u)
        for v in adj[u]:
            if v in alive:
                degree[v] -= 1
                if degree[v] < 2 and v not in queued:
                    q.append(v)
                    queued.add(v)
    return tuple(sorted(u[1] for u in alive if u[0] == "V"))


def _simplify(source, assignment):
    out = []
    for clause in source:
        satisfied = False
        kept = []
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                if bool(assignment[v]) == (lit > 0):
                    satisfied = True
                    break
            else:
                kept.append(lit)
        if satisfied:
            continue
        if not kept:
            return UNSAT
        out.append(tuple(kept))
    return tuple(out)


def _forest_parent_order(source):
    adj = _incidence_graph(source)
    parent = {}
    order = []
    roots = []
    for start in sorted(adj, key=str):
        if start in parent:
            continue
        roots.append(start)
        parent[start] = None
        q = deque([start])
        while q:
            u = q.popleft()
            order.append(u)
            for v in sorted(adj[u], key=str):
                if v == parent[u]:
                    continue
                if v in parent:
                    return None, None, None, adj
                parent[v] = u
                q.append(v)
    return parent, order, roots, adj


def _literal_truth(clause, var, value):
    for lit in clause:
        if abs(lit) == var:
            return bool(value) == (lit > 0)
    raise AssertionError("variable absent from clause")


def solve_incidence_forest(source, n):
    if source is UNSAT:
        return {"status": "UNSAT"}
    if not source:
        return {"status": "SAT", "witness": {i: False for i in range(1, int(n) + 1)}}
    if any(len(c) == 0 for c in source):
        return {"status": "UNSAT"}

    parent, order, roots, adj = _forest_parent_order(source)
    if parent is None:
        return {"status": "RESIDUAL_CYCLE"}

    clause_by_node = {("C", i): clause for i, clause in enumerate(source)}
    msg = {}
    for node in reversed(order):
        children = [v for v in adj[node] if parent.get(v) == node]
        if node[0] == "V":
            feasible = set()
            for value in (False, True):
                if all(value in msg[ch] for ch in children):
                    feasible.add(value)
            msg[node] = feasible
            continue

        clause = clause_by_node[node]
        p = parent[node]
        if p is None:
            raise AssertionError("clause root should not occur in nonempty CNF component")
        pvar = p[1]
        child_possible = all(bool(msg[ch]) for ch in children)
        child_can_satisfy = any(
            any(_literal_truth(clause, ch[1], b) for b in msg[ch])
            for ch in children
        )
        feasible = set()
        if child_possible:
            for pvalue in (False, True):
                if _literal_truth(clause, pvar, pvalue) or child_can_satisfy:
                    feasible.add(pvalue)
        msg[node] = feasible

    witness = {}

    def merge_value(var, value):
        value = bool(value)
        if var in witness and witness[var] != value:
            raise AssertionError("forest witness conflict")
        witness[var] = value

    def recover_var(vnode, value):
        merge_value(vnode[1], value)
        for cnode in sorted((x for x in adj[vnode] if parent.get(x) == vnode), key=str):
            recover_clause(cnode, bool(value))

    def recover_clause(cnode, parent_value):
        clause = clause_by_node[cnode]
        pvar = parent[cnode][1]
        children = sorted((x for x in adj[cnode] if parent.get(x) == cnode), key=str)
        chosen = {}
        already_sat = _literal_truth(clause, pvar, parent_value)
        if not already_sat:
            winner = None
            for vnode in children:
                for b in sorted(msg[vnode]):
                    if _literal_truth(clause, vnode[1], b):
                        winner = (vnode, b)
                        break
                if winner is not None:
                    break
            if winner is None:
                raise AssertionError("message/recovery mismatch")
            chosen[winner[0]] = winner[1]
        for vnode in children:
            if vnode not in chosen:
                if not msg[vnode]:
                    raise AssertionError("empty variable message during recovery")
                chosen[vnode] = sorted(msg[vnode])[0]
            recover_var(vnode, chosen[vnode])

    for root in roots:
        if root[0] != "V":
            raise AssertionError("nonempty CNF component root should be variable")
        allowed = msg[root]
        if not allowed:
            return {"status": "UNSAT"}
        recover_var(root, sorted(allowed)[0])

    full = {i: bool(witness.get(i, False)) for i in range(1, int(n) + 1)}
    if not eval_source(source, full):
        return {"status": "FAIL_FOREST_WITNESS_REPLAY"}
    return {"status": "SAT", "witness": full}


def compile_incidence_2core(source, n):
    norm = normalize_source(source)
    if any(len(c) == 0 for c in norm):
        return {
            "status": "CERTIFIED_UNSAT_INCIDENCE_2CORE",
            "core_width": 0,
            "budget": int(math.floor(math.log2(encoding_size(source, n)))),
            "enumerated_assignments": 0,
            "reason": "EMPTY_CLAUSE",
        }

    L = encoding_size(norm, n)
    budget = int(math.floor(math.log2(max(2, L))))
    core_vars = canonical_two_core_variables(norm)
    k = len(core_vars)
    if k > budget:
        return {
            "status": "OPEN_INCIDENCE_2CORE_WIDTH",
            "core_width": k,
            "budget": budget,
            "encoding_size": L,
            "enumerated_assignments": 0,
        }

    branch_count = 1 << k
    if branch_count > L:
        return {
            "status": "FAIL_INTERNAL_BUDGET_MISMATCH",
            "core_width": k,
            "budget": budget,
            "encoding_size": L,
            "enumerated_assignments": 0,
        }

    tried = 0
    for mask in range(branch_count):
        tried += 1
        core_assignment = {v: bool((mask >> i) & 1) for i, v in enumerate(core_vars)}
        residual = _simplify(norm, core_assignment)
        if residual is UNSAT:
            continue
        solved = solve_incidence_forest(residual, n)
        if solved["status"] == "RESIDUAL_CYCLE":
            return {
                "status": "FAIL_INTERNAL_RESIDUAL_CYCLE",
                "core_width": k,
                "budget": budget,
                "enumerated_assignments": tried,
            }
        if solved["status"].startswith("FAIL_"):
            return {
                "status": solved["status"],
                "core_width": k,
                "budget": budget,
                "enumerated_assignments": tried,
            }
        if solved["status"] == "SAT":
            witness = dict(solved["witness"])
            witness.update(core_assignment)
            witness = {i: bool(witness.get(i, False)) for i in range(1, int(n) + 1)}
            if not eval_source(source, witness):
                return {
                    "status": "FAIL_SOURCE_WITNESS_REPLAY",
                    "core_width": k,
                    "budget": budget,
                    "enumerated_assignments": tried,
                }
            return {
                "status": "CERTIFIED_SAT_INCIDENCE_2CORE",
                "witness": witness,
                "core_width": k,
                "budget": budget,
                "encoding_size": L,
                "enumerated_assignments": tried,
                "branch_bound": branch_count,
                "certificate": {
                    "kind": "CANONICAL_INCIDENCE_2CORE_CUTSET_PLUS_EXACT_FOREST_MESSAGES",
                    "core_variables": core_vars,
                },
            }

    return {
        "status": "CERTIFIED_UNSAT_INCIDENCE_2CORE",
        "core_width": k,
        "budget": budget,
        "encoding_size": L,
        "enumerated_assignments": tried,
        "branch_bound": branch_count,
        "certificate": {
            "kind": "ALL_BOUNDED_CORE_ASSIGNMENTS_EXHAUSTED_WITH_EXACT_FOREST_MESSAGES",
            "core_variables": core_vars,
        },
    }
