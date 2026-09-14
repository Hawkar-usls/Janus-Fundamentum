from collections import defaultdict, deque


def _norm_clause(clause):
    lits = set(int(x) for x in clause if int(x) != 0)
    if any(-x in lits for x in lits):
        return None
    return tuple(sorted(lits, key=lambda x: (abs(x), x)))


def _clean_source(source):
    cleaned = []
    for clause in source:
        c = _norm_clause(clause)
        if c is None:
            continue
        if not c:
            return None, "EMPTY_CLAUSE"
        cleaned.append(c)
    return tuple(sorted(cleaned)), None


def _eval_source(source, witness):
    return all(any(bool(witness.get(abs(l), False)) == (l > 0) for l in c) for c in source)


def _polarity_clause_vars(clause):
    if len(clause) != 3:
        return None, None
    if all(l > 0 for l in clause):
        return "POS", frozenset(abs(l) for l in clause)
    if all(l < 0 for l in clause):
        return "NEG", frozenset(abs(l) for l in clause)
    return None, None


def _clause_components(edges):
    var_to_edges = defaultdict(list)
    for i, edge in enumerate(edges):
        for v in edge:
            var_to_edges[v].append(i)
    unseen = set(range(len(edges)))
    out = []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        q = deque([seed])
        comp = [seed]
        while q:
            i = q.popleft()
            for v in edges[i]:
                for j in var_to_edges[v]:
                    if j in unseen:
                        unseen.remove(j)
                        q.append(j)
                        comp.append(j)
        out.append(tuple(edges[i] for i in sorted(comp)))
    return out


def _verify_windows(sequence, edges):
    expected = [frozenset(sequence[i:i + 3]) for i in range(len(sequence) - 2)]
    lhs = sorted(tuple(sorted(e)) for e in expected)
    rhs = sorted(tuple(sorted(e)) for e in edges)
    return len(expected) == len(edges) and lhs == rhs


def _reconstruct_three_window_path(edges):
    edges = tuple(frozenset(e) for e in edges)
    if not edges or any(len(e) != 3 for e in edges) or len(set(edges)) != len(edges):
        return None
    m = len(edges)
    if m == 1:
        return None
    if m == 2:
        a, b = edges
        shared = sorted(a & b)
        left = sorted(a - b)
        right = sorted(b - a)
        if len(shared) != 2 or len(left) != 1 or len(right) != 1:
            return None
        seq = (left[0], shared[0], shared[1], right[0])
        return seq if len(set(seq)) == 4 and _verify_windows(seq, edges) else None

    adj = {i: set() for i in range(m)}
    for i in range(m):
        for j in range(i + 1, m):
            if len(edges[i] & edges[j]) == 2:
                adj[i].add(j)
                adj[j].add(i)
    endpoints = [i for i in range(m) if len(adj[i]) == 1]
    if len(endpoints) != 2 or sum(len(v) for v in adj.values()) != 2 * (m - 1):
        return None
    if any(len(adj[i]) not in (1, 2) for i in range(m)):
        return None
    start = min(endpoints, key=lambda i: tuple(sorted(edges[i])))
    order = []
    prev = None
    cur = start
    while True:
        order.append(cur)
        nxt = [x for x in sorted(adj[cur]) if x != prev]
        if not nxt:
            break
        if len(nxt) != 1:
            return None
        prev, cur = cur, nxt[0]
        if cur in order:
            return None
    if len(order) != m:
        return None

    e0, e1, e2 = edges[order[0]], edges[order[1]], edges[order[2]]
    shared01 = e0 & e1
    v2s = shared01 & e2
    v1s = shared01 - e2
    v0s = e0 - e1
    v3s = e1 - e0
    if not all(len(x) == 1 for x in (v0s, v1s, v2s, v3s)):
        return None
    seq = [next(iter(v0s)), next(iter(v1s)), next(iter(v2s)), next(iter(v3s))]
    for t in range(2, m):
        new = edges[order[t]] - edges[order[t - 1]]
        if len(new) != 1:
            return None
        seq.append(next(iter(new)))
    seq = tuple(seq)
    if len(set(seq)) != len(seq) or not _verify_windows(seq, edges):
        return None
    return seq


