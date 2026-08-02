#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, math, random
from collections import defaultdict

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
AffineRow = tuple[tuple[int, ...], int]
Module = dict

def canon_clause(c: Clause):
    s = set(c)
    if any(-x in s for x in s):
        return None
    return tuple(sorted(s, key=lambda x: (abs(x), x < 0)))

def normalize(f: CNF) -> CNF:
    cs = []
    for c in f:
        q = canon_clause(c)
        if q is not None:
            cs.append(q)
    cs = sorted(set(cs), key=lambda c: (len(c), c))
    keep = []
    for c in cs:
        sc = set(c)
        if any(set(d) <= sc for d in keep):
            continue
        keep.append(c)
    return tuple(keep)

def cnf_vars(f: CNF) -> set[int]:
    return {abs(x) for c in f for x in c}

def eval_cnf(f: CNF, a: dict[int, bool]) -> bool:
    return all(any(a.get(abs(x), False) == (x > 0) for x in c) for c in f)

def substitute_cnf(f: CNF, fixed: dict[int, bool]) -> CNF:
    out = []
    for c in f:
        sat = False
        rem = []
        for lit in c:
            v = abs(lit)
            if v in fixed:
                if fixed[v] == (lit > 0):
                    sat = True
                    break
            else:
                rem.append(lit)
        if not sat:
            out.append(tuple(rem))
    return normalize(tuple(out))

def is_horn(f: CNF) -> bool:
    return all(sum(x > 0 for x in c) <= 1 for c in f)

def is_dual_horn(f: CNF) -> bool:
    return all(sum(x < 0 for x in c) <= 1 for c in f)

def horn_solve(f: CNF):
    f = normalize(f)
    a = {v: False for v in cnf_vars(f)}
    trace = []
    changed = True
    while changed:
        changed = False
        for i, c in enumerate(f):
            pos = [x for x in c if x > 0]
            body = [-x for x in c if x < 0]
            if all(a[v] for v in body):
                if not pos:
                    return False, None, {"kind": "HORN_UNSAT", "trace": trace + [["conflict", i]]}
                h = pos[0]
                if not a[h]:
                    a[h] = True
                    trace.append(["set", h, i])
                    changed = True
    assert eval_cnf(f, a)
    return True, a, {"kind": "HORN_SAT", "trace": trace, "witness": {str(k): v for k, v in a.items()}}

def verify_horn(f: CNF, sat: bool, cert: dict) -> bool:
    f = normalize(f)
    if not is_horn(f):
        return False
    if sat:
        w = {int(k): bool(v) for k, v in cert.get("witness", {}).items()}
        return cert.get("kind") == "HORN_SAT" and eval_cnf(f, w)
    a = {v: False for v in cnf_vars(f)}
    for step in cert.get("trace", []):
        if not step:
            return False
        op = step[0]
        if op == "set":
            if len(step) != 3:
                return False
            h = int(step[1])
            recorded_i = int(step[2])
            if not (0 <= recorded_i < len(f)):
                return False
            c = f[recorded_i]
            pos = [x for x in c if x > 0]
            body = [-x for x in c if x < 0]
            if pos != [h] or not all(a[v] for v in body):
                return False
            a[h] = True
        elif op == "conflict":
            if len(step) != 2:
                return False
            i = int(step[1])
            if not (0 <= i < len(f)):
                return False
            c = f[i]
            if any(x > 0 for x in c):
                return False
            if not all(a[-x] for x in c):
                return False
            return cert.get("kind") == "HORN_UNSAT"
        else:
            return False
    return False

def dual_horn_solve(f: CNF):
    flipped = tuple(tuple(-x for x in c) for c in f)
    sat, w, cert = horn_solve(flipped)
    if sat:
        out = {v: not b for v, b in w.items()}
        return True, out, {"kind": "DUAL_HORN_SAT", "inner": cert,
                           "witness": {str(k): v for k, v in out.items()}}
    return False, None, {"kind": "DUAL_HORN_UNSAT", "inner": cert}

