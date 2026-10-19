#!/usr/bin/env python3
"""JANUS R5 exact adaptive gearbox for cubic graph 3-edge-coloring.

Three gears share ONE complete DFS frontier; switching only changes
sound domain filtering, never deletes unexplored alternatives.
GEAR 2: vertex + small cut parity + bounded failed-literal probes
GEAR 1: vertex + two-edge-cut parity
GEAR 0: vertex-only all-different propagation (fast default fallback)

This is a correct FINITE exponential-backtracking solver, NOT an n^C
algorithm and NOT a proof of P=NP. UNKNOWN_RESOURCE_LIMIT preserves the
frontier for exact resumption without false negative verdicts.
Python 3.11 standard library; no external dependencies.
"""
import argparse
from collections import Counter
from itertools import combinations, permutations
import hashlib
import json
from pathlib import Path

COLORS = (1, 2, 4)
PERMS = tuple(permutations(COLORS, 3))


def graph_info(n, input_edges):
    assert n % 2 == 0 and n >= 4
    edges = tuple(sorted(tuple(sorted(e)) for e in input_edges))
    assert len(edges) == 3 * n // 2
    assert len(edges) == len(set(edges))
    assert all(0 <= u < v < n for u, v in edges)
    incidence = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        incidence[u].append(i)
        incidence[v].append(i)
    assert all(len(row) == 3 for row in incidence)
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # Disconnected inputs are allowed. Their colorings combine componentwise.
    # Preprocessing must not mistake old disconnectedness for a bridge.
    return {"n": n, "edges": edges,
            "incidence": tuple(tuple(row) for row in incidence)}


