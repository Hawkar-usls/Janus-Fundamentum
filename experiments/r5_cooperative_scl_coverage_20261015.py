#!/usr/bin/env python3
"""R5 Cooperative Universal Progress: exact SCL-native proof-carrying prototype.

EXPERIMENT, NOT P=NP: finite exact branch solver for legal square+cubic+
linear positive 1-in-3-SAT. Experts exchange only checkable information:
  WEIGHT: exact global cardinality n/3, local forced bits and contradictions
  EXACT_ONE: deterministic unit consequences of integer clause equals 1
  GF2: affine parity solution space, forced coordinates and exact rank bound
  SMALL_KERNEL: bounded exhaustive affine basis search (dimension <= 8)
  BRANCH: exhaustive split if no expert can finish the current cube

The shared DFS frontier consists of disjoint Boolean cubes. Each carries
a certified bound U=min(number with exact weight, number satisfying GF2).
The aggregate sum is a sound integer upper bound on the union of cubes
intersected with BOTH necessary conditions. Every solution remains inside.
A small-kernel leaf proves SAT or UNSAT by verifying every parity solution.
A per-run finite node budget yields UNKNOWN, not UNSAT. No polynomial
total runtime or universal cooperative progress bound is claimed.

No external dependencies; Python 3.11+. Tests run n=7,9,12 and Holyer K4,
and deliberately bounded Petersen Holyer n=45 (no fabricated UNSAT).
"""
import argparse
import hashlib
from itertools import combinations, product
import json
from math import comb
from pathlib import Path


def validate_scl(rows):
    n = len(rows)
    if n == 0 or any(len(row) != 3 or len(set(row)) != 3
                     for row in rows):
        raise ValueError("each of n rows must have 3 distinct variables")
    if any(not all(isinstance(v, int) and 0 <= v < n for v in row)
           for row in rows):
        raise ValueError("variables must be indices in [0,n)")
    canonical = tuple(sorted(tuple(sorted(row)) for row in rows))
    if len(set(canonical)) != n:
        raise ValueError("duplicate rows violate linearity")
    count = [0] * n
    rowsets = []
    for row in canonical:
        bitset = sum(1 << v for v in row)
        rowsets.append(bitset)
        for v in row:
            count[v] += 1
    if count != [3] * n:
        raise ValueError("each variable must occur exactly three times")
    for i in range(n):
        for j in range(i):
            if (rowsets[i] & rowsets[j]).bit_count() > 1:
                raise ValueError("rows share two or more variables")
    return canonical


def fingerprint(rows):
    return hashlib.sha256(json.dumps(
        rows, separators=(",", ":")
    ).encode()).hexdigest()


def literal_weight_bound(n, zeros, ones):
    free = n - (zeros | ones).bit_count()
    needed = n // 3 - ones.bit_count()
    return comb(free, needed) if 0 <= needed <= free else 0


def gf2_affine(rows, zeros, ones):
    """Exact Gaussian elimination on fixed-variable parity equations.

    Returns (particular, basis, dimension) or None if contradictory.
    All equations are XOR of three variables equal to 1.
    """
    fixed = zeros | ones
    echelon = {}
    for row in rows:
        mask = sum(1 << v for v in row) & ~fixed
        rhs = 1 ^ ((sum(1 << v for v in row) & ones).bit_count() & 1)
        while mask:
            pivot = mask.bit_length() - 1
            if pivot in echelon:
                other, r = echelon[pivot]
                mask ^= other
                rhs ^= r
            else:
                echelon[pivot] = (mask, rhs)
                break
        else:
            if rhs:
                return None
    free = [v for v in range(len(rows)) if not (fixed >> v) & 1
            and v not in echelon]

    def reconstruct(free_seed):
        value = ones | free_seed
        # Echelon pivots are their row's highest-set bits; remaining bits
        # have LOWER indices. Ascending order is an exact back substitution.
        for pivot in sorted(echelon):
            mask, rhs = echelon[pivot]
            bit = rhs ^ (((mask & ~(1 << pivot)) & value).bit_count() & 1)
            if bit:
                value |= 1 << pivot
        return value

    part = reconstruct(0)
    basis = tuple(reconstruct(1 << v) ^ part for v in free)
    assert all((part & zeros) == 0 and ((part & ones) == ones)
               for _ in (0,))
    return part, basis, len(free)


