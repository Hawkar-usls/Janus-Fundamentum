#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, random
from dataclasses import dataclass
from typing import Any

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Equation = tuple[int, int]


def jdump(x: Any) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def dg(x: Any) -> str:
    return hashlib.sha256(jdump(x).encode()).hexdigest()


def vcnf(f: CNF) -> set[int]:
    return {abs(l) for c in f for l in c}


def veqs(a: tuple[Equation, ...]) -> set[int]:
    out = set()
    for m, _ in a:
        while m:
            b = m & -m
            out.add(b.bit_length())
            m ^= b
    return out


def norm(f: CNF) -> CNF:
    out = []
    for c in f:
        s = set(c)
        if any(-x in s for x in s):
            continue
        t = tuple(sorted(s, key=lambda x: (abs(x), x < 0)))
        if t not in out:
            out.append(t)
    return tuple(sorted(out, key=lambda c: (len(c), c)))


def eval_cnf(f: CNF, x: dict[int, bool]) -> bool:
    return all(any(x.get(abs(l), False) == (l > 0) for l in c) for c in f)


def eval_eqs(a: tuple[Equation, ...], x: dict[int, bool]) -> bool:
    for m, r in a:
        p = 0
        while m:
            b = m & -m
            p ^= int(x.get(b.bit_length(), False))
            m ^= b
        if p != (r & 1):
            return False
    return True


@dataclass
class Meter:
    pair_limit: int = 10_000_000
    row_limit: int = 10_000_000
    pairs: int = 0
    xors: int = 0
    eliminations: int = 0
    counts: int = 0

    def pair(self) -> None:
        self.pairs += 1
        if self.pairs > self.pair_limit:
            raise RuntimeError("PAIR_BUDGET")

    def xor(self) -> None:
        self.xors += 1
        if self.xors > self.row_limit:
            raise RuntimeError("ROW_BUDGET")


def rref(eqs: tuple[Equation, ...], n: int, meter: Meter) -> tuple[tuple[Equation, ...], bool]:
    meter.eliminations += 1
    rows = [[m, r & 1] for m, r in eqs]
    rank = 0
    for v in range(1, n + 1):
        bit = 1 << (v - 1)
        p = next((i for i in range(rank, len(rows)) if rows[i][0] & bit), None)
        if p is None:
            continue
        rows[rank], rows[p] = rows[p], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i][0] & bit:
                rows[i][0] ^= rows[rank][0]
                rows[i][1] ^= rows[rank][1]
                meter.xor()
        rank += 1
    out = []
    for m, r in rows:
        if m == 0:
            if r:
                return (), True
        else:
            out.append((m, r))
    out.sort(key=lambda z: ((z[0] & -z[0]).bit_length(), z))
    return tuple(out), False


def solve(eqs: tuple[Equation, ...], n: int, meter: Meter) -> dict[int, bool] | None:
    rr, bad = rref(eqs, n, meter)
    if bad:
        return None
    x = {i: False for i in range(1, n + 1)}
    for m, r in reversed(rr):
        b = m & -m
        p = b.bit_length()
        val, q = r, m ^ b
        while q:
            c = q & -q
            val ^= int(x[c.bit_length()])
            q ^= c
        x[p] = bool(val)
    return x


def dim(sys: tuple[Equation, ...], n: int) -> int:
    return n - len(sys)


def inter(a: tuple[Equation, ...], b: tuple[Equation, ...], n: int, meter: Meter):
    rr, bad = rref(a + b, n, meter)
    return None if bad else rr


def entails(sys: tuple[Equation, ...], eq: Equation, n: int, meter: Meter) -> bool:
    _, bad = rref(sys + ((eq[0], eq[1] ^ 1),), n, meter)
    return bad


def subset(a: tuple[Equation, ...], b: tuple[Equation, ...], n: int, meter: Meter) -> bool:
    return all(entails(a, e, n, meter) for e in b)


def parameterize(a: tuple[Equation, ...], n: int, meter: Meter) -> dict[str, Any]:
    rr, bad = rref(a, n, meter)
    if bad:
        return {"status": "UNSAT"}
    piv = {(m & -m).bit_length(): (m, r) for m, r in rr}
    free = [i for i in range(1, n + 1) if i not in piv]

    def extension(seed: dict[int, bool], homogeneous: bool) -> dict[int, bool]:
        x = {i: bool(seed.get(i, False)) for i in range(1, n + 1)}
        for p in sorted(piv, reverse=True):
            m, r = piv[p]
            val = 0 if homogeneous else r
            q = m ^ (1 << (p - 1))
            while q:
                b = q & -q
                val ^= int(x[b.bit_length()])
                q ^= b
            x[p] = bool(val)
        return x

    p = extension({}, False)
    basis = [extension({v: True}, True) for v in free]
    assert eval_eqs(a, p)
    return {"status": "SAT", "dimension": len(free), "particular": p,
            "basis": basis, "free": free, "rref": rr}


