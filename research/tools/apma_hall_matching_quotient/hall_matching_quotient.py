from collections import deque
from itertools import combinations

STATUS_SAT = "CERTIFIED_SAT_HALL_MATCHING_QUOTIENT"
STATUS_UNSAT = "CERTIFIED_UNSAT_HALL_MATCHING_QUOTIENT"
STATUS_REJECT = "REJECT_NOT_CANONICAL_GRAPH_PHP"


def _norm_clause(c):
    return tuple(sorted((int(x) for x in c), key=lambda x: (abs(x), x)))


def _norm_cnf(cnf):
    return tuple(sorted((_norm_clause(c) for c in cnf), key=lambda c: (len(c), c)))


def canonical_graph_php(left_count, right_count, edges, functional=True):
    L = tuple(range(int(left_count)))
    R = tuple(range(int(right_count)))
    E = tuple(sorted({(int(u), int(v)) for u, v in edges}))
    if any(u not in L or v not in R for u, v in E):
        raise ValueError("edge outside bipartition")
    edge_var = {e: i + 1 for i, e in enumerate(E)}
    cnf = []
    by_left = {u: [] for u in L}
    by_right = {v: [] for v in R}
    for e, var in edge_var.items():
        u, v = e
        by_left[u].append(var)
        by_right[v].append(var)
    for u in L:
        cnf.append(tuple(by_left[u]))
    for v in R:
        for a, b in combinations(sorted(by_right[v]), 2):
            cnf.append((-a, -b))
    if functional:
        for u in L:
            for a, b in combinations(sorted(by_left[u]), 2):
                cnf.append((-a, -b))
    return {
        "left_count": len(L), "right_count": len(R), "edges": E,
        "functional": bool(functional), "edge_var": edge_var,
        "cnf": _norm_cnf(cnf),
    }


def recognize(instance):
    try:
        rebuilt = canonical_graph_php(instance["left_count"], instance["right_count"], instance["edges"], instance.get("functional", True))
    except Exception as exc:
        return {"ok": False, "reason": str(exc)}
    source = _norm_cnf(instance.get("cnf", ()))
    if source != rebuilt["cnf"]:
        return {"ok": False, "reason": "canonical CNF mismatch"}
    return {"ok": True, "graph": rebuilt}


def _adj(graph):
    a = {u: [] for u in range(graph["left_count"])}
    for u, v in graph["edges"]:
        a[u].append(v)
    for u in a:
        a[u].sort()
    return a

def maximum_matching(graph):
    adj = _adj(graph)
    match_l, match_r = {}, {}
    operations = 0
    for root in range(graph["left_count"]):
        if root in match_l:
            continue
        q = deque([("L", root)])
        parent = {("L", root): None}
        target = None
        while q and target is None:
            side, x = q.popleft()
            if side == "L":
                for v in adj[x]:
                    operations += 1
                    if match_l.get(x) == v:
                        continue
                    node = ("R", v)
                    if node in parent:
                        continue
                    parent[node] = ("L", x)
                    if v not in match_r:
                        target = node
                        break
                    nxt = ("L", match_r[v])
                    if nxt not in parent:
                        parent[nxt] = node
                        q.append(nxt)
            else:
                raise AssertionError("unexpected queue side")
        if target is None:
            continue
        node = target
        while node is not None and node[0] == "R":
            v = node[1]
            lnode = parent[node]
            u = lnode[1]
            old_v = match_l.get(u)
            match_l[u] = v
            match_r[v] = u
            if old_v is not None and old_v != v:
                match_r.pop(old_v, None)
            node = parent.get(lnode)
    return match_l, match_r, operations


def hall_witness(graph, match_l, match_r):
    adj = _adj(graph)
    zl = set(u for u in range(graph["left_count"]) if u not in match_l)
    zr = set()
    q = deque(("L", u) for u in sorted(zl))
    while q:
        side, x = q.popleft()
        if side == "L":
            for v in adj[x]:
                if match_l.get(x) == v or v in zr:
                    continue
                zr.add(v)
                q.append(("R", v))
        else:
            if x in match_r:
                u = match_r[x]
                if u not in zl:
                    zl.add(u)
                    q.append(("L", u))
    neighborhood = set()
    for u in zl:
        neighborhood.update(adj[u])
    return tuple(sorted(zl)), tuple(sorted(neighborhood))


def verify_matching(graph, matching):
    if set(matching) != set(range(graph["left_count"])):
        return False
    if len(set(matching.values())) != len(matching):
        return False
    edges = set(graph["edges"])
    return all((u, v) in edges for u, v in matching.items())


def verify_hall(graph, S, N):
    S = tuple(sorted(set(int(u) for u in S)))
    N = tuple(sorted(set(int(v) for v in N)))
    if any(u < 0 or u >= graph["left_count"] for u in S):
        return False
    if any(v < 0 or v >= graph["right_count"] for v in N):
        return False
    actual = set()
    adj = _adj(graph)
    for u in S:
        actual.update(adj[u])
    return tuple(sorted(actual)) == N and len(N) < len(S)


def reconstruct_assignment(graph, matching):
    witness = {var: False for var in graph["edge_var"].values()}
    for u, v in matching.items():
        witness[graph["edge_var"][(u, v)]] = True
    return witness


def eval_cnf(cnf, witness):
    for clause in cnf:
        if not any(bool(witness.get(abs(lit), False)) == (lit > 0) for lit in clause):
            return False
    return True


def counting_baseline(instance):
    rec = recognize(instance)
    if not rec["ok"]:
        return {"status": STATUS_REJECT}
    g = rec["graph"]
    if g["left_count"] > g["right_count"]:
        return {"status": "COUNTING_BASELINE_UNSAT", "reason": "m>n"}
    return {"status": "COUNTING_BASELINE_OPEN", "reason": "m<=n"}

def solve(instance):
    rec = recognize(instance)
    if not rec["ok"]:
        return {"status": STATUS_REJECT, "reason": rec.get("reason", "recognizer rejected")}
    graph = rec["graph"]
    match_l, match_r, operations = maximum_matching(graph)
    if len(match_l) == graph["left_count"]:
        if not verify_matching(graph, match_l):
            raise AssertionError("matching verification failed")
        witness = reconstruct_assignment(graph, match_l)
        if not eval_cnf(graph["cnf"], witness):
            raise AssertionError("root CNF witness replay failed")
        return {
            "status": STATUS_SAT,
            "matching": dict(sorted(match_l.items())),
            "witness": witness,
            "matching_operations": operations,
            "certificate_verified": True,
        }
    S, N = hall_witness(graph, match_l, match_r)
    if not verify_hall(graph, S, N):
        raise AssertionError("Hall certificate verification failed")
    return {
        "status": STATUS_UNSAT,
        "hall_S": S,
        "hall_N": N,
        "deficiency": len(S) - len(N),
        "matching_operations": operations,
        "certificate_verified": True,
    }
