#!/usr/bin/env python3
"""Provider finite replay for the large-support ROBDD Akinator lane."""

from itertools import product


class BDD:
    def __init__(self, order):
        self.order = {v: i for i, v in enumerate(order)}
        self.nodes = {0: None, 1: None}
        self.unique = {}
        self.next_id = 2

    def mk(self, idx, lo, hi):
        if lo == hi:
            return lo
        key = (idx, lo, hi)
        if key in self.unique:
            return self.unique[key]
        u = self.next_id
        self.next_id += 1
        self.unique[key] = u
        self.nodes[u] = key
        return u

    def var(self, name):
        return self.mk(self.order[name], 0, 1)

    def top(self, u):
        return 10**18 if u < 2 else self.nodes[u][0]

    def cof(self, u, idx):
        if u < 2:
            return u, u
        j, lo, hi = self.nodes[u]
        return (lo, hi) if j == idx else (u, u)

    def neg(self, root):
        memo = {}
        def rec(u):
            if u == 0: return 1
            if u == 1: return 0
            if u in memo: return memo[u]
            idx, lo, hi = self.nodes[u]
            memo[u] = self.mk(idx, rec(lo), rec(hi))
            return memo[u]
        return rec(root)

    def land(self, a, b):
        memo = {}
        def rec(u, v):
            if u == 0 or v == 0: return 0
            if u == 1: return v
            if v == 1: return u
            key = tuple(sorted((u, v)))
            if key in memo: return memo[key]
            idx = min(self.top(u), self.top(v))
            u0, u1 = self.cof(u, idx)
            v0, v1 = self.cof(v, idx)
            memo[key] = self.mk(idx, rec(u0, v0), rec(u1, v1))
            return memo[key]
        return rec(a, b)

    def lor(self, a, b):
        return self.neg(self.land(self.neg(a), self.neg(b)))

    def xor(self, a, b):
        return self.lor(self.land(a, self.neg(b)), self.land(self.neg(a), b))

    def iff(self, a, b):
        return self.neg(self.xor(a, b))

    def size(self, root):
        seen = set()
        def dfs(u):
            if u < 2 or u in seen: return
            seen.add(u)
            _, lo, hi = self.nodes[u]
            dfs(lo); dfs(hi)
        dfs(root)
        return len(seen)


def parity(n):
    b = BDD([f"x{i}" for i in range(n)])
    root = 0
    for i in range(n):
        root = b.xor(root, b.var(f"x{i}"))
    return b, root


def eq(n, interleaved):
    order = ([z for i in range(n) for z in (f"x{i}", f"y{i}")]
             if interleaved else
             [f"x{i}" for i in range(n)] + [f"y{i}" for i in range(n)])
    b = BDD(order)
    root = 1
    for i in range(n):
        root = b.land(root, b.iff(b.var(f"x{i}"), b.var(f"y{i}")))
    return b, root


def main():
    for n in range(1, 33):
        b, root = parity(n)
        assert b.size(root) <= 2*n

    for n in range(1, 10):
        bad, rb = eq(n, False)
        good, rg = eq(n, True)
        assert bad.size(rb) >= 2**n
        assert good.size(rg) <= 4*n

        ys = list(product((False, True), repeat=n))
        sigs = set()
        for x in product((False, True), repeat=n):
            sigs.add(tuple(y == x for y in ys))
        assert len(sigs) == 2**n

    print("C025_AKINATOR_ROBDD_PARITY_LINEAR_SIZE_FINITE = PASS")
    print("C025_AKINATOR_ROBDD_EQ_BAD_ORDER_EXP_FRONTIER_FINITE = PASS")
    print("C025_AKINATOR_ROBDD_EQ_INTERLEAVED_LINEAR_SIZE_FINITE = PASS")
    print("C025_AKINATOR_ROBDD_RESIDUAL_FRONTIER_FINITE = PASS")
    print("C025_AKINATOR_ROBDD_LOCAL_CERTIFICATE = ANALYTIC_THEOREM_NOT_CI")
    print("C025_AKINATOR_GENERAL_ORDERING_HARDNESS = EXTERNAL_SOURCE_RESULT_NOT_CI")
    print("C025_AKINATOR_TARGET_NW_ORDERING_HARDNESS = NOT_PROVED")
    print("C025_AKINATOR_GLOBAL_PROGRESS = OPEN")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