def verify_dual_horn(f: CNF, sat: bool, cert: dict) -> bool:
    if not is_dual_horn(normalize(f)):
        return False
    flipped = tuple(tuple(-x for x in c) for c in f)
    if sat:
        w = {int(k): bool(v) for k, v in cert.get("witness", {}).items()}
        return cert.get("kind") == "DUAL_HORN_SAT" and eval_cnf(f, w)
    return cert.get("kind") == "DUAL_HORN_UNSAT" and verify_horn(flipped, False, cert.get("inner", {}))

def nest_point(f: CNF, v: int) -> bool:
    edges = [set(abs(x) for x in c) for c in normalize(f) if any(abs(x) == v for x in c)]
    return all(a <= b or b <= a for a in edges for b in edges)

def nest_order(f: CNF):
    cur = normalize(f)
    vs = set(cnf_vars(cur))
    order = []
    while vs:
        hit = None
        for v in sorted(vs):
            restricted = tuple(tuple(x for x in c if abs(x) in vs) for c in cur)
            if nest_point(restricted, v):
                hit = v
                break
        if hit is None:
            return None
        order.append(hit)
        vs.remove(hit)
    return order

def eliminate(f: CNF, x: int) -> CNF:
    f = normalize(f)
    pos = [c for c in f if x in c]
    neg = [c for c in f if -x in c]
    rest = [c for c in f if x not in c and -x not in c]
    res = []
    for p in pos:
        for n in neg:
            q = canon_clause(tuple(y for y in p if y != x) +
                             tuple(y for y in n if y != -x))
            if q is not None:
                res.append(q)
    return normalize(tuple(rest + res))

def beta_solve(f: CNF):
    f = normalize(f)
    order = nest_order(f)
    if order is None:
        return "OPEN", None, {"kind": "OPEN"}
    cur = f
    records = []
    for x in order:
        if not nest_point(cur, x):
            return "OPEN", None, {"kind": "OPEN"}
        nxt = eliminate(cur, x)
        records.append({"x": x, "before": [list(c) for c in cur], "after": [list(c) for c in nxt]})
        cur = nxt
    if () in cur:
        return False, None, {"kind": "BETA_UNSAT", "records": records}
    a = {}
    for rec in reversed(records):
        x = rec["x"]
        before = tuple(tuple(c) for c in rec["before"])
        chosen = None
        for xv in (False, True):
            trial = dict(a)
            trial[x] = xv
            if eval_cnf(before, trial):
                chosen = xv
                break
        if chosen is None:
            return "INVALID", None, {"kind": "INVALID"}
        a[x] = chosen
    assert eval_cnf(f, a)
    return True, a, {"kind": "BETA_SAT", "records": records,
                     "witness": {str(k): v for k, v in a.items()}}

def verify_beta(f: CNF, sat: bool, cert: dict) -> bool:
    f = normalize(f)
    records = cert.get("records", [])
    cur = f
    for rec in records:
        x = int(rec.get("x"))
        before = tuple(tuple(c) for c in rec.get("before", []))
        after = tuple(tuple(c) for c in rec.get("after", []))
        if before != cur or not nest_point(cur, x) or eliminate(cur, x) != after:
            return False
        cur = after
    if set(cnf_vars(cur)):
        return False
    if sat:
        w = {int(k): bool(v) for k, v in cert.get("witness", {}).items()}
        return cert.get("kind") == "BETA_SAT" and eval_cnf(f, w)
    return cert.get("kind") == "BETA_UNSAT" and () in cur

def canon_affine_row(vars_: tuple[int, ...], rhs: int) -> AffineRow:
    parity = set()
    for v in vars_:
        if v in parity:
            parity.remove(v)
        else:
            parity.add(v)
    return tuple(sorted(parity)), rhs & 1

def normalize_affine(rows: tuple[AffineRow, ...]) -> tuple[AffineRow, ...]:
    return tuple(canon_affine_row(tuple(vs), rhs) for vs, rhs in rows)

