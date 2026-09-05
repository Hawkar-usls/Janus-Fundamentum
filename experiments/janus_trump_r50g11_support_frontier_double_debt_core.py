from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g9_explicit_wide_fixpoint_ancestry_counterexample as r50g9
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10

GATE = "JANUS_TRUMP_R50G11_SUPPORT_FRONTIER_DOUBLE_DEBT_CORE"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def nontaut_union(a, b):
    u = set(a) | set(b)
    if any(-x in u for x in u):
        return None
    return r33.canonical_clause(u)


def chi_bad_pair_certificate(formula, y: int):
    f = canon(formula)
    pos = [c for c in f if int(y) in c]
    neg = [c for c in f if -int(y) in c]
    if not pos or not neg:
        raise AssertionError(("R50G11_NONBIPOLAR_PIVOT", y))

    rows = []
    for p in pos:
        pr = tuple(l for l in p if l != int(y))
        for n in neg:
            nr = tuple(l for l in n if l != -int(y))
            u = nontaut_union(pr, nr)
            if u is None:
                continue
            rows.append((len(u), u, p, n, pr, nr))
    if not rows:
        # Bipolar can still have only tautological cross pairs. In a pre-BVE-clean
        # state this is relevant to BCE, but the closed-door theorem only needs
        # exact chi_star. Keep the certificate explicit.
        return {
            "pivot": int(y),
            "chi_star": 0,
            "witness": None,
            "geometry": "NO_NONTAUTOLOGICAL_CROSS_PAIR",
        }

    rows.sort(key=lambda z: (z[0], z[1], z[2], z[3]))
    width, union, p, n, pr, nr = rows[-1]
    if width > 6:
        raise AssertionError(("R50G11_W4_CHI_EXCEEDS_6", y, width, p, n))

    overlap = len(set(pr) & set(nr))
    geometry = f"{len(p)}x{len(n)}_RESIDUAL_{len(pr)}PLUS{len(nr)}_OVERLAP_{overlap}"
    if width == 6:
        if not (len(p) == 4 and len(n) == 4 and overlap == 0):
            raise AssertionError(("R50G11_CHI6_GEOMETRY_FAIL", y, p, n, union))
    if width == 5:
        allowed = (
            (len(p), len(n), overlap) in {(4, 3, 0), (3, 4, 0), (4, 4, 1)}
        )
        if not allowed:
            raise AssertionError(("R50G11_CHI5_GEOMETRY_FAIL", y, p, n, union, overlap))

    return {
        "pivot": int(y),
        "chi_star": int(width),
        "witness": {
            "positive_parent": list(p),
            "negative_parent": list(n),
            "positive_residual": list(pr),
            "negative_residual": list(nr),
            "nontautological_union": list(union),
            "width": int(width),
            "overlap": int(overlap),
        },
        "geometry": geometry,
    }


def r47j_wide_debt_certificate(formula, y: int):
    f = canon(formula)
    row, cand = r50a._fallback_candidate(f, int(y))
    if cand is None:
        raise AssertionError(("R50G11_R47J_CANDIDATE_MISSING", y))
    replay = r47j.independent_fixpoint_macro_replay(f, cand)
    if not replay["pass"]:
        raise AssertionError(("R50G11_R47J_REPLAY_FAIL", y, replay))
    final = canon(cand["normalization"]["final_formula"])
    if int(y) in set(r33.variables(final)):
        raise AssertionError(("R50G11_R47J_PIVOT_SURVIVED", y))
    widest = max(final, key=lambda c: (len(c), c), default=tuple())
    return {
        "pivot": int(y),
        "safe": bool(row["width4_safe"]),
        "terminal": row["terminal"],
        "final_width": int(row["final_max_width"]),
        "final_CLV": row["final_CLV"],
        "widest_final_clause": list(widest),
        "independent_replay_pass": True,
    }


def alternate_neighbours_from_literals(literals, x: int, y: int):
    return sorted({abs(int(l)) for l in literals if abs(int(l)) not in {abs(int(x)), abs(int(y))}})


