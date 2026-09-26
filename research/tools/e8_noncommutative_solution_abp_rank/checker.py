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


def main():
    for k in range(1, 9):
        words = list(product((0, 1), repeat=k))
        N = 1 << k
        # Coefficient matrix at the x|y cut for S_k is identity.
        rows = []
        for a in words:
            bits = 0
            for j, b in enumerate(words):
                if a == b:
                    bits |= 1 << j
            rows.append(bits)
        assert all(row == (1 << i) for i, row in enumerate(rows))
        rank = gf2_rank(rows, N)
        assert rank == N
        print(f"k={k}: coefficient_matrix=I_{N}, rank={rank}, ABP_width_lower_bound={rank}")
    print("PASS: finite replay matches the symbolic Nisan-rank lower bound family")


if __name__ == '__main__':
    main()