def affine_vars(rows: tuple[AffineRow, ...]) -> set[int]:
    return {v for vs, _ in rows for v in vs}

def eval_affine(rows: tuple[AffineRow, ...], a: dict[int, bool]) -> bool:
    return all((sum(bool(a.get(v, False)) for v in vs) & 1) == rhs for vs, rhs in rows)

def substitute_affine(rows: tuple[AffineRow, ...], fixed: dict[int, bool]) -> tuple[AffineRow, ...]:
    out = []
    for vs, rhs in normalize_affine(rows):
        nrhs = rhs
        rem = []
        for v in vs:
            if v in fixed:
                nrhs ^= int(bool(fixed[v]))
            else:
                rem.append(v)
        out.append((tuple(rem), nrhs))
    return tuple(out)

def affine_solve(rows: tuple[AffineRow, ...]):
    rows = normalize_affine(rows)
    variables = sorted(affine_vars(rows))
    col = {v: i for i, v in enumerate(variables)}
    work = []
    for i, (vs, rhs) in enumerate(rows):
        mask = 0
        for v in vs:
            mask ^= 1 << col[v]
        work.append([mask, rhs, 1 << i])
    ops = []
    rank = 0
    for c in range(len(variables)):
        pivot = next((i for i in range(rank, len(work)) if (work[i][0] >> c) & 1), None)
        if pivot is None:
            continue
        if pivot != rank:
            work[rank], work[pivot] = work[pivot], work[rank]
            ops.append(["swap", rank, pivot])
        for i in range(len(work)):
            if i != rank and ((work[i][0] >> c) & 1):
                work[i][0] ^= work[rank][0]
                work[i][1] ^= work[rank][1]
                work[i][2] ^= work[rank][2]
                ops.append(["xor", i, rank])
        rank += 1
    final = [{"mask": m, "rhs": b, "provenance": p} for m, b, p in work]
    contradiction = next((r for r in final if r["mask"] == 0 and r["rhs"] == 1), None)
    base = {"variables": variables, "operations": ops, "final_rows": final}
    if contradiction is not None:
        base.update({"kind": "AFFINE_UNSAT", "contradiction_provenance": contradiction["provenance"]})
        return False, None, base
    a = {v: False for v in variables}
    for r in final:
        if r["mask"] == 0:
            continue
        pivot = (r["mask"] & -r["mask"]).bit_length() - 1
        total = r["rhs"]
        rest = r["mask"] & ~(1 << pivot)
        while rest:
            low = rest & -rest
            j = low.bit_length() - 1
            total ^= int(a[variables[j]])
            rest ^= low
        a[variables[pivot]] = bool(total)
    assert eval_affine(rows, a)
    base.update({"kind": "AFFINE_SAT", "witness": {str(k): v for k, v in a.items()}})
    return True, a, base

def verify_affine(rows: tuple[AffineRow, ...], sat: bool, cert: dict) -> bool:
    rows = normalize_affine(rows)
    variables = cert.get("variables")
    if variables != sorted(affine_vars(rows)):
        return False
    col = {v: i for i, v in enumerate(variables)}
    work = []
    for i, (vs, rhs) in enumerate(rows):
        mask = 0
        for v in vs:
            mask ^= 1 << col[v]
        work.append([mask, rhs, 1 << i])
    for op in cert.get("operations", []):
        if len(op) != 3:
            return False
        kind, i, j = op
        if not (0 <= i < len(work) and 0 <= j < len(work)):
            return False
        if kind == "swap":
            work[i], work[j] = work[j], work[i]
        elif kind == "xor":
            work[i][0] ^= work[j][0]
            work[i][1] ^= work[j][1]
            work[i][2] ^= work[j][2]
        else:
            return False
    final = [{"mask": m, "rhs": b, "provenance": p} for m, b, p in work]
    if final != cert.get("final_rows"):
        return False
    for r in final:
        p = r["provenance"]
        mask = rhs = 0
        for i, (vs, b) in enumerate(rows):
            if (p >> i) & 1:
                rm = 0
                for v in vs:
                    rm ^= 1 << col[v]
                mask ^= rm
                rhs ^= b
        if mask != r["mask"] or rhs != r["rhs"]:
            return False
    if sat:
        w = {int(k): bool(v) for k, v in cert.get("witness", {}).items()}
        return cert.get("kind") == "AFFINE_SAT" and eval_affine(rows, w)
    p = cert.get("contradiction_provenance", 0)
    return (cert.get("kind") == "AFFINE_UNSAT" and
            any(r["mask"] == 0 and r["rhs"] == 1 and r["provenance"] == p for r in final))

