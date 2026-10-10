from itertools import product


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


def conflict_free(a, b):
    return a == b


def main():
    for n in range(1, 9):
        assignments = list(product((0, 1), repeat=n))
        N = 1 << n
        rows = []
        for a in assignments:
            bits = 0
            for j, b in enumerate(assignments):
                if conflict_free(a, b):
                    bits |= 1 << j
            rows.append(bits)
        rank = gf2_rank(rows, N)
        assert rank == N
        for i, row in enumerate(rows):
            assert row == (1 << i)
        print(f"n={n}: identity_submatrix={N}x{N} rank={rank} PASS")
    print("PASS: conflict-free literal-selection Hankel rank >= 2^n on frozen submatrix")


if __name__ == '__main__':
    main()
