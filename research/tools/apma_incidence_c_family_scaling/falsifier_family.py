import math


def cycle_2cnf(n):
    n = int(n)
    if n < 3:
        raise ValueError("n must be >= 3")
    clauses = []
    for i in range(1, n + 1):
        j = 1 if i == n else i + 1
        if i % 2:
            clauses.append((i, -j))
        else:
            clauses.append((-i, j))
    return tuple(clauses)


def fixed_c_counterexample(c):
    c = float(c)
    if not c > 0:
        raise ValueError("c must be positive")
    C = int(math.ceil(max(1.0, c)))
    n = 16 * C * C
    return {
        "requested_c": c,
        "integer_majorant_C": C,
        "n": n,
        "source": cycle_2cnf(n),
        "claimed_k": n,
        "claimed_L": 4 * n,
        "proof_bound": "2^k > L^C >= L^c",
    }