def module_support(module: Module) -> set[int]:
    if module["type"] == "CNF":
        return cnf_vars(tuple(tuple(c) for c in module["clauses"]))
    return affine_vars(tuple((tuple(r["vars"]), int(r["rhs"])) for r in module["rows"]))

def substitute_module(module: Module, fixed: dict[int, bool]) -> Module:
    if module["type"] == "CNF":
        f = tuple(tuple(c) for c in module["clauses"])
        g = substitute_cnf(f, fixed)
        return {"type": "CNF", "clauses": [list(c) for c in g]}
    rows = tuple((tuple(r["vars"]), int(r["rhs"])) for r in module["rows"])
    out = substitute_affine(rows, fixed)
    return {"type": "AFFINE", "rows": [{"vars": list(vs), "rhs": rhs} for vs, rhs in out]}

def solve_module(module: Module):
    if module["type"] == "AFFINE":
        rows = tuple((tuple(r["vars"]), int(r["rhs"])) for r in module["rows"])
        sat, w, cert = affine_solve(rows)
        return {"status": "EXACT", "class": "AFFINE_GF2", "sat": sat, "witness": w, "certificate": cert}
    f = normalize(tuple(tuple(c) for c in module["clauses"]))
    if is_horn(f):
        sat, w, cert = horn_solve(f)
        return {"status": "EXACT", "class": "HORN", "sat": sat, "witness": w, "certificate": cert}
    if is_dual_horn(f):
        sat, w, cert = dual_horn_solve(f)
        return {"status": "EXACT", "class": "DUAL_HORN", "sat": sat, "witness": w, "certificate": cert}
    sat, w, cert = beta_solve(f)
    if sat != "OPEN" and sat != "INVALID":
        return {"status": "EXACT", "class": "BETA_ACYCLIC", "sat": sat, "witness": w, "certificate": cert}
    return {"status": "OPEN"}

def verify_module(module: Module, result: dict) -> bool:
    if result.get("status") != "EXACT":
        return False
    sat = bool(result["sat"])
    cls = result["class"]
    cert = result["certificate"]
    if module["type"] == "AFFINE":
        rows = tuple((tuple(r["vars"]), int(r["rhs"])) for r in module["rows"])
        return cls == "AFFINE_GF2" and verify_affine(rows, sat, cert)
    f = tuple(tuple(c) for c in module["clauses"])
    if cls == "HORN":
        return verify_horn(f, sat, cert)
    if cls == "DUAL_HORN":
        return verify_dual_horn(f, sat, cert)
    if cls == "BETA_ACYCLIC":
        return verify_beta(f, sat, cert)
    return False

def eval_module(module: Module, a: dict[int, bool]) -> bool:
    if module["type"] == "CNF":
        return eval_cnf(tuple(tuple(c) for c in module["clauses"]), a)
    rows = tuple((tuple(r["vars"]), int(r["rhs"])) for r in module["rows"])
    return eval_affine(rows, a)

def encoding_length(modules: list[Module]) -> int:
    total = 1 + len(modules)
    for m in modules:
        if m["type"] == "CNF":
            total += sum(1 + len(c) for c in m["clauses"])
        else:
            total += sum(2 + len(r["vars"]) for r in m["rows"])
    return total