def graph_hash(graph):
    raw = json.dumps([graph["n"], graph["edges"]],
                     separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def disconnected_component(graph, omitted):
    """First component after removing the specified edge indices."""
    n, edges = graph["n"], graph["edges"]
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        if i not in omitted:
            adj[u].append(v)
            adj[v].append(u)
    unseen = set(range(n))
    while unseen:
        root = min(unseen)
        seen = {root}
        queue = [root]
        unseen.remove(root)
        for u in queue:
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    unseen.remove(v)
                    queue.append(v)
        # A component created by edge deletion has a nonempty boundary.
        # An original disconnected component has empty boundary.
        boundary = {i for i, (u, v) in enumerate(edges)
                    if (u in seen) != (v in seen)}
        if boundary:
            assert boundary.issubset(omitted)
            return seen
    return None


def precompute_cuts(graph, max_triples=20000):
    """Polynomial-budget sampling of exact 1/2/3-edge cuts.

    Ignoring unchecked cuts can ONLY weaken pruning. No derived cut
    is accepted without an explicit component and boundary check.
    """
    edges = graph["edges"]
    singles, pairs, triples = set(), set(), set()
    for i in range(len(edges)):
        component = disconnected_component(graph, {i})
        if component is not None:
            singles.add(i)
    if singles:
        return {"bridges": sorted(singles), "equal": [], "triples": [],
                "triples_examined": 0, "triples_complete": False}
    for comb in combinations(range(len(edges)), 2):
        S = disconnected_component(graph, set(comb))
        if S is None:
            continue
        boundary = tuple(i for i, (u, v) in enumerate(edges)
                         if (u in S) != (v in S))
        if len(boundary) == 2:
            pairs.add(boundary)
    count = 0
    complete = True
    for comb in combinations(range(len(edges)), 3):
        if count >= max_triples:
            complete = False
            break
        count += 1
        S = disconnected_component(graph, set(comb))
        if S is None:
            continue
        boundary = tuple(i for i, (u, v) in enumerate(edges)
                         if (u in S) != (v in S))
        if len(boundary) == 3:
            triples.add(boundary)
    return {"bridges": [], "equal": sorted(pairs), "triples": sorted(triples),
            "triples_examined": count, "triples_complete": complete}


def domain_count(state):
    return sum(x.bit_count() for x in state)


def propagate(state, vertex_factors, cut_info, gear, stats):
    """Every elimination is licensed by a necessary vertex/cut relation."""
    work = list(state)
    triples = list(vertex_factors)
    if gear >= 2:
        triples += cut_info["triples"]
    equal_pairs = cut_info["equal"] if gear >= 1 else ()
    gained = 0
    while True:
        changed = False
        for a, b, c in triples:
            stats["triple_checks"] += 1
            support = [0, 0, 0]
            for x, y, z in PERMS:
                if (work[a] & x) and (work[b] & y) and (work[c] & z):
                    support[0] |= x
                    support[1] |= y
                    support[2] |= z
            if not all(support):
                return None, gained
            for index, supported in zip((a, b, c), support):
                fresh = work[index] & supported
                if fresh != work[index]:
                    gained += work[index].bit_count() - fresh.bit_count()
                    work[index] = fresh
                    changed = True
        for a, b in equal_pairs:
            stats["equal_checks"] += 1
            common = work[a] & work[b]
            if not common:
                return None, gained
            for index in (a, b):
                if work[index] != common:
                    gained += work[index].bit_count() - common.bit_count()
                    work[index] = common
                    changed = True
        if not changed:
            return tuple(work), gained


def strong_failed_literal(state, vertex_factors, cut_info, stats,
                          probe_edges=2):
    """Bounded deterministic one-step lookahead (no unsound truncation)."""
    current = state
    removed = 0
    candidates = sorted(
        (i for i, d in enumerate(current) if d.bit_count() > 1),
        key=lambda i: (current[i].bit_count(), i)
    )[:probe_edges]
    for edge in candidates:
        for color in COLORS:
            if not (current[edge] & color):
                continue
            stats["probes"] += 1
            trial = list(current)
            trial[edge] = color
            attempt, _ = propagate(
                tuple(trial), vertex_factors, cut_info, 1, stats
            )
            if attempt is None:
                stats["failed_literals"] += 1
                current = list(current)
                current[edge] &= ~color
                removed += 1
                if not current[edge]:
                    return None, removed
                current = tuple(current)
    if removed:
        current, _ = propagate(current, vertex_factors, cut_info, 2, stats)
    return current, removed


def choose_edge(state, graph):
    """Deterministic MRV, then maximum assigned-neighbor pressure."""
    incidence = graph["incidence"]
    endpoints = [None] * len(state)
    for v, group in enumerate(incidence):
        for e in group:
            if endpoints[e] is None:
                endpoints[e] = []
            endpoints[e].append(v)

    def weight(i):
        pressure = sum(
            state[j].bit_count() == 1
            for v in endpoints[i] for j in incidence[v] if j != i
        )
        return state[i].bit_count(), -pressure, i

    return min((i for i, d in enumerate(state) if d.bit_count() > 1),
               key=weight)


def verify_coloring(graph, state):
    if not all(x in COLORS for x in state):
        return False
    return all({state[i] for i in group} == set(COLORS)
               for group in graph["incidence"])

def verify_holyer_exact_one_witness(graph, state):
    """Independent check of square+cubic+linear positive 1-in-3 embedding.

    x_(e,c) is one exactly when edge e receives color c.
    Every variable participates in one edge-row and two vertex-color rows.
    """
    if not verify_coloring(graph, state):
        return False
    n, m = graph["n"], len(graph["edges"])
    x = {(e, c): int(state[e] == COLORS[c])
         for e in range(m) for c in range(3)}
    rows = [set((e, c) for c in range(3)) for e in range(m)]
    rows += [set((e, c) for e in graph["incidence"][v])
             for v in range(n) for c in range(3)]
    assert len(rows) == 3*m == len(x)
    assert all(len(row) == 3 for row in rows)
    assert all(sum(x[k] for k in row) == 1 for row in rows)
    occurrences = Counter(k for row in rows for k in row)
    assert all(count == 3 for count in occurrences.values())
    assert all(len(rows[i] & rows[j]) <= 1
               for i in range(len(rows)) for j in range(i))
    return True




def default_stats():
    return {"nodes": 0, "dead": 0, "branches": 0,
            "triple_checks": 0, "equal_checks": 0,
            "probes": 0, "failed_literals": 0,
            "forced_bits": 0, "gear_changes": [],
            "gear_node_histogram": [0, 0, 0],
            "gear_since_node": 0, "gear_baseline_probes": 0,
            "gear_baseline_failed": 0, "gear_baseline_dead": 0}


def gearbox_shift(gear, stats, previous, adaptive, window):
    """Deterministic no-loss heuristic: downshift expensive methods when
    they give little extra pruning; temporarily upshift if cheap gear
    produces mostly contradictions. A shift NEVER discards DFS nodes.
    """
    if not adaptive or window <= 0 or stats["nodes"] % window:
        return gear
    # Use a complete residency window rather than reacting to two
    # unproductive probes. This avoids premature downshifts on Petersen,
    # where global failed-literal pruning only becomes useful later.
    dn = stats["nodes"] - stats["gear_since_node"]
    probes = stats["probes"] - stats["gear_baseline_probes"]
    failed = stats["failed_literals"] - stats["gear_baseline_failed"]
    deaths = stats["dead"] - stats["gear_baseline_dead"]
    equal_since_last_window = (
        stats["equal_checks"] - previous["equal_checks"]
    )
    if gear == 2 and dn >= max(8, window) and probes >= 12 and failed == 0:
        new, reason = 1, "sustained costly lookahead with zero failed literals"
    elif gear == 1 and dn >= max(4, window) and equal_since_last_window == 0:
        new, reason = 0, "no two-edge-cut constraints to justify balanced gear"
    elif gear == 0 and dn >= max(6, window) and deaths >= max(4, dn * 3 // 4):
        new, reason = 2, "cheap gear produced many dead branches; precision rescue"
    else:
        new, reason = gear, ""
    if new != gear:
        stats["gear_changes"].append({
            "at_node": stats["nodes"], "from": gear,
            "to": new, "reason": reason,
        })
        stats["gear_since_node"] = stats["nodes"]
        stats["gear_baseline_probes"] = stats["probes"]
        stats["gear_baseline_failed"] = stats["failed_literals"]
        stats["gear_baseline_dead"] = stats["dead"]
    return new


def solve(graph, max_nodes=None, resume=None, checkpoint=None,
          start_gear=2, adaptive=True, adapt_every=8,
          cut_budget=20000, probe_edges=2):
    if resume is not None:
        cp = json.loads(Path(resume).read_text(encoding="utf-8"))
        if cp["version"] != 1 or cp["graph_hash"] != graph_hash(graph):
            raise ValueError("checkpoint graph hash/version mismatch")
        frontier = [tuple(x) for x in cp["frontier"]]
        gear = cp["gear"]
        stats = cp["stats"]
        cut_budget = cp["cut_budget"]
        adapt_every = cp["adapt_every"]
        adaptive = cp["adaptive"]
        probe_edges = cp["probe_edges"]
        last = cp["window_previous"]
    else:
        frontier = [(7,) * len(graph["edges"])]
        gear, stats, last = start_gear, default_stats(), default_stats()
    assert 0 <= gear <= 2
    # Cheap fixed gears never precompute expensive 3-edge-cut relations.
    # Adaptive sessions retain the high-gear cut table for future upshifts.
    triple_budget = cut_budget if (adaptive or gear == 2) else 0
    cuts = precompute_cuts(graph, max_triples=triple_budget)
    if cuts["bridges"]:
        result = {"verdict": "UNSAT", "reason": "cubic graph has a bridge",
                  "bridge_edges": [list(graph["edges"][i])
                                   for i in cuts["bridges"]]}
        return {**result, "stats": stats, "frontier_size": 0,
                "cuts": {k: len(v) if isinstance(v, list) else v
                         for k, v in cuts.items()}}

    limit = float("inf") if max_nodes is None else stats["nodes"]+max_nodes
    factors = tuple(graph["incidence"])
    while frontier and stats["nodes"] < limit:
        current = frontier.pop()
        stats["nodes"] += 1
        stats["gear_node_histogram"][gear] += 1
        before = domain_count(current)
        filtered, _ = propagate(current, factors, cuts, gear, stats)
        if filtered is not None and gear == 2 and probe_edges:
            filtered, _ = strong_failed_literal(
                filtered, factors, cuts, stats, probe_edges=probe_edges
            )
        if filtered is None:
            stats["dead"] += 1
        else:
            stats["forced_bits"] += before - domain_count(filtered)
            if all(x in COLORS for x in filtered):
                if not verify_coloring(graph, filtered):
                    raise AssertionError("unverified SAT witness")
                return {
                    "verdict": "SAT",
                    "edge_colors": [COLORS.index(x) for x in filtered],
                    "stats": stats,
                    "frontier_size": len(frontier),
                    "cuts": {k: len(v) if isinstance(v, list) else v
                             for k, v in cuts.items()},
                }
            e = choose_edge(filtered, graph)
            for color in reversed(COLORS):
                if filtered[e] & color:
                    child = list(filtered)
                    child[e] = color
                    frontier.append(tuple(child))
                    stats["branches"] += 1
        if adaptive and adapt_every and stats["nodes"] % adapt_every == 0:
            gear = gearbox_shift(
                gear, stats, last, adaptive, adapt_every
            )
            last = {key: stats[key] for key in
                    ("nodes", "failed_literals", "probes",
                     "equal_checks", "dead")}
    if not frontier:
        return {"verdict": "UNSAT", "reason": "complete exhaustive DFS",
                "stats": stats, "frontier_size": 0}
    if checkpoint is not None:
        record = {
            "version": 1, "graph_hash": graph_hash(graph),
            "frontier": [list(x) for x in frontier],
            "gear": gear, "stats": stats,
            "cut_budget": cut_budget,
            "adapt_every": adapt_every,
            "adaptive": adaptive,
            "probe_edges": probe_edges,
            "window_previous": last
        }
        Path(checkpoint).write_text(
            json.dumps(record, separators=(",", ":"), sort_keys=True),
            encoding="utf-8"
        )
    return {"verdict": "UNKNOWN_RESOURCE_LIMIT", "reason": "node budget",
            "stats": stats, "frontier_size": len(frontier),
            "checkpoint_written": checkpoint}


def fixtures():
    # Imports are local so the program is also usable with a custom JSON graph.
    from r5_tutte_deficit_local_trap_20261014 import N12_EDGES, controls
    from r5_tutte_hall_decomposition_20261014 import N10_EDGES
    return {
        "K4": (4, tuple(combinations(range(4), 2)), True),
        "K33": (6, tuple((u, v) for u in range(3)
                          for v in range(3, 6)), True),
        "Petersen": (10, controls()[2][1], False),
        "SAT_Hall10": (10, N10_EDGES, True),
        "SAT_Imbalance12": (12, N12_EDGES, True),
        "K4x2": (8,
                 tuple(list(tuple(combinations(range(4), 2))) +
                       [(u+4, v+4) for u, v in combinations(range(4), 2)]),
                 True),
        "K4x10": (
            40,
            tuple((4*b+u, 4*b+v) for b in range(10)
                  for u, v in combinations(range(4), 2)),
            True,
        ),
        "Bridge10": (10, tuple(
            [e for e in combinations(range(4), 2) if e != (0, 1)]
            + [(0, 8), (1, 8)]
            + [(u+4, v+4) for u, v in combinations(range(4), 2)
               if (u, v) != (0, 1)]
            + [(4, 9), (5, 9), (8, 9)]
        ), False),
        "CirculantBipartite20": (
            20,
            tuple((u, 10 + ((u + d) % 10))
                  for u in range(10) for d in (0, 1, 3)),
            True,
        ),
        "CirculantBipartite60": (
            60,
            tuple((u, 30 + ((u + d) % 30))
                  for u in range(30) for d in (0, 1, 3)),
            True,
        ),
    }


def self_test():
    from tempfile import TemporaryDirectory
    result = {}
    for name, (n, edges, expected_sat) in fixtures().items():
        graph = graph_info(n, edges)
        outputs = {}
        for gear in (0, 1, 2):
            out = solve(graph, start_gear=gear, adaptive=False,
                        cut_budget=5000)
            assert (out["verdict"] == "SAT") == expected_sat, (name, gear, out)
            if expected_sat:
                domains = tuple(COLORS[c] for c in out["edge_colors"])
                assert verify_coloring(graph, domains)
                assert verify_holyer_exact_one_witness(graph, domains)
            outputs[str(gear)] = {
                "verdict": out["verdict"], "nodes": out["stats"]["nodes"],
                "probes": out["stats"]["probes"],
                "triple_checks": out["stats"]["triple_checks"],
                "failed_literals": out["stats"]["failed_literals"],
            }
        auto = solve(graph, adaptive=True, adapt_every=2, cut_budget=5000)
        assert (auto["verdict"] == "SAT") == expected_sat
        outputs["automatic"] = {
            "verdict": auto["verdict"], "nodes": auto["stats"]["nodes"],
            "probes": auto["stats"]["probes"],
            "triple_checks": auto["stats"]["triple_checks"],
            "failed_literals": auto["stats"]["failed_literals"],
            "gear_changes": auto["stats"]["gear_changes"]}
        result[name] = outputs

    # Real, not simulated, gear transitions on 10 independent K4 blocks.
    # The strong gear's failed-literal probes yield no refutations here.
    shifts = result["K4x10"]["automatic"]["gear_changes"]
    assert [(event["from"], event["to"]) for event in shifts] == [
        (2, 1), (1, 0)
    ], shifts
    assert result["K4x10"]["automatic"]["nodes"] == 21
    # Strong reasoning demonstrably prunes Petersen search more than FAST.
    assert result["Petersen"]["2"]["nodes"] == 10
    assert result["Petersen"]["0"]["nodes"] == 22
    assert result["Petersen"]["automatic"]["nodes"] == 10

    graph = graph_info(10, fixtures()["Petersen"][1])
    with TemporaryDirectory() as folder:
        file = Path(folder) / "frontier.json"
        limited = solve(graph, max_nodes=1, checkpoint=file,
                        adapt_every=1, cut_budget=5000)
        assert limited["verdict"] == "UNKNOWN_RESOURCE_LIMIT"
        assert file.exists() and limited["frontier_size"] > 0
        resumed = solve(graph, resume=file, cut_budget=5000)
        full = solve(graph, cut_budget=5000, adapt_every=1)
        assert resumed["verdict"] == "UNSAT" == full["verdict"]
        assert resumed["stats"]["nodes"] == full["stats"]["nodes"]
    return {"scientific_status": "FINITE_EXACT_GEARBOX_NOT_POLYNOMIAL",
            "fixtures": result,
            "resume_replay": "PASS (Petersen UNKNOWN->UNSAT, same node count)",
            "P_vs_NP": "OPEN",
            "universal_polynomial_runtime": "NOT_PROVED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", choices=sorted(fixtures()), default=None)
    parser.add_argument("--graph", help="JSON object with n and edges")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--gear", type=int, choices=(0, 1, 2), default=2)
    parser.add_argument("--fixed-gear", action="store_true")
    parser.add_argument("--max-nodes", type=int)
    parser.add_argument("--checkpoint", help="write resumable frontier JSON on UNKNOWN")
    parser.add_argument("--resume", help="read saved frontier JSON")
    parser.add_argument("--adapt-every", type=int, default=8)
    parser.add_argument("--cut-budget", type=int, default=20000)
    args = parser.parse_args()
    if args.self_test:
        report = self_test()
    else:
        if args.fixture:
            n, edges, _ = fixtures()[args.fixture]
        elif args.graph:
            inp = json.loads(Path(args.graph).read_text(encoding="utf-8"))
            n, edges = inp["n"], inp["edges"]
        else:
            parser.error("choose --self-test, --fixture, or --graph")
        if args.max_nodes is not None and args.max_nodes < 0:
            parser.error("--max-nodes must be >= 0")
        g = graph_info(n, edges)
        report = {"graph_hash": graph_hash(g), "n": n,
                  **solve(g, max_nodes=args.max_nodes, resume=args.resume,
                          checkpoint=args.checkpoint, start_gear=args.gear,
                          adaptive=not args.fixed_gear,
                          adapt_every=args.adapt_every,
                          cut_budget=args.cut_budget)}
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