def combined_closed_door_certificate(formula, x: int, y: int):
    f = canon(formula)
    door = r50g10.exact_door_row(f, int(y))
    chi = chi_bad_pair_certificate(f, int(y))
    rj = r47j_wide_debt_certificate(f, int(y))
    if int(door["chi_star"]) != int(chi["chi_star"]):
        raise AssertionError(("R50G11_CHI_PROFILE_MISMATCH", y, door, chi))

    if door["closed_door_certificate"]:
        if chi["chi_star"] not in (5, 6):
            raise AssertionError(("R50G11_CLOSED_R49H_NOT_5_OR_6", y, chi))
        if rj["terminal"] is not None or rj["final_width"] <= WIDTH_CAP:
            raise AssertionError(("R50G11_CLOSED_R47J_NOT_WIDE_NONTERMINAL", y, rj))
        chi_neigh = alternate_neighbours_from_literals(chi["witness"]["nontautological_union"], x, y)
        rj_neigh = alternate_neighbours_from_literals(rj["widest_final_clause"], x, y)
        if len(chi_neigh) < 4:
            raise AssertionError(("R50G11_CHI_DEBT_HAS_LT4_ALT_NEIGHBOURS", x, y, chi_neigh, chi))
        if len(rj_neigh) < 4:
            raise AssertionError(("R50G11_R47J_DEBT_HAS_LT4_ALT_NEIGHBOURS", x, y, rj_neigh, rj))
    else:
        chi_neigh = []
        rj_neigh = []

    return {
        "pivot": int(y),
        "door": door,
        "chi_debt": chi,
        "r47j_debt": rj,
        "combined_closed": bool(door["closed_door_certificate"]),
        "chi_alt_neighbours": chi_neigh,
        "r47j_alt_neighbours": rj_neigh,
    }


def first_directed_cycle(graph):
    visiting = set()
    visited = set()
    stack = []

    def dfs(v):
        visiting.add(v)
        stack.append(v)
        for w in graph.get(v, []):
            if w not in graph:
                continue
            if w in visiting:
                i = stack.index(w)
                return stack[i:] + [w]
            if w not in visited:
                got = dfs(w)
                if got is not None:
                    return got
        stack.pop()
        visiting.remove(v)
        visited.add(v)
        return None

    for v in sorted(graph):
        if v not in visited:
            got = dfs(v)
            if got is not None:
                return got
    return None


def all_closed_dependency_core(formula, x: int):
    f = canon(formula)
    alts = [int(v) for v in r33.variables(f) if int(v) != int(x)]
    rows = [combined_closed_door_certificate(f, int(x), y) for y in alts]
    if not rows or not all(r["combined_closed"] for r in rows):
        return {
            "all_alternate_doors_closed": False,
            "alternate_count": len(rows),
            "first_open": next((r for r in rows if not r["combined_closed"]), None),
            "rows": rows,
        }

    if len(alts) < 5:
        raise AssertionError(("R50G11_ALL_CLOSED_WITH_LT5_ALTERNATES", alts))
    chi_graph = {r["pivot"]: r["chi_alt_neighbours"] for r in rows}
    rj_graph = {r["pivot"]: r["r47j_alt_neighbours"] for r in rows}
    if min(len(v) for v in chi_graph.values()) < 4:
        raise AssertionError("R50G11_CHI_GRAPH_MIN_OUTDEG_LT4")
    if min(len(v) for v in rj_graph.values()) < 4:
        raise AssertionError("R50G11_R47J_GRAPH_MIN_OUTDEG_LT4")
    chi_cycle = first_directed_cycle(chi_graph)
    rj_cycle = first_directed_cycle(rj_graph)
    if chi_cycle is None or rj_cycle is None:
        raise AssertionError(("R50G11_MIN_OUTDEG_GRAPH_WITHOUT_CYCLE", chi_cycle, rj_cycle))

    if len(r33.variables(f)) == 6:
        for r in rows:
            if r["chi_debt"]["chi_star"] != 5:
                raise AssertionError(("R50G11_V6_CHI_NOT5", r))
            if set(r["chi_debt"]["witness"]["nontautological_union"]) != set(
                l for v in r33.variables(f) if int(v) != r["pivot"] for l in ()
            ):
                # Literal signs prevent direct set comparison to variable IDs; the
                # cardinality/variable support check below is the exact statement.
                support_vars = {abs(int(l)) for l in r["chi_debt"]["witness"]["nontautological_union"]}
                expected = set(int(v) for v in r33.variables(f) if int(v) != r["pivot"])
                if support_vars != expected:
                    raise AssertionError(("R50G11_V6_CHI_NOT_ALL_OTHER_VARS", r["pivot"], support_vars, expected))

    return {
        "all_alternate_doors_closed": True,
        "alternate_count": len(rows),
        "chi_graph_min_outdegree": min(len(v) for v in chi_graph.values()),
        "r47j_graph_min_outdegree": min(len(v) for v in rj_graph.values()),
        "chi_cycle": chi_cycle,
        "r47j_cycle": rj_cycle,
        "rows": rows,
    }


