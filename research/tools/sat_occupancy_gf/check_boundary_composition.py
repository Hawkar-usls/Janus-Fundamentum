import itertools, json, random

def sat_clause(clause, a):
    if not clause:
        return False
    return any((a[abs(l)] if l > 0 else not a[abs(l)]) for l in clause)

def occupancy(clauses, a):
    return sum(1 for c in clauses if sat_clause(c, a))

def conv(x, y):
    z = [0] * (len(x) + len(y) - 1)
    for i, aa in enumerate(x):
        for j, bb in enumerate(y):
            z[i + j] += aa * bb
    return z

def message(clauses, boundary, internal):
    out = {}
    for bits in itertools.product((False, True), repeat=len(boundary)):
        beta = dict(zip(boundary, bits))
        coeff = [0] * (len(clauses) + 1)
        for ibits in itertools.product((False, True), repeat=len(internal)):
            a = dict(beta)
            a.update(zip(internal, ibits))
            coeff[occupancy(clauses, a)] += 1
        out[bits] = coeff
    return out

def compose(A, B, boundary, ia, ib):
    ma = message(A, boundary, ia)
    mb = message(B, boundary, ib)
    total = [0] * (len(A) + len(B) + 1)
    for beta in ma:
        c = conv(ma[beta], mb[beta])
        total = [x + y for x, y in zip(total, c)]
    return total, ma, mb

def direct(clauses, variables):
    coeff = [0] * (len(clauses) + 1)
    for bits in itertools.product((False, True), repeat=len(variables)):
        a = dict(zip(variables, bits))
        coeff[occupancy(clauses, a)] += 1
    return coeff

def check_case(A, B, boundary, ia, ib):
    got, ma, mb = compose(A, B, boundary, ia, ib)
    want = direct(A + B, boundary + ia + ib)
    return got == want, got, want, ma, mb

def rand_clause(pool, rng):
    return [(v if rng.random() < .5 else -v)
            for v in [rng.choice(pool) for _ in range(3)]]

def random_case(rng):
    k = rng.randint(0, 4)
    na = rng.randint(0, 3)
    nb = rng.randint(0, 3)
    boundary = list(range(1, k + 1))
    ia = list(range(k + 1, k + 1 + na))
    ib = list(range(k + 1 + na, k + 1 + na + nb))
    pa = boundary + ia
    pb = boundary + ib
    if not pa:
        ia = [1]
        pa = [1]
    if not pb:
        start = max(pa) + 1
        ib = [start]
        pb = [start]
    A = [rand_clause(pa, rng) for _ in range(rng.randint(0, 5))]
    B = [rand_clause(pb, rng) for _ in range(rng.randint(0, 5))]
    return A, B, boundary, ia, ib

def main():
    checks = []
    controls = [
        ("EMPTY_BOUNDARY", [[1, 1, 1]], [[2, 2, 2]], [], [1], [2]),
        ("ONE_BOUNDARY_COUPLING",
         [[1, 2, 2], [-1, 3, 3]],
         [[1, 4, 4], [-1, 5, 5]], [1], [2, 3], [4, 5]),
        ("EXPLICIT_EMPTY_CLAUSE_CONTRADICTION_STATE",
         [[], [1, 1, 1]], [[2, 2, 2]], [], [1], [2])
    ]
    for name, A, B, b, ia, ib in controls:
        ok, got, want, _, _ = check_case(A, B, b, ia, ib)
        checks.append({"name": name, "pass": ok, "gf": got, "direct": want})
    rng = random.Random(20260913)
    random_pass = 0
    random_total = 64
    for i in range(random_total):
        A, B, b, ia, ib = random_case(rng)
        ok, _, _, _, _ = check_case(A, B, b, ia, ib)
        random_pass += int(ok)
        if not ok:
            checks.append({"name": f"RANDOM_{i}", "pass": False,
                           "A": A, "B": B, "boundary": b})
    scaling = []
    for k in range(13):
        b = list(range(1, k + 1))
        av = k + 1
        bv = k + 2
        A = [[v, av, av] for v in b]
        B = [[-v, bv, bv] for v in b]
        _, ma, mb = compose(A, B, b, [av], [bv])
        rows = len(ma)
        cells = rows * (len(A) + 1) + len(mb) * (len(B) + 1)
        scaling.append({"k": k, "rows_per_block": rows,
                        "expected_rows": 2 ** k,
                        "coefficient_cells_both_blocks": cells})
    all_ok = (all(c["pass"] for c in checks)
              and random_pass == random_total
              and all(s["rows_per_block"] == s["expected_rows"]
                      for s in scaling))
    verdict = (
        "PASS_EXACT_OCCUPANCY_GF_COMPOSITION__BOUNDARY_MESSAGE_EXPONENTIAL_IN_SEPARATOR_WIDTH"
        if all_ok else "FALSIFIED_EXACT_COMPOSITION"
    )
    print(json.dumps({
        "schema": "JANUS_TRUMP_SAT_OCCUPANCY_GF_GATE_V1",
        "verdict": verdict,
        "controls": checks,
        "random": {"passed": random_pass, "total": random_total},
        "scaling": scaling,
        "theorem_scope": "two-block exact clause partition with shared-variable boundary and disjoint internal variables",
        "complexity_observation": "message rows are exactly 2^k for explicit boundary enumeration; exact composition alone does not yield polynomial time for unbounded k",
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN",
                              "Pi_negative_evidence_weight": 0}
    }, sort_keys=True))

if __name__ == "__main__":
    main()