def compose_bounded_interface(modules: list[Module]):
    counts = defaultdict(int)
    for m in modules:
        for v in module_support(m):
            counts[v] += 1
    boundary = sorted(v for v, c in counts.items() if c >= 2)
    L = encoding_length(modules)
    cap = int(math.log2(max(2, L)))
    if len(boundary) > cap:
        return {"status": "OPEN", "reason": "BOUNDARY_TOO_LARGE",
                "boundary": boundary, "boundary_size": len(boundary), "cap": cap, "encoding_length": L}
    ledger = []
    for bits in itertools.product((False, True), repeat=len(boundary)):
        fixed = dict(zip(boundary, bits))
        local_results = []
        any_open = False
        blocking = None
        for idx, m in enumerate(modules):
            sm = substitute_module(m, fixed)
            r = solve_module(sm)
            local_results.append({"module": idx, "substituted": sm, "result": r})
            if r["status"] == "EXACT" and not r["sat"] and blocking is None:
                blocking = idx
            if r["status"] == "OPEN":
                any_open = True
        if blocking is not None:
            ledger.append({"boundary": {str(k): v for k, v in fixed.items()},
                           "blocking_module": blocking,
                           "local": local_results[blocking]})
            continue
        if any_open:
            return {"status": "OPEN", "reason": "UNRECOGNIZED_RESIDUAL",
                    "boundary": boundary, "cap": cap, "encoding_length": L}
        witness = dict(fixed)
        for item in local_results:
            witness.update(item["result"].get("witness") or {})
        if all(eval_module(m, witness) for m in modules):
            return {"status": "EXACT", "sat": True, "class": "BOUNDED_INTERFACE_PORTFOLIO",
                    "boundary": boundary, "cap": cap, "encoding_length": L,
                    "witness": witness,
                    "certificate": {"kind": "COMPOSED_SAT",
                                    "boundary": {str(k): v for k, v in fixed.items()},
                                    "local_results": local_results}}
        return {"status": "INVALID"}
    return {"status": "EXACT", "sat": False, "class": "BOUNDED_INTERFACE_PORTFOLIO",
            "boundary": boundary, "cap": cap, "encoding_length": L,
            "certificate": {"kind": "COMPOSED_UNSAT", "ledger": ledger}}

def verify_composition(modules: list[Module], result: dict) -> bool:
    if result.get("status") != "EXACT":
        return False
    cert = result.get("certificate", {})
    if result["sat"]:
        if cert.get("kind") != "COMPOSED_SAT":
            return False
        fixed = {int(k): bool(v) for k, v in cert.get("boundary", {}).items()}
        w = {int(k): bool(v) for k, v in result.get("witness", {}).items()}
        if any(w.get(k) != v for k, v in fixed.items()):
            return False
        for item in cert.get("local_results", []):
            idx = item["module"]
            sm = substitute_module(modules[idx], fixed)
            if sm != item["substituted"] or not verify_module(sm, item["result"]):
                return False
        return all(eval_module(m, w) for m in modules)
    if cert.get("kind") != "COMPOSED_UNSAT":
        return False
    boundary = result["boundary"]
    expected = 1 << len(boundary)
    ledger = cert.get("ledger", [])
    if len(ledger) != expected:
        return False
    seen = set()
    for entry in ledger:
        fixed = {int(k): bool(v) for k, v in entry["boundary"].items()}
        key = tuple(fixed[v] for v in boundary)
        if key in seen:
            return False
        seen.add(key)
        idx = entry["blocking_module"]
        sm = substitute_module(modules[idx], fixed)
        item = entry["local"]
        if item["module"] != idx or item["substituted"] != sm:
            return False
        r = item["result"]
        if not (verify_module(sm, r) and r["sat"] is False):
            return False
    return len(seen) == expected