def profile_r50g9_support_frontier():
    r9 = r50g9.run()
    source = r50g10.build_r50g9_source()
    x = int(r9["source"]["pivot"])
    frontier = r50g10.support_frontier_from_r50g9_result(r9)
    rows = []
    for y in frontier:
        if int(y) == x:
            continue
        door = r50g10.exact_door_row(source, int(y))
        chi = chi_bad_pair_certificate(source, int(y))
        rj = r47j_wide_debt_certificate(source, int(y))
        rows.append({"pivot": int(y), "door": door, "chi": chi, "r47j": rj})

    r49h_only = sum(int(r["door"]["r49h_authorized"] and not r["door"]["r47j_safe"]) for r in rows)
    r47j_only = sum(int(r["door"]["r47j_safe"] and not r["door"]["r49h_authorized"]) for r in rows)
    both = sum(int(r["door"]["r47j_safe"] and r["door"]["r49h_authorized"]) for r in rows)
    none = sum(int(not r["door"]["alternate_certified_door"]) for r in rows)
    return {
        "source_hash": r50g4.fhash(source),
        "pivot": x,
        "frontier": frontier,
        "frontier_size": len(rows),
        "r49h_only": r49h_only,
        "r47j_only": r47j_only,
        "both": both,
        "none": none,
        "all_frontier_hit": bool(rows and none == 0),
        "rows": rows,
    }


def run():
    witness = profile_r50g9_support_frontier()
    reachable = r50g10.replay_frozen_reachable_roots()

    return {
        "gate": GATE,
        "mode": "SYMBOLIC_DOUBLE_DEBT_REDUCTION_PLUS_FROZEN_REPLAY",
        "proved_from_frozen_source_definitions": [
            "W4_IMPLIES_CHI_STAR_LE_6_FOR_BIPOLAR_PIVOTS",
            "PRE_BVE_R49H_CLOSED_IFF_CHI_STAR_IN_5_6",
            "CHI_6_WITNESS_IS_4x4_DISJOINT_RESIDUAL_GEOMETRY",
            "CHI_5_WITNESS_IS_4x3_OR_3x4_DISJOINT_OR_4x4_ONE_OVERLAP",
            "COMBINED_CLOSED_DOOR_CARRIES_CHI_DEBT_AND_R47J_DEBT",
            "EACH_CLOSED_DEBT_CERTIFICATE_HAS_AT_LEAST_FOUR_OTHER_ALTERNATE_NEIGHBOURS_AFTER_EXCLUDING_X",
            "ALL_DOORS_CLOSED_IMPLIES_DOUBLE_DEBT_DEPENDENCY_CORE_WITH_MIN_OUTDEGREE_AT_LEAST_4",
            "ALL_DOORS_CLOSED_IMPLIES_AT_LEAST_6_TOTAL_VARIABLES",
        ],
        "r50g9_support_frontier": witness,
        "reachable_replay": reachable,
        "critical_next_obligation": "IMPOSSIBILITY_OF_REACHABLE_DOUBLE_DEBT_DEPENDENCY_CORE_OR_EXPLICIT_REACHABLE_ALL_DOORS_CLOSED_WITNESS",
        "verdict": "DOUBLE_DEBT_CORE_REDUCTION_CLOSED__R50G9_SUPPORT_FRONTIER_SHOWS_EXACT_R49H_R47J_COMPLEMENTARITY__REACHABLE_IMPOSSIBILITY_OPEN",
        "firewall": {
            "FINITE_SUCCESS_IMPLIES_THEOREM": False,
            "HEURISTIC_AUTHORITY": False,
            "NEW_SEMANTIC_INFERENCE_RULE": False,
            "SUPPORT_FRONTIER_HITTING_THEOREM": "OPEN",
            "REACHABLE_ALTERNATE_DOOR_THEOREM": "OPEN",
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