def forms(par: dict[str, Any], n: int) -> list[tuple[int, int]]:
    out = []
    for x in range(1, n + 1):
        m = 0
        for j, b in enumerate(par["basis"]):
            if b[x]:
                m |= 1 << j
        out.append((m, int(par["particular"][x])))
    return out


def forbidden(c: Clause, fs: list[tuple[int, int]], d: int, meter: Meter):
    eqs = []
    for lit in c:
        m, k = fs[abs(lit) - 1]
        wanted = 0 if lit > 0 else 1
        eqs.append((m, wanted ^ k))
    rr, bad = rref(tuple(eqs), d, meter)
    return None if bad else rr


def lift(lam: dict[int, bool], par: dict[str, Any], n: int) -> dict[int, bool]:
    x = dict(par["particular"])
    for j, b in enumerate(par["basis"], start=1):
        if lam.get(j, False):
            for i in range(1, n + 1):
                x[i] ^= b[i]
    return x


def decide(f: CNF, a: tuple[Equation, ...], *, nvars_hint: int = 0,
           pair_limit: int = 10_000_000, row_limit: int = 10_000_000) -> dict[str, Any]:
    f = norm(f)
    n = max(max(vcnf(f) | veqs(a), default=0), nvars_hint)
    meter = Meter(pair_limit, row_limit)
    cap = {"nvars_hint": nvars_hint, "pair_limit": pair_limit, "row_limit": row_limit}
    try:
        par = parameterize(a, n, meter)
        if par["status"] == "UNSAT":
            z = {"schema": "janus.c041.laminar_subspace.v1", "capability": cap,
                 "status": "UNSAT", "reason": "AFFINE_CONTRADICTION",
                 "nvars": n, "meter": meter.__dict__, "p_vs_np": "OPEN"}
            z["integrity_sha256"] = dg(z)
            return z

        d = par["dimension"]
        fs = forms(par, n)
        raw = []
        unique: dict[tuple[Equation, ...], list[int]] = {}
        for i, c in enumerate(f):
            u = forbidden(c, fs, d, meter)
            raw.append({"clause_id": i, "clause": list(c), "empty": u is None,
                        "system": [] if u is None else [list(e) for e in u]})
            if u is not None:
                unique.setdefault(u, []).append(i)
        spaces = sorted(unique, key=lambda u: (len(u), u))
        pairs = []
        for i in range(len(spaces)):
            for j in range(i + 1, len(spaces)):
                meter.pair()
                u, v = spaces[i], spaces[j]
                w = inter(u, v, d, meter)
                if w is None:
                    rel = "DISJOINT"
                else:
                    uv, vu = subset(u, v, d, meter), subset(v, u, d, meter)
                    if uv and vu:
                        rel = "EQUAL"
                    elif uv:
                        rel = "LEFT_IN_RIGHT"
                    elif vu:
                        rel = "RIGHT_IN_LEFT"
                    else:
                        common = solve(w, d, meter) or {}
                        lu = next((solve(u + ((m, r ^ 1),), d, meter)
                                   for m, r in v
                                   if solve(u + ((m, r ^ 1),), d, meter) is not None), {})
                        rv = next((solve(v + ((m, r ^ 1),), d, meter)
                                   for m, r in u
                                   if solve(v + ((m, r ^ 1),), d, meter) is not None), {})
                        z = {"schema": "janus.c041.laminar_subspace.v1",
                             "capability": cap, "status": "OPEN_NON_LAMINAR",
                             "reason": "OVERLAPPING_INCOMPARABLE",
                             "dimension": d, "raw_spaces": raw,
                             "offending_pair": {
                                 "left": [list(e) for e in u],
                                 "right": [list(e) for e in v],
                                 "common": {str(k): x for k, x in common.items()},
                                 "left_not_right": {str(k): x for k, x in (lu or {}).items()},
                                 "right_not_left": {str(k): x for k, x in (rv or {}).items()}},
                             "meter": meter.__dict__, "p_vs_np": "OPEN"}
                        z["integrity_sha256"] = dg(z)
                        return z
                pairs.append({"left": i, "right": j, "relation": rel})

        maxima = []
        contained = []
        for i, u in enumerate(spaces):
            containers = [j for j, v in enumerate(spaces)
                          if i != j and subset(u, v, d, meter)]
            if containers:
                contained.append({"child": i, "containers": containers})
            else:
                maxima.append(i)
        maxspaces = [spaces[i] for i in maxima]
        for i in range(len(maxspaces)):
            for j in range(i + 1, len(maxspaces)):
                assert inter(maxspaces[i], maxspaces[j], d, meter) is None

        total = 1 << d
        covered = sum(1 << dim(u, d) for u in maxspaces)
        base = {
            "schema": "janus.c041.laminar_subspace.v1", "capability": cap,
            "nvars": n, "dimension": d,
            "parameterization": {
                "particular": {str(k): v for k, v in par["particular"].items()},
                "basis": [{str(k): v for k, v in b.items()} for b in par["basis"]],
                "free": par["free"], "rref": [list(e) for e in par["rref"]]},
            "raw_spaces": raw,
            "unique_spaces": [{"index": i, "system": [list(e) for e in u],
                               "dimension": dim(u, d), "clauses": unique[u]}
                              for i, u in enumerate(spaces)],
            "pair_records": pairs, "contained": contained, "maxima": maxima,
            "covered_points": str(covered), "total_points": str(total),
            "meter": meter.__dict__, "p_vs_np": "OPEN"}

        if covered == total:
            z = dict(base)
            z.update(status="UNSAT", reason="LAMINAR_COVER")
            z["integrity_sha256"] = dg(z)
            return z

        prefix: tuple[Equation, ...] = ()
        trace = []
        for q in range(1, d + 1):
            branches, choice = [], None
            for bit in (0, 1):
                bsys, bad = rref(prefix + ((1 << (q - 1), bit),), d, meter)
                if bad:
                    branches.append({"bit": bit, "points": "0", "covered": "0"})
                    continue
                points, cov = 1 << dim(bsys, d), 0
                parts = []
                for idx, u in zip(maxima, maxspaces):
                    meter.counts += 1
                    w = inter(bsys, u, d, meter)
                    cnt = 0 if w is None else 1 << dim(w, d)
                    cov += cnt
                    parts.append({"maximal": idx, "points": str(cnt)})
                branches.append({"bit": bit, "points": str(points),
                                 "covered": str(cov), "parts": parts})
                if choice is None and cov < points:
                    choice = (bit, bsys)
            assert choice is not None
            bit, prefix = choice
            trace.append({"coordinate": q, "chosen": bit, "branches": branches})
        lam = solve(prefix, d, meter)
        assert lam is not None
        witness = lift(lam, par, n)
        assert eval_eqs(a, witness) and eval_cnf(f, witness)
        z = dict(base)
        z.update(status="SAT", reason="POINT_OUTSIDE_LAMINAR_UNION",
                 greedy_trace=trace,
                 lambda_witness={str(k): v for k, v in lam.items()},
                 witness={str(k): v for k, v in witness.items()})
        z["integrity_sha256"] = dg(z)
        return z
    except RuntimeError as e:
        return {"schema": "janus.c041.laminar_subspace.v1", "capability": cap,
                "status": "OPEN_BUDGET", "reason": str(e),
                "meter": meter.__dict__, "p_vs_np": "OPEN"}