def nand3_neq_reduction(cnf: CNF, nvars: int) -> list[Module]:
    rows = [{"vars": [i, nvars + i], "rhs": 1} for i in range(1, nvars + 1)]
    horn = []
    for clause in cnf:
        args = []
        for lit in clause:
            v = abs(lit)
            falsity = nvars + v if lit > 0 else v
            args.append(falsity)
        horn.append([-v for v in args])
    return [{"type": "CNF", "clauses": horn},
            {"type": "AFFINE", "rows": rows}]

def brute_modules(modules: list[Module]):
    vs = sorted(set().union(*(module_support(m) for m in modules)))
    for bits in itertools.product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if all(eval_module(m, a) for m in modules):
            return True, a
    return False, None

def random_affine_audit(rng: random.Random, cases: int):
    mismatch = certfail = 0
    satc = unsatc = 0
    for _ in range(cases):
        n = rng.randint(0, 10)
        m = rng.randint(0, 16)
        rows = []
        for _ in range(m):
            vs = tuple(v for v in range(1, n + 1) if rng.getrandbits(1))
            rows.append((vs, rng.getrandbits(1)))
        rows = tuple(rows)
        sat, w, cert = affine_solve(rows)
        brute = False
        for bits in itertools.product((False, True), repeat=n):
            a = {i + 1: bits[i] for i in range(n)}
            if eval_affine(rows, a):
                brute = True
                break
        mismatch += int(sat != brute)
        certfail += int(not verify_affine(rows, sat, cert))
        satc += int(sat)
        unsatc += int(not sat)
    assert mismatch == 0 and certfail == 0
    return {"cases": cases, "sat": satc, "unsat": unsatc,
            "mismatches": mismatch, "certificate_failures": certfail}

def chain_beta_module(vars_: list[int], rng: random.Random) -> Module:
    clauses = []
    if not vars_:
        return {"type": "CNF", "clauses": []}
    for j in range(1, len(vars_) + 1):
        support = vars_[:j]
        clauses.append([v if rng.getrandbits(1) else -v for v in support])
    return {"type": "CNF", "clauses": clauses}

def random_composition_audit(rng: random.Random, cases: int):
    exact = opened = mismatch = certfail = 0
    for _ in range(cases):
        k = rng.randint(0, 2)
        boundary = list(range(1, k + 1))
        nextv = k + 1
        horn_local = list(range(nextv, nextv + rng.randint(1, 2))); nextv += len(horn_local)
        aff_local = list(range(nextv, nextv + rng.randint(1, 2))); nextv += len(aff_local)
        beta_local = list(range(nextv, nextv + rng.randint(1, 2))); nextv += len(beta_local)
        horn_vars = boundary + horn_local
        horn_clauses = []
        for _ in range(rng.randint(1, 4)):
            body = rng.sample(horn_vars, rng.randint(0, min(2, len(horn_vars))))
            heads = [v for v in horn_vars if v not in body]
            c = [-v for v in body]
            if heads and rng.getrandbits(1):
                c.append(rng.choice(heads))
            horn_clauses.append(c)
        rows = []
        av = boundary + aff_local
        for _ in range(rng.randint(1, 4)):
            chosen = [v for v in av if rng.getrandbits(1)]
            rows.append({"vars": chosen, "rhs": rng.getrandbits(1)})
        beta = chain_beta_module(boundary + beta_local, rng)
        modules = [
            {"type": "CNF", "clauses": horn_clauses},
            {"type": "AFFINE", "rows": rows},
            beta,
        ]
        r = compose_bounded_interface(modules)
        b, _ = brute_modules(modules)
        if r["status"] == "OPEN":
            opened += 1
            continue
        exact += 1
        mismatch += int(bool(r["sat"]) != b)
        certfail += int(not verify_composition(modules, r))
    assert mismatch == 0 and certfail == 0 and opened == 0
    return {"cases": cases, "exact": exact, "open": opened,
            "mismatches": mismatch, "certificate_failures": certfail}

