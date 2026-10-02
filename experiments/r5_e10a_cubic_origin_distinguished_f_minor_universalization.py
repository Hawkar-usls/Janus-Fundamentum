#!/usr/bin/env python3
"""Finite controls for distinguished-f cubic-origin minor universalization.

The proof is structural.  This checker independently verifies, on seeded small
binary cocycle spaces, that:
  * all contracted/retained right nodes are ternary;
  * the construction completes to a square 3-regular binary H;
  * shortening contracted coordinates and puncturing deleted coordinates
    returns exactly the target cocycle row space;
  * the parent all-ones coordinate equals the target distinguished coordinate.
"""

from collections import defaultdict
import random

SEED = 510

def gf2_rank(vectors):
    basis = {}
    for x in vectors:
        y = x
        while y:
            p = y.bit_length() - 1
            if p in basis:
                y ^= basis[p]
            else:
                basis[p] = y
                break
    return len(basis)

def canonical_rowspace(rows):
    a = [x for x in rows if x]
    rr = 0
    maxbits = max((x.bit_length() for x in a), default=0)
    for c in range(maxbits):
        piv = next((i for i in range(rr, len(a)) if (a[i] >> c) & 1), None)
        if piv is None:
            continue
        a[rr], a[piv] = a[piv], a[rr]
        for i in range(len(a)):
            if i != rr and ((a[i] >> c) & 1):
                a[i] ^= a[rr]
        rr += 1
        if rr == len(a):
            break
    return tuple(sorted(a[:rr]))

def nullspace_basis(rows, nvars):
    a = [x for x in rows if x]
    rr = 0
    pivots = []
    for c in range(nvars):
        piv = next((i for i in range(rr, len(a)) if (a[i] >> c) & 1), None)
        if piv is None:
            continue
        a[rr], a[piv] = a[piv], a[rr]
        for i in range(len(a)):
            if i != rr and ((a[i] >> c) & 1):
                a[i] ^= a[rr]
        pivots.append(c)
        rr += 1
        if rr == len(a):
            break

    pset = set(pivots)
    free = [c for c in range(nvars) if c not in pset]
    out = []
    for f in free:
        x = 1 << f
        for i, p in enumerate(pivots):
            if (a[i] & x).bit_count() & 1:
                x |= 1 << p
        out.append(x)
    return out

class Builder:
    def __init__(self):
        self.left = []
        self.deg = []
        self.constraints = []
        self.outputs = []

    def new_left(self, name):
        i = len(self.left)
        self.left.append(name)
        self.deg.append(0)
        return i

    def _touch(self, tri):
        assert len(set(tri)) == 3
        for i in tri:
            self.deg[i] += 1
            assert self.deg[i] <= 3

    def add_constraint(self, tri):
        self._touch(tri)
        self.constraints.append(tuple(tri))

    def add_output(self, label, tri):
        self._touch(tri)
        self.outputs.append((label, tuple(tri)))

def random_generator(rank, n, rng):
    while True:
        rows = []
        while len(rows) < rank:
            x = rng.randrange(1, 1 << n)
            if gf2_rank(rows + [x]) > len(rows):
                rows.append(x)
        # no zero column = loopless target
        if all(any((row >> j) & 1 for row in rows) for j in range(n)):
            return rows