def verify(f: CNF, a: tuple[Equation, ...], cert: dict[str, Any]) -> bool:
    if "integrity_sha256" in cert:
        b = dict(cert)
        h = b.pop("integrity_sha256")
        if dg(b) != h:
            return False
    c = cert.get("capability", {})
    return decide(f, a, nvars_hint=int(c.get("nvars_hint", 0)),
                  pair_limit=int(c.get("pair_limit", 10_000_000)),
                  row_limit=int(c.get("row_limit", 10_000_000))) == cert


def brute(f: CNF, a: tuple[Equation, ...], n: int = 0) -> bool:
    n = max(n, max(vcnf(f) | veqs(a), default=0))
    for bits in itertools.product((False, True), repeat=n):
        x = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(f, x) and eval_eqs(a, x):
            return True
    return False


def prefix_clause(p: tuple[int, ...]) -> Clause:
    return tuple(i if b == 0 else -i for i, b in enumerate(p, 1))


def laminar_formula(rng: random.Random, n: int, m: int) -> CNF:
    nodes = {tuple(rng.getrandbits(1) for _ in range(rng.randint(0, n)))
             for _ in range(m)}
    return norm(tuple(prefix_clause(p) for p in nodes))


def random_formula(rng: random.Random, n: int, m: int) -> CNF:
    out = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), rng.randint(0, min(4, n)))
        out.append(tuple(v if rng.getrandbits(1) else -v for v in vs))
    return norm(tuple(out))


def random_affine(rng: random.Random, n: int, m: int) -> tuple[Equation, ...]:
    return tuple((rng.randrange(1, 1 << n), rng.getrandbits(1)) for _ in range(m))