def random_sat_formula(rng: random.Random, n: int, m: int) -> CNF:
    target = {i: bool(rng.getrandbits(1)) for i in range(1, n + 1)}
    out = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), 3)
        while True:
            c = tuple(v if rng.getrandbits(1) else -v for v in vs)
            if eval_cnf((c,), target):
                out.append(c)
                break
    return tuple(out)

def unsat_formula(rng: random.Random, n: int, extras: int) -> CNF:
    core = []
    for bits in itertools.product((False, True), repeat=3):
        core.append(tuple((-i if bits[i-1] else i) for i in (1, 2, 3)))
    for _ in range(extras):
        vs = rng.sample(range(1, n + 1), 3)
        core.append(tuple(v if rng.getrandbits(1) else -v for v in vs))
    return tuple(core)

def mixed_barrier_audit(rng: random.Random, pairs: int):
    mapping_fail = composer_false_exact = 0
    sat_count = unsat_count = 0
    for i in range(pairs * 2):
        n = rng.randint(3, 6)
        if i % 2 == 0:
            f = random_sat_formula(rng, n, rng.randint(3, 10))
            expected = True
            sat_count += 1
        else:
            f = unsat_formula(rng, n, rng.randint(0, 4))
            expected = False
            unsat_count += 1
        modules = nand3_neq_reduction(f, n)
        b, _ = brute_modules(modules)
        source_b = any(eval_cnf(f, dict(zip(range(1, n+1), bits)))
                       for bits in itertools.product((False, True), repeat=n))
        mapping_fail += int(b != source_b or source_b != expected)
        r = compose_bounded_interface(modules)
        if r["status"] == "EXACT":
            composer_false_exact += 1
    assert mapping_fail == 0 and composer_false_exact == 0
    return {"cases": pairs * 2, "sat": sat_count, "unsat": unsat_count,
            "mapping_failures": mapping_fail,
            "bounded_composer_exact_on_hard_image": composer_false_exact,
            "bounded_composer_status": "OPEN"}

def corruption_controls():
    rows = (((1, 2), 0), ((1, 2), 1))
    sat, w, cert = affine_solve(rows)
    assert not sat and verify_affine(rows, sat, cert)
    bad = json.loads(json.dumps(cert))
    bad["contradiction_provenance"] ^= 1
    assert not verify_affine(rows, False, bad)
    return {"valid_unsat_certificate": True, "corrupt_provenance_rejected": True}

def run(seed=340034):
    rng = random.Random(seed)
    affine = random_affine_audit(rng, 700)
    composition = random_composition_audit(rng, 300)
    barrier = mixed_barrier_audit(rng, 60)
    controls = corruption_controls()
    out = {
        "artifact_id": "C034-JANUS-AFFINE-PORTFOLIO-COMPOSITION",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "seed": seed,
        "affine_audit": affine,
        "bounded_interface_composition": composition,
        "horn_affine_np_hard_image": barrier,
        "corruption_controls": controls,
        "theorems": [
            "Explicit GF(2) systems admit deterministic polynomial solving with replayable row operations, SAT witnesses, and 0=1 provenance certificates.",
            "A heterogeneous exact-module network with k shared variables is solvable in O(2^k poly(L)); hence logarithmic shared boundary is polynomial.",
            "Arbitrary 3-SAT reduces linearly to a mixture of Horn NAND3 clauses and affine NEQ equations, so unrestricted Horn+affine composition is already NP-hard."
        ],
        "located_gate": "PROOF_CARRYING_CROSS_CLASS_INTERFACE_COMPRESSION",
        "claim_boundary": "Adds an exact affine engine and bounded-interface composition; does not solve unrestricted Horn-affine mixtures or arbitrary CNF."
    }
    out["integrity_sha256"] = hashlib.sha256(
        json.dumps(out, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    r = run()
    print(json.dumps(r, indent=2, sort_keys=True))
    if args.self_test:
        assert r["status"] == "PASS"

if __name__ == "__main__":
    main()
