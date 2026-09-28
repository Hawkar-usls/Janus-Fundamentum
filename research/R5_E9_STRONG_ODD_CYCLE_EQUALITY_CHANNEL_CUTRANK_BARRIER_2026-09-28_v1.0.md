# R5 E9 — Strong Odd-Cycle Equality-Channel Cut-Rank Barrier

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_REPRESENTATION_BARRIER__LOCAL_BOND2_NOT_GLOBAL_SMALL_STATE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_STRONG_ODD_CYCLE_DET2_TRANSFER_NORMAL_FORM_2026-09-28_v1.0.md`
- `research/R5_E9_ODD_HOLE_FULL_BOUNDARY_DELTA_MATROID_BARRIER_2026-09-26_v1.0.md`

Scientific ceiling:

```text
THIS RULES OUT ONLY A WIDTH-INDEPENDENT SINGLE-SUMMARY-STATE
INTERPRETATION OF THE STRONG-ODD-CYCLE BOND-2 TRANSFER FORM.

IT DOES NOT RULE OUT POLYNOMIAL-SIZE NETWORK REPRESENTATIONS,
GOOD DECOMPOSITIONS, OR A DIFFERENT GLOBAL ALGORITHM.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. The k=3 strong-cycle belt relation

For a strong odd cycle of order `k=3`, write the three cycle variables as
`v0,v1,v2` and the three belt variables as `w0,w1,w2`:

```text
v0 + v1 + w0 = 1
v1 + v2 + w1 = 1
v2 + v0 + w2 = 1
```

with all variables Boolean.

The Exact-One solutions in the `v` coordinates are exactly

```text
000, 100, 010, 001.
```

Their corresponding belt tuples are

```text
111, 010, 001, 100.
```

Hence the exact projected belt relation is

```text
R_belt^3(w0,w1,w2)
iff
w0 XOR w1 XOR w2 = 1.
```

This is also the `k=3` specialization of the already-proved det-2 transfer normal form.

## 2. Pinning one belt port gives an equality channel

Pin

```text
w2 = 1.
```

Then

```text
w0 XOR w1 = 0,
```

so

```text
R_belt^3(w0,w1,1)
iff
w0 = w1.
```

The full third-occurrence boundary does not obstruct this projection: for every feasible cycle assignment, each equation

```text
v_i + a_i + b_i = 1
```

has at least one Boolean extension in `(a_i,b_i)` (two extensions if `v_i=0`, one if `v_i=1`). Therefore existentially projecting the full source-valid strong-cycle boundary to `(w0,w1,w2)` gives exactly the belt relation above.

Thus one strong 6-cycle transfer block can realize an exact Boolean equality channel after one boundary pin and existential projection of the remaining third-occurrence ports.

## 3. m independent blocks give the identity relation on 2^m states

Take `m` disjoint copies of the pinned `k=3` transfer block. Denote the two free belt ports of block `i` by

```text
x_i, y_i.
```

The exact composed boundary relation is

```text
R_m(x,y)
iff
for every i, x_i = y_i.
```

Equivalently,

```text
R_m = { (x,x) : x in {0,1}^m }.
```

Order left boundary assignments `x` and right boundary assignments `y` lexicographically and form the `2^m x 2^m` communication matrix

```text
M_m[x,y] = 1 iff R_m(x,y).
```

Then

```text
M_m = I_(2^m).
```

Therefore over every field,

```text
rank(M_m) = 2^m.
```

The Boolean rank is also exactly `2^m`: the 1-entries of an identity matrix are pairwise incompatible with any rectangle containing two diagonal entries, because such a rectangle would also contain an off-diagonal 0-entry. Thus every Boolean rectangle cover needs one rectangle per diagonal 1.

## 4. Consequence for a single global summary state

Consider any exact factorization across the cut of the form

```text
R_m(x,y)
=
exists s in S_m:
    L(x,s) AND U(s,y).
```

Each hidden state `s` contributes one Boolean rectangle to the communication matrix. Since Boolean rank is `2^m`, necessarily

```text
|S_m| >= 2^m.
```

Likewise, for any weighted linear/tensor factorization

```text
M_m = A B
```

through an intermediate vector space of dimension `d`, ordinary rank gives

```text
d >= 2^m.
```

Hence a local bond dimension two for each individual strong cycle does **not** imply that an arbitrary collection of such channels admits one width-independent polynomial-size aggregate state across a wide cut.

## 5. What remains allowed

The theorem does **not** say that the product of `m` equality channels requires exponential description size. It has an `O(m)` factor-graph description using `m` separate two-state wires.

The barrier is specifically against the shortcut

```text
local bond dimension = 2
=> arbitrary global region has O(1) or poly(m) single-summary state
=> polynomial solver.
```

That implication is false.

A valid continuation must instead prove one of:

1. a polynomially discoverable decomposition whose active frontier remains `O(log n)` or otherwise polynomially evaluable;
2. an algebra allowing many independent wires to be manipulated without enumerating their Cartesian product;
3. a different global invariant/contraction with a strict progress theorem;
4. another exact polynomial terminal.

## 6. Relation to the historical equality-channel control

The historical JANUS anti-loop inventory already records independent equality channels as a family with `2^m` continuation-distinguishable states across a bad cut. The theorem above binds that abstract control directly to the newly derived strong-odd-cycle transfer language: the equality channel is already a pinned minor of the smallest strong odd-cycle belt relation.

Therefore the strong-odd-cycle transfer route does not escape the old fixed-cut semantic-state barrier merely by using a two-state local transfer matrix.

## 7. Checker

Executable regression:

`experiments/r5_e9_strong_odd_cycle_equality_channel_cutrank.py`

It verifies exactly:

- the `k=3` projected belt relation;
- pinning `w2=1` yields equality;
- for `m=1,...,8`, the composed communication matrix is identity;
- ordinary rank is `2^m`;
- the identity relation has one isolated 1-entry per row/column, giving Boolean rank `2^m`.

Finite replay is only a regression control; the arbitrary-`m` proof is Sections 1–4.

## 8. Ceiling

```text
K=3 STRONG-CYCLE BELT
= ODD PARITY

PINNED K=3 BELT
= EQ2

M INDEPENDENT PINNED BLOCKS
= IDENTITY RELATION ON 2^M ASSIGNMENTS

ORDINARY CUT RANK
= 2^M

BOOLEAN CUT RANK
= 2^M

WIDTH-INDEPENDENT SINGLE-SUMMARY BOND-2 CLOSURE
= FALSIFIED

POLYNOMIAL NETWORK / GOOD-DECOMPOSITION ROUTES
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY
P_VS_NP
= OPEN
```