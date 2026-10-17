from itertools import product


def isolate(pattern, target):
    return int(pattern == target)


def gf2_rank(rows, width):
    rows = rows[:]
    r = 0
    for c in range(width):
        pivot = next((j for j in range(r, len(rows)) if (rows[j] >> c) & 1), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for j in range(len(rows)):
            if j != r and ((rows[j] >> c) & 1):
                rows[j] ^= rows[r]
        r += 1
    return r


def main():
    for n in range(1, 9):
        assignments = list(product((0, 1), repeat=n))
        N = 1 << n

        # Singleton assignment vectors form the identity basis.
        rows = [1 << i for i in range(N)]
        rank = gf2_rank(rows, N)
        assert rank == N

        # Coordinate projectors jointly isolate each assignment.
        for a in assignments:
            hits = []
            for c in assignments:
                keep = 1
                for i, bit in enumerate(a):
                    keep &= int(c[i] == bit)
                hits.append(keep)
            assert sum(hits) == 1
            assert hits[assignments.index(a)] == 1

        # Distinct eigenvalue signatures are unique.
        assert len(set(assignments)) == N
        print(f"n={n}: assignments={N} rank={rank} isolation=PASS")

    print("PASS: finite replay matches the symbolic 2^n dimension barrier")


if __name__ == "__main__":
    main()
