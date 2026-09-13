import itertools, json, random, statistics
from collections import defaultdict

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

def poly_add(x, y):
    return [a + b for a, b in zip(x, y)]

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

def direct(clauses, variables):
    coeff = [0] * (len(clauses) + 1)
    for bits in itertools.product((False, True), repeat=len(variables)):
        a = dict(zip(variables, bits))
        coeff[occupancy(clauses, a)] += 1
    return coeff

def quotient_compose(A, B, boundary, ia, ib):
    ma = message(A, boundary, ia)
    mb = message(B, boundary, ib)
    groups = defaultdict(list)
    for beta, sig in mb.items():
        groups[tuple(sig)].append(beta)
    total = [0] * (len(A) + len(B) + 1)
    for sig, betas in groups.items():
        agg = [0] * (len(A) + 1)
        for beta in betas:
            agg = poly_add(agg, ma[beta])
        total = poly_add(total, conv(agg, list(sig)))
    return total, ma, mb, groups

def rand_clause(pool, rng):
    return [(v if rng.random() < .5 else -v)
            for v in [rng.choice(pool) for _ in range(3)]]
def random_case(rng):
    k = rng.randint(0, 4)
    na = rng.randint(1, 2)
    nb = rng.randint(1, 2)
    boundary = list(range(1, k + 1))
    ia = list(range(k + 1, k + 1 + na))
    ib = list(range(k + 1 + na, k + 1 + na + nb))
    pa = boundary + ia or [1]
    pb = boundary + ib or [max(pa) + 1]
    if not ia and not boundary:
        ia = [pa[0]]
    if not ib and not boundary:
        ib = [pb[0]]
    A = [rand_clause(pa, rng) for _ in range(rng.randint(0, 4))]
    B = [rand_clause(pb, rng) for _ in range(rng.randint(0, 4))]
    return A, B, boundary, ia, ib

def sig_for_beta(clauses, boundary, beta_bits, internal):
    beta = dict(zip(boundary, beta_bits))
    coeff = [0] * (len(clauses) + 1)
    for ibits in itertools.product((False, True), repeat=len(internal)):
        a = dict(beta)
        a.update(zip(internal, ibits))
        coeff[occupancy(clauses, a)] += 1
    return coeff

def pairwise_distinguisher(k):
    boundary = list(range(1, k + 1))
    y, z = k + 1, k + 2
    states = list(itertools.product((False, True), repeat=k))
    checked = 0
    for p, beta in enumerate(states):
        for beta2 in states[p + 1:]:
            i = next(j for j in range(k) if beta[j] != beta2[j])
            var = boundary[i]
            lit = var if beta[i] else -var
            clause = [[lit, y, z]]
            s1 = sig_for_beta(clause, boundary, beta, [y, z])
            s2 = sig_for_beta(clause, boundary, beta2, [y, z])
            if s1 != [0, 4] or s2 != [1, 3]:
                return False, checked, {"k": k, "beta": beta, "beta2": beta2, "s1": s1, "s2": s2}
            checked += 1
    return True, checked, None