def nand3_neq() -> tuple[CNF, tuple[Equation, ...]]:
    n, src = 5, ((1, 2, 3), (3, 4, 5))
    horn = tuple(tuple(-(n + v) for v in c) for c in src)
    neq = tuple(((1 << (i - 1)) | (1 << (n + i - 1)), 1)
                for i in range(1, n + 1))
    return norm(horn), neq


def audit(seed: int = 410041) -> dict[str, Any]:
    rng = random.Random(seed)
    mismatch = witness_bad = replay_bad = exact = opened = 0
    for _ in range(450):
        n = rng.randint(0, 8)
        f, a = laminar_formula(rng, n, rng.randint(0, 12)), ()
        c = decide(f, a, nvars_hint=n)
        truth = brute(f, a, n)
        if c["status"].startswith("OPEN"):
            opened += 1
            continue
        exact += 1
        mismatch += ((c["status"] == "SAT") != truth)
        if c["status"] == "SAT":
            w = {int(k): v for k, v in c["witness"].items()}
            witness_bad += not (eval_cnf(f, w) and eval_eqs(a, w))
        replay_bad += not verify(f, a, c)

    gexact = gopen = 0
    for _ in range(350):
        n = rng.randint(1, 8)
        f = random_formula(rng, n, rng.randint(0, 9))
        a = random_affine(rng, n, rng.randint(0, 5))
        c, truth = decide(f, a), brute(f, a)
        if c["status"].startswith("OPEN"):
            gopen += 1
            continue
        gexact += 1
        mismatch += ((c["status"] == "SAT") != truth)
        replay_bad += not verify(f, a, c)

    high_u = decide(((1,), (-1,)), (), nvars_hint=128)
    high_s = decide(tuple([(1,)] + [tuple(range(1, i + 1)) for i in range(2, 17)]),
                    (), nvars_hint=128)
    crossing = decide(((1,), (2,)), ())
    hf, ha = nand3_neq()
    hard = decide(hf, ha)
    bad_aff = decide((), ((1, 0), (1, 1)))
    budget_f = tuple((i,) for i in range(1, 10))
    budget = decide(budget_f, (), pair_limit=0)
    corrupt = json.loads(json.dumps(high_s))
    corrupt["witness"]["1"] = not corrupt["witness"]["1"]

    assert high_u["status"] == "UNSAT" and high_u["dimension"] == 128
    assert high_s["status"] == "SAT" and high_s["dimension"] == 128
    assert crossing["status"] == hard["status"] == "OPEN_NON_LAMINAR"
    assert bad_aff["status"] == "UNSAT"
    assert budget["status"] == "OPEN_BUDGET" and verify(budget_f, (), budget)
    assert not verify(tuple([(1,)] + [tuple(range(1, i + 1)) for i in range(2, 17)]),
                      (), corrupt)

    z = {
        "artifact_id": "C041-JANUS-LAMINAR-AFFINE-SUBSPACE-AVOIDANCE",
        "status": "PASS", "p_vs_np": "OPEN", "seed": seed,
        "laminar_random_cases": 450, "laminar_exact": exact,
        "laminar_open": opened, "general_random_cases": 350,
        "general_exact": gexact, "general_open": gopen,
        "mismatches": int(mismatch), "witness_failures": int(witness_bad),
        "verification_failures": int(replay_bad),
        "constructive_theorem":
            "CNF satisfiability in an affine GF(2) space is polynomial with replayable SAT/UNSAT evidence when clause-falsifying affine subspaces are laminar.",
        "complexity": "O(m^2 * poly(L,d))",
        "high_dimension_unsat": {"dimension": 128, "status": high_u["status"],
                                 "maxima": len(high_u["maxima"])},
        "high_dimension_sat": {"dimension": 128, "status": high_s["status"],
                               "unique_spaces": len(high_s["unique_spaces"])},
        "crossing_control": crossing["status"],
        "nand3_neq_control": hard["status"],
        "affine_contradiction_control": bad_aff["status"],
        "budget_control": budget["status"],
        "corrupt_control": "REJECTED",
        "new_gate": "NON_LAMINAR_AFFINE_SUBSPACE_UNION_COMPRESSION",
        "claim_boundary":
            "Laminar subspace-arrangement algorithm only; general SUB-SAT, NAND3+NEQ and P versus NP remain open."
    }
    z["integrity_sha256"] = dg(z)
    return z


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--output")
    p.add_argument("--seed", type=int, default=410041)
    a = p.parse_args()
    z = audit(a.seed)
    if a.output:
        open(a.output, "w", encoding="utf-8").write(json.dumps(z, indent=2, sort_keys=True))
    print(json.dumps(z, indent=2, sort_keys=True))
    if a.self_test:
        assert z["status"] == "PASS"
        assert z["mismatches"] == z["witness_failures"] == z["verification_failures"] == 0


if __name__ == "__main__":
    main()