def build_parent(generator, nout, distinguished):
    rank = len(generator)

    columns = []
    for j in range(nout):
        c = 0
        for i, row in enumerate(generator):
            if (row >> j) & 1:
                c |= 1 << i
        assert c != 0
        columns.append(c)

    signal_names = []
    def new_signal(name):
        signal_names.append(name)
        return len(signal_names) - 1

    inputs = [new_signal(("input", i)) for i in range(rank)]
    gates = []
    finals = []

    # Independent XOR tree for every target coordinate.
    for j, mask in enumerate(columns):
        inds = [i for i in range(rank) if (mask >> i) & 1]
        cur = inputs[inds[0]]
        for q, ii in enumerate(inds[1:]):
            out = new_signal(("sum", j, q))
            gates.append((cur, inputs[ii], out))
            cur = out
        finals.append(cur)

    distinguished_signal = finals[distinguished]

    uses = defaultdict(list)
    gate_tokens = []
    for gi, gate in enumerate(gates):
        local = []
        for pos, sig in enumerate(gate):
            token = ("gate", gi, pos)
            uses[sig].append(token)
            local.append((sig, token))
        gate_tokens.append(local)

    output_tokens = {}
    for j, sig in enumerate(finals):
        if j == distinguished:
            continue
        local = []
        for q in range(3):
            token = ("output", j, q)
            uses[sig].append(token)
            local.append((sig, token))
        output_tokens[j] = local

    b = Builder()
    token_to_left = {}

    # Copies are even for every signal except the distinguished signal.
    for sig in range(len(signal_names)):
        local_uses = list(uses[sig])
        desired_parity = 1 if sig == distinguished_signal else 0
        q = len(local_uses)
        if q == 0:
            q = 1 if desired_parity else 2
        elif (q & 1) != desired_parity:
            q += 1

        copies = [b.new_left(("copy", sig, k)) for k in range(q)]
        for token, lid in zip(local_uses, copies):
            token_to_left[token] = lid

        # Parity-neutral equality chain:
        # a+u+v=0, b+u+v=0, u+v+w=0.
        for k in range(q - 1):
            a = copies[k]
            bb = copies[k + 1]
            u = b.new_left(("eq-u", sig, k))
            v = b.new_left(("eq-v", sig, k))
            w = b.new_left(("eq-w", sig, k))
            b.add_constraint((a, u, v))
            b.add_constraint((bb, u, v))
            b.add_constraint((u, v, w))

    for local in gate_tokens:
        b.add_constraint(tuple(token_to_left[token] for _, token in local))

    for j, local in output_tokens.items():
        b.add_output(j, tuple(token_to_left[token] for _, token in local))

    # Neutral contracted triples raise |L|-|R| without changing global parity.
    while len(b.left) - (len(b.constraints) + len(b.outputs)) < 3:
        tri = tuple(b.new_left(("dummy", len(b.constraints), q)) for q in range(3))
        b.add_constraint(tri)

    k = len(b.left) - (len(b.constraints) + len(b.outputs))
    assert k >= 3

    deficits = [3 - d for d in b.deg]
    assert sum(deficits) == 3 * k

    # Havel-Hakimi realization of left deficits against k deleted degree-3 nodes.
    deleted = []
    for _ in range(k):
        cand = sorted(
            (i for i, d in enumerate(deficits) if d > 0),
            key=lambda i: (-deficits[i], i),
        )
        assert len(cand) >= 3
        tri = tuple(cand[:3])
        deleted.append(tri)
        for i in tri:
            deficits[i] -= 1
            b.deg[i] += 1

    assert not any(deficits)
    assert all(d == 3 for d in b.deg)
    assert len(b.left) == len(b.constraints) + len(b.outputs) + len(deleted)

    return b, deleted

def minor_cocycle_space(builder, target_size, distinguished):
    nleft = len(builder.left)
    constraints = [
        sum(1 << i for i in tri)
        for tri in builder.constraints
    ]
    kernel = nullspace_basis(constraints, nleft)

    output = {j: tri for j, tri in builder.outputs}
    rows = []
    for y in kernel:
        word = 0

        # Parent all-ones column f becomes the distinguished target coordinate.
        if y.bit_count() & 1:
            word |= 1 << distinguished

        for j, tri in output.items():
            if sum((y >> i) & 1 for i in tri) & 1:
                word |= 1 << j

        rows.append(word)

    return rows

def explicit_controls():
    controls = [
        ([0b111, 0b101], 3, 0),
        ([0b1111, 0b1010, 0b1100], 4, 2),
        ([0b10111, 0b01101, 0b11001], 5, 4),
    ]
    for rows, n, p in controls:
        assert gf2_rank(rows) == len(rows)
        assert all(any((row >> j) & 1 for row in rows) for j in range(n))
        parent, deleted = build_parent(rows, n, p)
        got = minor_cocycle_space(parent, n, p)
        assert canonical_rowspace(rows) == canonical_rowspace(got)
        assert all(len(tri) == 3 for tri in parent.constraints)
        assert all(len(tri) == 3 for _, tri in parent.outputs)
        assert all(len(tri) == 3 for tri in deleted)

def randomized_controls():
    rng = random.Random(SEED)
    tested = 0
    max_parent = 0

    for n in range(3, 9):
        for rank in range(1, min(n, 4) + 1):
            for _ in range(20):
                rows = random_generator(rank, n, rng)
                p = rng.randrange(n)
                parent, _ = build_parent(rows, n, p)
                got = minor_cocycle_space(parent, n, p)
                assert canonical_rowspace(rows) == canonical_rowspace(got)
                max_parent = max(max_parent, len(parent.left))
                tested += 1

    return tested, max_parent

def main():
    explicit_controls()
    tested, max_parent = randomized_controls()

    print("PASS")
    print("EXPLICIT_CONTROLS = PASS")
    print("RANDOM_LOOPLESS_COCYCLE_SPACES =", tested)
    print("MAX_PARENT_ROWS =", max_parent)
    print("ROW_COLUMN_DEGREE_3 = PASS")
    print("DISTINGUISHED_F_ROUNDTRIP = PASS")
    print("CLAIM_CEILING = MINOR_IMAGE_ONLY; TORSO_PLACEMENT_AND_GLOBAL_OBJECTIVE_NOT_CLAIMED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