def main():
    fixed = {
        "A": [[1, 3, 3], [-2, 4, 4]],
        "B": [[1, 5, 6], [-1, 5, -6], [2, 5, 5]],
        "boundary": [1, 2], "ia": [3, 4], "ib": [5, 6]
    }
    q, _, _, groups = quotient_compose(**fixed)
    want = direct(fixed["A"] + fixed["B"],
                  fixed["boundary"] + fixed["ia"] + fixed["ib"])
    fixed_ok = q == want

    rng = random.Random(20260913)
    random_total = 64
    random_pass = 0
    random_failure = None
    for i in range(random_total):
        A, B, b, ia, ib = random_case(rng)
        got, _, _, _ = quotient_compose(A, B, b, ia, ib)
        want_i = direct(A + B, b + ia + ib)
        if got == want_i:
            random_pass += 1
        elif random_failure is None:
            random_failure = {"i": i, "A": A, "B": B, "boundary": b,
                              "got": got, "want": want_i}

    A, B, b, ia, ib = [], [[1, 2, 3]], [1], [], [2, 3]
    correct, ma, mb, _ = quotient_compose(A, B, b, ia, ib)
    agg_left = [sum(ma[beta][0] for beta in ma)]
    representative = mb[(False,)]
    bad_merge = conv(agg_left, representative)
    lossy_rejected = bad_merge != correct

    empty_case = ([], [[], [1, 2, 3]], [1], [], [2, 3])
    empty_got, _, _, _ = quotient_compose(*empty_case)
    empty_want = direct(empty_case[0] + empty_case[1], [1, 2, 3])
    empty_ok = empty_got == empty_want
    irrelevant_scaling = []
    for k in range(1, 11):
        boundary = list(range(1, k + 1))
        y, z = k + 1, k + 2
        Bk = [[1, y, z]]
        mbk = message(Bk, boundary, [y, z])
        classes = len({tuple(v) for v in mbk.values()})
        irrelevant_scaling.append({"k": k, "rows": 2 ** k, "classes": classes})

    random_class_scaling = []
    rng2 = random.Random(20260914)
    for k in range(1, 9):
        values = []
        boundary = list(range(1, k + 1))
        ib = [k + 1, k + 2]
        pool = boundary + ib
        for _ in range(12):
            Bk = [rand_clause(pool, rng2) for _ in range(max(1, 2 * k))]
            mbk = message(Bk, boundary, ib)
            values.append(len({tuple(v) for v in mbk.values()}))
        random_class_scaling.append({
            "k": k, "rows": 2 ** k, "min_classes": min(values),
            "median_classes": statistics.median(values), "max_classes": max(values)
        })

    distinguish = []
    distinguish_ok = True
    total_pairs = 0
    for k in range(1, 9):
        ok, pairs, failure = pairwise_distinguisher(k)
        distinguish.append({"k": k, "pass": ok, "pairs": pairs, "failure": failure})
        distinguish_ok = distinguish_ok and ok
        total_pairs += pairs

    all_ok = (fixed_ok and random_pass == random_total and lossy_rejected
              and empty_ok and distinguish_ok
              and all(x["classes"] == 2 for x in irrelevant_scaling))
    verdict = ("PASS_FORMULA_SCOPED_EXACT_QUOTIENT_AND_UNIVERSAL_CONGRUENCE_IDENTITY"
               if all_ok else "FALSIFIED_FROZEN_CLAIM")
    print(json.dumps({
        "schema": "JANUS_TRUMP_SAT_OCCUPANCY_FUTURE_Q_GATE_V1",
        "verdict": verdict,
        "fixed_future_control": {"pass": fixed_ok, "classes": len(groups),
                                 "rows": 2 ** len(fixed["boundary"]),
                                 "gf": q, "direct": want},
        "random_formula_scoped": {"passed": random_pass, "total": random_total,
                                   "failure": random_failure},
        "red_team": {
            "lossy_past_occupancy_merge_rejected": lossy_rejected,
            "bad_merge": bad_merge, "correct": correct,
            "empty_clause_contradiction_preserved": empty_ok
        },
        "formula_scoped_irrelevant_boundary_scaling": irrelevant_scaling,
        "formula_scoped_random_class_scaling": random_class_scaling,
        "universal_pairwise_3cnf_distinguisher": {
            "pass": distinguish_ok, "tested_k_max": 8,
            "tested_pairs": total_pairs, "per_k": distinguish,
            "symbolic_template": "choose differing x_i; clause (l_i OR y OR z): beta gives 4*z, beta' gives 1+3*z"
        },
        "scoped_theorem": "Under arbitrary future 3-CNF continuations that may use two fresh internal variables, universal boundary future-congruence is identity: every distinct beta,beta' is separated by one 3-literal clause.",
        "interpretation": "Fixed-future exact signatures can safely merge rows, including exponentially many irrelevant-boundary rows in special formulas; no formula-independent universal quotient can merge any distinct boundary assignments under the frozen continuation grammar.",
        "next": "Search formula-specific/stage-specific future signatures or a weaker exact query projection with provable polynomial representation and transition cost.",
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN",
                              "Pi_negative_evidence_weight": 0}
    }, sort_keys=True))

if __name__ == "__main__":
    main()