def _canonical_disequality_edges(comp):
    comp = tuple(frozenset(e) for e in comp)
    pairs = set()
    for i in range(len(comp)):
        for j in range(i + 1, len(comp)):
            shared = comp[i] & comp[j]
            if len(shared) == 2:
                a, b = sorted(shared)
                pairs.add((a, b))
    return tuple(sorted(pairs))


def _recover_lines(cleaned):
    by_pol = {"NEG": [], "POS": []}
    for clause in cleaned:
        pol, edge = _polarity_clause_vars(clause)
        if pol is None:
            return None, "OPEN_UNSUPPORTED_CLAUSE_SHAPE"
        by_pol[pol].append(edge)
    records = []
    for pol in ("NEG", "POS"):
        for comp in _clause_components(by_pol[pol]):
            if len(comp) < 2:
                return None, "OPEN_SHORT_LINE_UNORIENTED"
            seq = _reconstruct_three_window_path(comp)
            if seq is None:
                return None, "OPEN_NOT_EXACT_THREE_WINDOW_PATH"
            pairs = _canonical_disequality_edges(comp)
            if len(pairs) != len(comp) - 1:
                return None, "OPEN_NOT_EXACT_THREE_WINDOW_PATH"
            records.append({
                "polarity": pol,
                "line_length": len(seq),
                "clauses": len(comp),
                "disequality_edges": pairs,
            })
    return records, None


def _bipartite_coloring(lines):
    adj = defaultdict(set)
    vertices = set()
    for rec in lines:
        for a, b in rec["disequality_edges"]:
            if a == b:
                return None
            vertices.add(a)
            vertices.add(b)
            adj[a].add(b)
            adj[b].add(a)
    color = {}
    for root in sorted(vertices):
        if root in color:
            continue
        color[root] = False
        q = deque([root])
        while q:
            u = q.popleft()
            for v in sorted(adj[u]):
                want = not color[u]
                if v in color:
                    if color[v] != want:
                        return None
                else:
                    color[v] = want
                    q.append(v)
    return color


def compile_dense_bipartite_grid(source, n=None):
    cleaned, err = _clean_source(source)
    if err is not None:
        return {"status": "OPEN_SOURCE_NORMALIZATION", "reason": err}
    lines, err = _recover_lines(cleaned)
    if err is not None:
        return {"status": err}
    coloring = _bipartite_coloring(lines)
    if coloring is None:
        return {"status": "OPEN_NONBIPARTITE_LINE_GRAPH", "line_count": len(lines)}
    max_var = max((abs(l) for c in cleaned for l in c), default=0)
    bound = max(int(n or 0), max_var)
    witness = {i: bool(coloring.get(i, False)) for i in range(1, bound + 1)}
    if not _eval_source(source, witness):
        return {"status": "FAIL_SOURCE_WITNESS_REPLAY"}
    return {
        "status": "CERTIFIED_SAT_DENSE_BIPARTITE_GRID",
        "witness": witness,
        "line_count": len(lines),
        "negative_lines": sum(1 for r in lines if r["polarity"] == "NEG"),
        "positive_lines": sum(1 for r in lines if r["polarity"] == "POS"),
        "line_lengths": tuple(sorted(r["line_length"] for r in lines)),
        "disequality_edge_count": sum(len(r["disequality_edges"]) for r in lines),
        "certificate": {
            "kind": "EXACT_THREE_WINDOW_PATHS_PLUS_CANONICAL_SHARED_PAIR_BIPARTITE_COLORING",
            "color_classes": {
                "false": tuple(sorted(v for v, b in coloring.items() if not b)),
                "true": tuple(sorted(v for v, b in coloring.items() if b)),
            },
        },
    }
