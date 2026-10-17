#!/usr/bin/env python3
"""JANUS R5 POLYNOMIAL-BUDGET multi-engine gearbox.

Two INDEPENDENT complete exact solvers on cubic graph 3-edge coloring:
(1) EDGE_DFS: 3-color edge-domain propagation + adaptive gears 0/1/2.
(2) MATCHING_DFS: perfect-matching enumeration with EVEN-2-factor test.

Both frontiers persist. Engine selection is heuristic and provably cannot
erase branches. One invocation visits <= 4*n*n search nodes (unless the
user requests fewer). Thus its total work is polynomial in n, BUT it can
return UNKNOWN_RESOURCE_LIMIT with both frontiers stored. Unbounded
restarts can take exponential aggregate time. P versus NP is OPEN.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory

from r5_adaptive_gearbox_exact_coloring_20261015 import (
    COLORS, default_stats, graph_info, graph_hash, precompute_cuts,
    propagate, strong_failed_literal, choose_edge, verify_coloring,
    verify_holyer_exact_one_witness, gearbox_shift, fixtures
)

FORMAT_VERSION = 1
ENGINES = ("edge_domains", "matching_even_factor")


def polynomial_nodes(n):
    """Hard n^2 cap per invocation, including resume calls."""
    return 4 * n * n


def initial_state(graph):
    return {
        "format": FORMAT_VERSION,
        "graph_hash": graph_hash(graph),
        "edge_frontier": [[7] * len(graph["edges"])],
        "matching_frontier": [[0, []]],
        "edge_stats": default_stats(),
        "matching_stats": {
            "nodes": 0, "dead": 0, "branches": 0, "tested_2factors": 0,
            "odd_cycle_rejections": 0
        },
        "gear": 2,
        "edge_last": {
            "nodes": 0, "failed_literals": 0, "probes": 0,
            "equal_checks": 0, "dead": 0
        },
        "selector": {
            "quanta": 0,
            "last_engine": None,
            "last_seen_quantum": {e: -1 for e in ENGINES},
            "scores": {e: 0.0 for e in ENGINES},
            "switch_log": [],
            "work_progress_log": [],
            "engine_node_histogram": {e: 0 for e in ENGINES}
        },
        "cut_limit": min(256, graph["n"] * graph["n"]),
        "probe_edges": 2,
        "gear_window": 8,
        "work_units": {
            "vertex_factor_checks": 0,
            "pair_checks": 0,
            "failed_literal_probes": 0,
            "matching_candidates_checked": 0,
            "matching_cycles_checked": 0
        },
    }


def validate_resume(state, graph):
    if (state.get("format") != FORMAT_VERSION or
            state.get("graph_hash") != graph_hash(graph)):
        raise ValueError("checkpoint incompatible with input graph/version")
    m, n = len(graph["edges"]), graph["n"]
    if not isinstance(state["edge_frontier"], list) or not isinstance(
            state["matching_frontier"], list):
        raise ValueError("invalid checkpoint frontiers")
    # DFS stacks have polynomial size because branching depth <= m.
    # Reject malicious/unbounded JSON frontiers rather than assuming
    # preloaded untrusted checkpoint can satisfy a polynomial envelope.
    if len(state["edge_frontier"]) > 3 * m + 1:
        raise ValueError("edge frontier exceeds stack upper bound")
    if len(state["matching_frontier"]) > 3 * n + 1:
        raise ValueError("matching frontier exceeds stack upper bound")
    for domains in state["edge_frontier"]:
        if len(domains) != m or any(d not in (1, 2, 3, 4, 5, 6, 7)
                                   for d in domains):
            raise ValueError("invalid edge domains")
    for used, chosen in state["matching_frontier"]:
        if used < 0 or used >= 1 << n or len(chosen) > n // 2:
            raise ValueError("invalid matching state")
        expected = 0
        for i in chosen:
            if not 0 <= i < m:
                raise ValueError("invalid matching edge")
            u, v = graph["edges"][i]
            pair = (1 << u) | (1 << v)
            if expected & pair:
                raise ValueError("nonmatching partial perfect matching")
            expected |= pair
        if expected != used:
            raise ValueError("matching used mask doesn't fit chosen edges")
    if state["gear"] not in (0, 1, 2):
        raise ValueError("invalid gear")
    return state


def coloring_from_matching(graph, chosen):
    """Independent completion: complement 2-factor must have even cycles."""
    n, m = graph["n"], len(graph["edges"])
    chosen = set(chosen)
    color = [None] * m
    for e in chosen:
        color[e] = 0
    for group in graph["incidence"]:
        if sum(e in chosen for e in group) != 1:
            raise AssertionError("incomplete matching at leaf")
    # Complement edges form a 2-factor. Adjacent residual edges must
    # alternate colors 1 and 2. BFS over edge adjacency tests bipartity
    # of this line-cycle graph, including odd cycles.
    for seed in range(m):
        if color[seed] is not None:
            continue
        color[seed] = 1
        queue = [seed]
        for e in queue:
            u, v = graph["edges"][e]
            for vertex in (u, v):
                for neighbor in graph["incidence"][vertex]:
                    if neighbor == e or neighbor in chosen:
                        continue
                    required = 3 - color[e]
                    if color[neighbor] is None:
                        color[neighbor] = required
                        queue.append(neighbor)
                    elif color[neighbor] != required:
                        return None
    domains = tuple(COLORS[c] for c in color)
    if not verify_coloring(graph, domains):
        raise AssertionError("completion returned invalid 3-edge-coloring")
    return color


def matching_step(state, graph):
    stack = state["matching_frontier"]
    stats = state["matching_stats"]
    used, chosen = stack.pop()
    stats["nodes"] += 1
    n, all_mask = graph["n"], (1 << graph["n"]) - 1
    if used == all_mask:
        stats["tested_2factors"] += 1
        outcome = coloring_from_matching(graph, chosen)
        state["work_units"]["matching_cycles_checked"] += n
        if outcome is None:
            stats["dead"] += 1
            stats["odd_cycle_rejections"] += 1
            return None
        return outcome

    edges = graph["edges"]
    best = None
    for v in range(n):
        if (used >> v) & 1:
            continue
        candidates = []
        for e in graph["incidence"][v]:
            state["work_units"]["matching_candidates_checked"] += 1
            a, b = edges[e]
            other = b if a == v else a
            if not ((used >> other) & 1):
                candidates.append((e, other))
        item = (len(candidates), v, tuple(candidates))
        if best is None or item < best:
            best = item
        if len(candidates) == 0:
            break

    count, pivot, choices = best
    if count == 0:
        stats["dead"] += 1
        return None

    # Every completion of the partial matching chooses one of these
    # edges incident to the selected unmatched vertex. Children form an
    # EXACT partition of the matching completion search space.
    for edge, other in reversed(choices):
        child_mask = used | (1 << pivot) | (1 << other)
        stack.append([child_mask, chosen + [edge]])
        stats["branches"] += 1
    return None


def edge_step(state, graph, cuts):
    stack = state["edge_frontier"]
    stats = state["edge_stats"]
    current = tuple(stack.pop())
    stats["nodes"] += 1
    gear = state["gear"]
    stats["gear_node_histogram"][gear] += 1
    prior = sum(d.bit_count() for d in current)
    filtered, _ = propagate(current, graph["incidence"], cuts, gear, stats)
    if filtered is not None and gear == 2:
        filtered, _ = strong_failed_literal(
            filtered, graph["incidence"], cuts, stats,
            probe_edges=state["probe_edges"]
        )
    if filtered is None:
        stats["dead"] += 1
    else:
        stats["forced_bits"] += prior - sum(d.bit_count() for d in filtered)
        if all(d in COLORS for d in filtered):
            if not verify_coloring(graph, filtered):
                raise AssertionError("invalid candidate color witness")
            return [COLORS.index(d) for d in filtered]
        edge = choose_edge(filtered, graph)
        for color in reversed(COLORS):
            if filtered[edge] & color:
                child = list(filtered)
                child[edge] = color
                stack.append(child)
                stats["branches"] += 1
    if stats["nodes"] % state["gear_window"] == 0:
        state["gear"] = gearbox_shift(
            state["gear"], stats, state["edge_last"], True,
            state["gear_window"]
        )
        # Keep checkpoint/history size polynomial across arbitrarily
        # many resumed invocations. Full aggregate counts stay in ints.
        stats["gear_changes"] = stats["gear_changes"][-64:]
        state["edge_last"] = {
            key: stats[key] for key in
            ("nodes", "failed_literals", "probes", "equal_checks", "dead")
        }
    return None


def frontier_mass(state, graph, name):
    """VALID upper bound on raw remaining assignments in each engine.

    These two masses are NOT comparable across engines: colorings are
    assigned by edge values, while matching DFS assigns perfect matchings.
    Rates are normalized within each engine before scheduling.
    """
    if name == "edge_domains":
        return sum(
            math.prod(int(d).bit_count() for d in row)
            for row in state["edge_frontier"]
        )
    n = graph["n"]
    return sum(3 ** ((n - int(used).bit_count()) // 2)
               for used, chosen in state["matching_frontier"])


def choose_engine(state):
    selector = state["selector"]
    available = [e for e in ENGINES if state[
        "edge_frontier" if e == "edge_domains" else "matching_frontier"
    ]]
    if not available:
        raise AssertionError("empty engine selection")
    if len(available) == 1:
        return available[0]
    # Mandatory first sample of both engines. Never confuse the
    # normalized upper-bound reduction with a proof of optimum speed.
    for e in ENGINES:
        if selector["last_seen_quantum"][e] == -1:
            return e
    # Fairness: at least one quantum per engine every 3 scheduled quanta.
    for e in ENGINES:
        if selector["quanta"] - selector["last_seen_quantum"][e] >= 3:
            return e
    return max(available, key=lambda e: (
        selector["scores"][e],
        -selector["last_seen_quantum"][e]
    ))


def run(graph, max_nodes=None, checkpoint=None, resume=None,
        quantum=None):
    n = graph["n"]
    state = (initial_state(graph) if resume is None else
             validate_resume(
                 json.loads(Path(resume).read_text(encoding="utf-8")),
                 graph
             ))
    cap = polynomial_nodes(n)
    if max_nodes is None:
        fuel = cap
    else:
        if not isinstance(max_nodes, int) or max_nodes < 0:
            raise ValueError("max_nodes must be a nonnegative integer")
        fuel = min(max_nodes, cap)
    # Every quantum is polynomial bounded, with at least one node.
    slice_size = max(1, min(8, n // 4)) if quantum is None else quantum
    if not isinstance(slice_size, int) or slice_size < 1:
        raise ValueError("quantum must be positive integer")
    slice_size = min(slice_size, 8)
    cuts = precompute_cuts(graph, max_triples=state["cut_limit"])

    if cuts["bridges"]:
        outcome = finished("UNSAT", graph, state, 0, cap)
        outcome["reason"] = "certified cubic graph bridge"
        outcome["bridge_edges"] = [
            graph["edges"][i] for i in cuts["bridges"]
        ]
        return outcome

    visited = 0
    while visited < fuel:
        # Either complete exact engine independently proves UNSAT.
        if not state["edge_frontier"] or not state["matching_frontier"]:
            return finished("UNSAT", graph, state, visited, cap)
        name = choose_engine(state)
        stat_name = ("edge_stats" if name == "edge_domains"
                     else "matching_stats")
        engine_stats = state[stat_name]
        selector = state["selector"]
        before_mass = frontier_mass(state, graph, name)
        before_stats = (dict(engine_stats))
        chunk = min(slice_size, fuel - visited)
        found = None
        for _ in range(chunk):
            if not state["edge_frontier"] or not state["matching_frontier"]:
                break
            if name == "edge_domains":
                found = edge_step(state, graph, cuts)
            else:
                found = matching_step(state, graph)
            visited += 1
            if found is not None:
                domains = tuple(COLORS[c] for c in found)
                if (not verify_coloring(graph, domains) or
                        not verify_holyer_exact_one_witness(graph, domains)):
                    raise AssertionError("independent SAT witness rejected")
                out = finished("SAT", graph, state, visited, cap)
                out["found_by"] = name
                out["edge_colors"] = found
                return out
        after_mass = frontier_mass(state, graph, name)
        if after_mass > before_mass:
            raise AssertionError("frontier raw-assignment upper bound increased")
        delta_nodes = engine_stats["nodes"] - before_stats["nodes"]
        # Strong pruning score: normalized log decrease of a verified
        # per-engine upper bound; NOT an estimate of unexplored SAT count.
        progress = max(0.0, math.log2(1 + before_mass) -
                       math.log2(1 + after_mass))
        if name == "edge_domains":
            state["work_units"]["vertex_factor_checks"] += (
                engine_stats["triple_checks"] -
                before_stats["triple_checks"]
            )
            state["work_units"]["pair_checks"] += (
                engine_stats["equal_checks"] -
                before_stats["equal_checks"]
            )
            state["work_units"]["failed_literal_probes"] += (
                engine_stats["probes"] - before_stats["probes"]
            )
            work = (engine_stats["triple_checks"] -
                    before_stats["triple_checks"] +
                    engine_stats["equal_checks"] -
                    before_stats["equal_checks"] +
                    6 * (engine_stats["probes"] - before_stats["probes"]))
        else:
            work = (engine_stats["nodes"] - before_stats["nodes"] +
                    3 * (engine_stats["branches"] - before_stats["branches"]))
        density = progress / max(1, work)
        selector["scores"][name] = round(
            0.5 * selector["scores"][name] + 0.5 * density, 12
        )
        # A compact history of actual decrease in an upper bound on raw
        # candidate completions (not a count of viable SAT witnesses).
        selector["work_progress_log"].append({
            "engine": name,
            "at_total_node": (
                state["edge_stats"]["nodes"] +
                state["matching_stats"]["nodes"]
            ),
            "before_bound_log2": round(math.log2(1+before_mass), 4),
            "after_bound_log2": round(math.log2(1+after_mass), 4),
            "log2_reduction": round(progress, 4),
            "work_proxy": work,
            "pruning_per_work_proxy": round(density, 9)
        })
        selector["work_progress_log"] = (
            selector["work_progress_log"][-64:]
        )
        old = selector["last_engine"]
        if name != old:
            selector["switch_log"].append({
                "after_total_node": (
                    state["edge_stats"]["nodes"] +
                    state["matching_stats"]["nodes"] - delta_nodes
                ),
                "from": old, "to": name,
                "reason": "sample/fairness/measured bound reduction"
            })
        selector["switch_log"] = selector["switch_log"][-64:]
        selector["last_engine"] = name
        selector["last_seen_quantum"][name] = selector["quanta"]
        selector["quanta"] += 1
        selector["engine_node_histogram"][name] += delta_nodes

    if not state["edge_frontier"] or not state["matching_frontier"]:
        return finished("UNSAT", graph, state, visited, cap)

    if checkpoint is not None:
        Path(checkpoint).write_text(
            json.dumps(state, sort_keys=True, separators=(",", ":")),
            encoding="utf-8"
        )
    out = finished("UNKNOWN_RESOURCE_LIMIT", graph, state, visited, cap)
    out["reason"] = "polynomial per-invocation node budget exhausted"
    out["checkpoint_written"] = checkpoint
    return out


def finished(verdict, graph, state, nodes, cap):
    return {
        "verdict": verdict,
        "graph_hash": graph_hash(graph),
        "vertices": graph["n"],
        "polynomial_visit_cap": cap,
        "visited_this_call": nodes,
        "total_nodes": (
            state["edge_stats"]["nodes"] +
            state["matching_stats"]["nodes"]
        ),
        "edge_stats": state["edge_stats"],
        "matching_stats": state["matching_stats"],
        "selector": state["selector"],
        "frontier_sizes": {
            "edge_domains": len(state["edge_frontier"]),
            "matching_even_factor": len(state["matching_frontier"])
        },
        "work_units": state["work_units"],
        "remaining_raw_upper_bound_log2": {
            e: round(math.log2(1+frontier_mass(state, graph, e)), 4)
            for e in ENGINES
        }
    }


def self_test():
    result = {}
    for name, (n, edges, sat) in fixtures().items():
        graph = graph_info(n, edges)
        out = run(graph)
        assert (out["verdict"] == "SAT") == sat, (name, out)
        result[name] = {
            "verdict": out["verdict"],
            "found_by": out.get("found_by"),
            "visited_this_call": out["visited_this_call"],
            "multi_engine_switches": len(out["selector"]["switch_log"]),
            "edge_nodes": out["edge_stats"]["nodes"],
            "matching_nodes": out["matching_stats"]["nodes"]
        }
    # Multiple sessions must never misclassify unfinished enumeration.
    p = fixtures()["Petersen"]
    graph = graph_info(p[0], p[1])
    with TemporaryDirectory() as tmp:
        checkpoint = str(Path(tmp) / "multi.json")
        first = run(graph, max_nodes=1, checkpoint=checkpoint, quantum=1)
        assert first["verdict"] == "UNKNOWN_RESOURCE_LIMIT"
        assert Path(checkpoint).exists()
        second = run(graph, resume=checkpoint, max_nodes=1,
                     checkpoint=checkpoint, quantum=1)
        assert second["verdict"] in ("UNKNOWN_RESOURCE_LIMIT", "UNSAT")
        final = run(graph, resume=checkpoint, quantum=1)
        assert final["verdict"] == "UNSAT"
        # Budget-resume must retain BOTH frontiers and sample both
        # independent complete engines, not silently restart either.
        assert final["edge_stats"]["nodes"] > 0
        assert final["matching_stats"]["nodes"] > 0
        assert len(final["selector"]["switch_log"]) >= 2
        assert final["total_nodes"] >= first["total_nodes"]
        assert final["visited_this_call"] <= polynomial_nodes(graph["n"])
        # Hash check must prevent loading the wrong graph state.
        k4 = fixtures()["K4"]
        try:
            run(graph_info(k4[0], k4[1]), resume=checkpoint)
        except ValueError:
            pass
        else:
            raise AssertionError("checkpoint graph hash was not checked")
        result["resume"] = {
            "first": first["verdict"],
            "second": second["verdict"],
            "terminal": final["verdict"],
            "hash_guard": "PASS"
        }
    # Each per-engine search-mass upper bound is monotone under its
    # branching + propagation, verified for every scheduled quantum.
    assert result["Petersen"]["edge_nodes"] > 0
    assert result["Petersen"]["matching_nodes"] > 0
    assert result["K4x10"]["found_by"] == "matching_even_factor"
    # Polynomial single-call cap must not be bypassable by CLI requests.
    tiny = graph_info(10, fixtures()["Petersen"][1])
    assert run(tiny, max_nodes=0)["verdict"] == "UNKNOWN_RESOURCE_LIMIT"
    assert run(tiny, max_nodes=10**100)["visited_this_call"] <= (
        polynomial_nodes(tiny["n"])
    )
    return {
        "scientific_status": "POLYNOMIAL_BUDGETED_EXACT_MULTIENGINE_WITH_UNKNOWN",
        "fixtures": result,
        "universal_polynomial_decision": "NOT_PROVED",
        "P_vs_NP": "OPEN"
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", choices=sorted(fixtures()))
    parser.add_argument("--graph", help="JSON with n and edges")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--max-nodes", type=int,
                        help="requested work allowance, capped at 4*n*n")
    parser.add_argument("--quantum", type=int,
                        help="nodes per engine session (capped at 8)")
    parser.add_argument("--checkpoint", help="path to store UNKNOWN frontier")
    parser.add_argument("--resume", help="path of prior UNKNOWN frontier")
    opts = parser.parse_args()
    if opts.self_test:
        report = self_test()
    else:
        if opts.fixture:
            n, edges, _ = fixtures()[opts.fixture]
        elif opts.graph:
            payload = json.loads(
                Path(opts.graph).read_text(encoding="utf-8"))
            n, edges = payload["n"], payload["edges"]
        else:
            parser.error("use --self-test, --fixture, or --graph")
        report = run(graph_info(n, edges), max_nodes=opts.max_nodes,
                     checkpoint=opts.checkpoint, resume=opts.resume,
                     quantum=opts.quantum)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