def bound_cube(rows, cube):
    zeros, ones = cube
    n = len(rows)
    weight = literal_weight_bound(n, zeros, ones)
    if not weight:
        return 0
    affine = gf2_affine(rows, zeros, ones)
    if affine is None:
        return 0
    return min(weight, 1 << affine[2])


def mass(rows, frontier):
    return sum(bound_cube(rows, cube) for cube in frontier)


def valid_witness(rows, bits):
    n = len(rows)
    return ((bits.bit_count() == n // 3)
            and all(sum((bits >> v) & 1 for v in row) == 1
                    for row in rows))


def local_consequences(rows, cube):
    """All rule consequences are checked from one immutable snapshot.

    Returns (status, newcube, premises). No heuristic deletion allowed.
    """
    zero, one = cube
    n = len(rows)
    zadd = oadd = 0
    premises = []
    fixed = zero | one
    for row in rows:
        ones = [v for v in row if (one >> v) & 1]
        free = [v for v in row if not ((fixed >> v) & 1)]
        if len(ones) > 1 or (not ones and not free):
            return "CONFLICT", cube, [("clause_conflict", list(row))]
        if ones:
            for v in free:
                zadd |= 1 << v
                premises.append(("one_forces_zero", list(row), v))
        elif len(free) == 1:
            oadd |= 1 << free[0]
            premises.append(("two_zeros_force_one", list(row), free[0]))
    need = n // 3 - one.bit_count()
    remaining = [v for v in range(n) if not (fixed >> v) & 1]
    if need < 0 or need > len(remaining):
        return "CONFLICT", cube, [("weight_conflict", need)]
    if need == 0:
        for v in remaining:
            zadd |= 1 << v
            premises.append(("full_weight_forces_zero", v))
    elif need == len(remaining):
        for v in remaining:
            oadd |= 1 << v
            premises.append(("full_weight_forces_one", v))
    if (zero | zadd) & (one | oadd):
        # Simultaneously certified but contradictory implications.
        return "CONFLICT", cube, premises + [("forced_conflict",)]
    new = (zero | zadd, one | oadd)
    return ("FORCED" if new != cube else "STABLE"), new, premises


def gf2_consequences(rows, cube):
    zeros, ones = cube
    affine = gf2_affine(rows, zeros, ones)
    if affine is None:
        return "CONFLICT", cube, -1
    part, basis, d = affine
    variable_mask = ((1 << len(rows)) - 1) & ~(zeros | ones)
    varying = 0
    for b in basis:
        varying |= b
    forced = variable_mask & ~varying
    add_one = forced & part
    add_zero = forced & ~part
    updated = (zeros | add_zero, ones | add_one)
    if updated[0] & updated[1]:
        raise AssertionError("bad affine forced deductions")
    return ("FORCED" if updated != cube else "STABLE"), updated, d


def bounded_affine_expert(rows, cube, max_dimension=8):
    aff = gf2_affine(rows, *cube)
    if aff is None:
        return "UNSAT_CUBE", None, 0
    particular, basis, d = aff
    if d > max_dimension:
        return "DECLINE", None, d
    checked = 0
    for pattern in range(1 << d):
        x = particular
        for j, vec in enumerate(basis):
            if pattern >> j & 1:
                x ^= vec
        checked += 1
        if valid_witness(rows, x):
            return "SAT", x, checked
    return "UNSAT_CUBE", None, checked


def verify_progress(rows, source_cube, replacement, proof):
    """Independent, polynomial-time verifier for one expert exchange.

    'proof' is a tiny opcode and optional branch variable. The verifier
    RECOMPUTES source consequences; it never trusts claimed bound changes.
    Returned tuple: (verified, U_before, U_after, threshold_met).
    For SMALL_KERNEL_UNSAT the fixed dimension cap is <=8.
    """
    kind = proof["kind"]
    u0 = bound_cube(rows, source_cube)
    if kind == "EXACT_ONE":
        status, child, _ = local_consequences(rows, source_cube)
        accepted = status == "FORCED" and replacement == [child]
    elif kind == "GF2":
        status, child, _ = gf2_consequences(rows, source_cube)
        accepted = status == "FORCED" and replacement == [child]
    elif kind == "BRANCH":
        v = proof.get("variable")
        fixed = source_cube[0] | source_cube[1]
        accepted = (
            isinstance(v, int) and 0 <= v < len(rows)
            and not (fixed >> v) & 1
            and replacement == [
                (source_cube[0] | (1 << v), source_cube[1]),
                (source_cube[0], source_cube[1] | (1 << v))
            ]
        )
    elif kind == "BOUND_ZERO":
        accepted = u0 == 0 and replacement == []
    elif kind == "SMALL_KERNEL_UNSAT":
        accepted = (replacement == [] and
                    bounded_affine_expert(rows, source_cube, 8)[0]
                    == "UNSAT_CUBE")
    elif kind == "EXACT_ONE_CONFLICT":
        accepted = (replacement == [] and
                    local_consequences(rows, source_cube)[0] == "CONFLICT")
    elif kind == "GF2_CONFLICT":
        accepted = (replacement == [] and
                    gf2_consequences(rows, source_cube)[0] == "CONFLICT")
    else:
        accepted = False
    if not accepted:
        return False, u0, None, False
    u1 = sum(bound_cube(rows, child) for child in replacement)
    if u1 > u0:
        return False, u0, u1, False
    power = proof.get("progress_power", 1)
    if not isinstance(power, int) or power < 0 or power > 8:
        return False, u0, u1, False
    n = len(rows)
    significant = u1 * (n ** power) <= (n ** power - 1) * u0
    return True, u0, u1, significant


def choose_branch(rows, cube):
    fixed = cube[0] | cube[1]
    # Degree is uniformly 3 in source SCL. Pick variable closest to
    # the most constrained exact-one rows, with deterministic tiebreak.
    rank = []
    for v in range(len(rows)):
        if fixed >> v & 1:
            continue
        row_pressure = sum(
            sum((fixed >> w) & 1 for w in row)
            for row in rows if v in row
        )
        rank.append((-row_pressure, v))
    return min(rank)[1]


def solve(rows, node_budget=200, kernel_limit=8,
          checkpoint=None, resume=None, progress_power=1):
    rows = validate_scl(rows)
    n = len(rows)
    if node_budget < 0 or kernel_limit < 0 or progress_power < 0:
        raise ValueError("budgets and power must be nonnegative")
    limit = min(node_budget, 4*n*n)
    if resume:
        source = json.loads(Path(resume).read_text(encoding="utf-8"))
        if source["version"] != 1 or source["fingerprint"] != fingerprint(rows):
            raise ValueError("checkpoint mismatch")
        stack = [tuple(map(int, a)) for a in source["frontier"]]
        visited = int(source["total_visited"])
        if len(stack) > n + 1:
            raise ValueError("invalid exponential frontier in checkpoint")
    else:
        stack, visited = [(0, 0)], 0
    initial_bound = mass(rows, stack) if n % 3 == 0 else 0
    report = {
        "n": n,
        "weight_target": (n//3 if n % 3 == 0 else None),
        "fingerprint": fingerprint(rows),
        "initial_frontier_bound": initial_bound,
        "initial_weight_candidates": (
            comb(n, n//3) if n % 3 == 0 else 0
        ),
        "initial_GF2_candidates": (
            (1 << gf2_affine(rows, 0, 0)[2])
            if gf2_affine(rows, 0, 0) is not None else 0
        ),
        "work_nodes_this_call": 0,
        "total_previous_visited": visited,
        "proof_step_log": [],
        "cooperative_stalls": 0,
        "certified_shrinks": 0,
        "branch_steps": 0,
        "candidate_proofs_verified": 0,
        "max_dimension_enumerated": kernel_limit,
    }

    if n % 3:
        report.update(verdict="UNSAT", reason="3*|x|=n impossible")
        return report

    def log(event):
        report["proof_step_log"].append(event)
        report["proof_step_log"] = report["proof_step_log"][-32:]

    def commit_rewrite(old, new, name, info):
        # Independent deterministic rechecks on every accepted update.
        if name == "EXACT_ONE":
            kind, expected, premises = local_consequences(rows, old)
            assert kind == "FORCED" and expected == new
        elif name == "GF2":
            kind, expected, d = gf2_consequences(rows, old)
            assert kind == "FORCED" and expected == new
        else:
            raise AssertionError("unauthorized update")
        before = bound_cube(rows, old)
        after = bound_cube(rows, new)
        assert after <= before
        ok, certified_from, certified_to, significant = verify_progress(
            rows, old, [new], {"kind": name,
                              "progress_power": progress_power})
        assert ok and certified_from == before and certified_to == after
        if significant:
            report["certified_shrinks"] += 1
        stack.append(new)
        log({"expert": name, "before": list(old), "after": list(new),
             "U_before": before, "U_after": after, "proof": info})

    processed = 0
    while stack and processed < limit:
        cube = stack.pop()
        visited += 1
        processed += 1
        report["work_nodes_this_call"] += 1
        u = bound_cube(rows, cube)
        if u == 0:
            log({"expert": "BOUND", "cube": list(cube),
                 "proof": "recomputed weight/GF2 contradiction", "U": 0})
            continue
        kind, after, premises = local_consequences(rows, cube)
        if kind == "CONFLICT":
            log({"expert": "EXACT_ONE", "cube": list(cube),
                 "proof": premises, "U_after": 0})
            continue
        if kind == "FORCED":
            commit_rewrite(cube, after, "EXACT_ONE", premises)
            continue
        kind, after, d = gf2_consequences(rows, cube)
        if kind == "CONFLICT":
            log({"expert": "GF2", "cube": list(cube),
                 "proof": "recomputed Gaussian elimination", "U_after": 0})
            continue
        if kind == "FORCED":
            commit_rewrite(cube, after, "GF2", {"dimension": d})
            continue
        kind, solution, checked = bounded_affine_expert(
            rows, cube, kernel_limit
        )
        if kind == "SAT":
            assert valid_witness(rows, solution)
            report["candidate_proofs_verified"] += checked
            report.update(verdict="SAT", witness_bits=solution,
                          witness=[i for i in range(n) if solution >> i & 1],
                          found_by="SMALL_KERNEL_GAUSS_WEIGHT_EXACT_ONE")
            log({"expert": "SMALL_KERNEL", "dimension": d,
                 "checked": checked, "proof": "all candidate parity words replayable"})
            break
        if kind == "UNSAT_CUBE":
            # Enumeration ALL affine solutions is independently
            # reproducible in at most 2^kernel_limit attempts.
            assert bounded_affine_expert(rows, cube, kernel_limit)[0] == "UNSAT_CUBE"
            report["candidate_proofs_verified"] += checked
            log({"expert": "SMALL_KERNEL", "cube": list(cube),
                 "proof": "all affine words fail Exact-One", "checked": checked})
            continue

        report["cooperative_stalls"] += 1
        v = choose_branch(rows, cube)
        low = (cube[0] | (1 << v), cube[1])
        high = (cube[0], cube[1] | (1 << v))
        assert not low[0] & low[1] and not high[0] & high[1]
        b = bound_cube(rows, low) + bound_cube(rows, high)
        assert b <= u, "partition min-bound monotonicity violation"
        ok, checked_before, checked_after, significant = verify_progress(
            rows, cube, [low, high],
            {"kind": "BRANCH", "variable": v,
             "progress_power": progress_power})
        assert ok and checked_before == u and checked_after == b
        if significant:
            report["certified_shrinks"] += 1
        # Reverse push order: process 0 first. Keeping BOTH alternatives
        # guarantees completeness even after expert declines.
        stack.extend((high, low))
        report["branch_steps"] += 1
        log({"expert": "BRANCH", "cube": list(cube), "variable": v,
             "children": [list(low), list(high)], "U_before": u,
             "U_after": b, "stall": True,
             "proof": "complete disjoint Boolean partition"})

    if "verdict" not in report:
        report["verdict"] = "UNKNOWN_RESOURCE_LIMIT" if stack else "UNSAT"
    report["total_visited"] = visited
    report["frontier_count"] = len(stack)
    report["frontier_bound"] = mass(rows, stack)
    if report["verdict"] == "UNKNOWN_RESOURCE_LIMIT" and checkpoint:
        Path(checkpoint).write_text(
            json.dumps({
                "version": 1,
                "fingerprint": fingerprint(rows),
                "frontier": stack,
                "total_visited": visited
            }, sort_keys=True),
            encoding="utf-8"
        )
        report["checkpoint_written"] = checkpoint
    return report


def affine_plane9():
    # 3 parallel line families: x=c, y=c, y-x=c over F3^2.
    pts = list(product(range(3), repeat=2))
    lines = []
    for c in range(3):
        lines.append(tuple(i for i, (x, y) in enumerate(pts) if x == c))
    for c in range(3):
        lines.append(tuple(i for i, (x, y) in enumerate(pts) if y == c))
    for c in range(3):
        lines.append(tuple(i for i, (x, y) in enumerate(pts)
                           if (y-x) % 3 == c))
    return validate_scl(lines)


def fano7():
    return validate_scl(
        [tuple(sorted(((i+j) % 7 for j in (0, 1, 3))))
         for i in range(7)])


def unsat12():
    return validate_scl([
        (0,6,7),(1,5,8),(0,2,10),(3,5,10),
        (0,4,8),(2,4,5),(3,4,6),(1,7,11),
        (3,8,11),(1,2,9),(7,9,10),(6,9,11)])


def holyer(nvertices, graph_edges):
    edges = sorted(tuple(sorted(e)) for e in graph_edges)
    m = len(edges)
    inc = [[] for _ in range(nvertices)]
    for i, (u,v) in enumerate(edges):
        inc[u].append(i)
        inc[v].append(i)
    assert all(len(x)==3 for x in inc)
    rows = [tuple(3*i+c for c in range(3)) for i in range(m)]
    rows += [tuple(3*i+c for i in inc[v])
             for v in range(nvertices) for c in range(3)]
    return validate_scl(rows)


def fixtures():
    from r5_adaptive_gearbox_exact_coloring_20261015 import fixtures as graph_fixtures
    return {
        "AffinePlane9_SAT": affine_plane9(),
        "Fano7_UNSAT_weight": fano7(),
        "Regular12_UNSAT": unsat12(),
        "HolyerK4_SAT": holyer(*graph_fixtures()["K4"][:2]),
        "HolyerPetersen_UNSAT": holyer(*graph_fixtures()["Petersen"][:2]),
    }


def independent_tiny_oracle(rows):
    n = len(rows)
    if n % 3:
        return ()
    winners = []
    for positions in combinations(range(n), n//3):
        bits = sum(1 << v for v in positions)
        if valid_witness(rows, bits):
            winners.append(bits)
    return tuple(winners)


def self_test():
    cases = fixtures()
    expected = {"AffinePlane9_SAT": True, "Fano7_UNSAT_weight": False,
                "Regular12_UNSAT": False, "HolyerK4_SAT": True}
    result = {}
    for name in expected:
        rows = cases[name]
        ref = independent_tiny_oracle(rows)
        assert bool(ref) == expected[name], (name, ref)
        state = solve(rows, node_budget=4*len(rows)**2)
        assert (state["verdict"] == "SAT") == expected[name], (name, state)
        assert state["verdict"] != "UNKNOWN_RESOURCE_LIMIT", (name, state)
        if ref:
            assert valid_witness(rows, state["witness_bits"])
        result[name] = {"verdict": state["verdict"],
                        "n": len(rows), "oracle_witnesses": len(ref),
                        "initial_frontier_bound": state["initial_frontier_bound"],
                        "initial_GF2_candidates": state["initial_GF2_candidates"],
                        "nodes": state.get("work_nodes_this_call"),
                        "cooperative_stalls": state["cooperative_stalls"],
                        "found_by": state.get("found_by")}
    rows = cases["AffinePlane9_SAT"]
    assert result["AffinePlane9_SAT"]["initial_frontier_bound"] == 4
    assert result["AffinePlane9_SAT"]["initial_GF2_candidates"] == 4
    assert result["AffinePlane9_SAT"]["oracle_witnesses"] == 3
    # An accepted proof must be replayable independently; invalid
    # expert claims must be rejected before changing shared frontier.
    source = (0, 0)
    good, u0, u1, significant = verify_progress(
        rows, source, [(1, 0), (0, 1)],
        {"kind": "BRANCH", "variable": 0})
    assert good and u1 <= u0
    assert not verify_progress(
        rows, source, [(0, 0)],
        {"kind": "GF2"})[0]
    assert not verify_progress(
        rows, source, [(0, 0)],
        {"kind": "UNSUPPORTED"})[0]
    p = cases["HolyerPetersen_UNSAT"]
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as folder:
        file = str(Path(folder)/"resume.json")
        v = solve(p, node_budget=3, checkpoint=file, kernel_limit=8)
        assert v["verdict"] == "UNKNOWN_RESOURCE_LIMIT" and v["frontier_count"]>0
        # Finite falsification of this SPECIFIC progress policy: on
        # Petersen-Holyer, the first cube is unconstrained by local
        # forced assignments, and its exact parity bound is unchanged
        # by at least one complete Boolean split. No fractional
        # improvement for this bounded expert portfolio at that step.
        branches = [ev for ev in v["proof_step_log"]
                    if ev.get("expert") == "BRANCH"]
        assert branches and branches[0]["U_after"] == branches[0]["U_before"]
        assert v["cooperative_stalls"] > 0
        resumed = solve(p, node_budget=3, resume=file, checkpoint=file)
        assert resumed["total_visited"] >= v["total_visited"]
        assert resumed["verdict"] in ("UNKNOWN_RESOURCE_LIMIT","UNSAT")
        assert resumed["work_nodes_this_call"] <= 3
        result["HolyerPetersen_bounded"] = {
            "initial_bound": v["initial_frontier_bound"],
            "first": v["verdict"], "resumed": resumed["verdict"],
            "total_visited": resumed["total_visited"],
            "stalls": v["cooperative_stalls"]+resumed["cooperative_stalls"]}
        try:
            solve(rows, node_budget=1, resume=file)
        except ValueError:
            pass
        else:
            raise AssertionError("wrong graph checkpoint accepted")
    return {"status":"CERTIFIED_FINITE_COOPERATIVE_EXPERIMENT",
            "cases":result,
            "universal_cooperative_progress":"NOT_PROVED",
            "P_vs_NP":"OPEN"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--fixture", choices=tuple(fixtures()))
    ap.add_argument("--rows", help="JSON array of n 3-variable clauses")
    ap.add_argument("--node-budget", type=int, default=200)
    ap.add_argument("--kernel-limit", type=int, default=8)
    ap.add_argument("--checkpoint")
    ap.add_argument("--resume")
    args = ap.parse_args()
    if args.self_test:
        out = self_test()
    elif args.fixture or args.rows:
        rows = fixtures()[args.fixture] if args.fixture else json.loads(
            Path(args.rows).read_text(encoding="utf-8"))
        out = solve(rows, node_budget=args.node_budget,
                    kernel_limit=min(args.kernel_limit, 8),
                    checkpoint=args.checkpoint, resume=args.resume)
    else:
        ap.error("use --self-test, --fixture or --rows")
    print(json.dumps(out, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
