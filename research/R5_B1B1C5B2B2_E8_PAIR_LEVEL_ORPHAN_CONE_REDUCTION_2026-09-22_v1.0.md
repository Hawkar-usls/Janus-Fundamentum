# R5 E8 — Pair-Level Orphan Cone Reduction Lemma

Date: 2026-09-22

Authority: `SCOPED_SYMBOLIC_REDUCTION__NO_D1_PROMOTION`

Parent gate: `research/R5_B1B1C5B2B2_E8_ORPHAN_PAYLOAD_BARRIER_GATE_2026-09-22_v1.0.json`

## Pair-level tree

For `m=2^r`, group the frozen selector blocks into `n=m/2` adjacent pair positions:

```text
H_q = AND(G_{2q-1},G_{2q})
```

with zero/one-based indexing translated canonically by the executor.

Let `P` be the set of pair positions whose odd selector has already been projected.

For every dyadic interval `I` of pair positions, define:

```text
p(I) = |P intersect I|.
```

## Exact interval multiplicity

After an arbitrary odd-only projection history, the frozen structural block tree contains exactly

```text
2^{p(I)}
```

live structural instances of interval `I`.

Proof is by induction on the complete pair tree:

- at a pair leaf, an unresolved odd selector gives one pair ref and a projected odd selector gives its two branch refs;
- at an internal interval, child refs encode exactly the assignments to projected odd selectors in the two child intervals;
- branch injectivity makes distinct assignments yield distinct child-ref pairs;
- CONST / IDEMPOTENCE / COMPLEMENT do not collapse these interval roots in the odd-prefix regime.

Hence the number of instances multiplies:

```text
2^{p(left)} * 2^{p(right)} = 2^{p(I)}.
```

## Weighted ancestor-union function

For a set `T` of pair positions define:

```text
W_P(T)
=
sum over all dyadic intervals I intersecting T
of 2^{p(I)},
```

where pair leaves themselves are included as size-1 dyadic intervals.

## Common Shannon backbone

Every unresolved odd selector occurs in every restricted branch root.

Every payload also occurs in every restricted branch root because its two even support blocks remain unresolved throughout an odd-only prefix.

Therefore every pre-existing Shannon-OR backbone node depends on every candidate compared by the scheduler.

Let its common cone contribution be `C_Shannon(S)`.

This term is identical for all unresolved odd selectors and payloads and cancels from cone comparisons.

## Exact unresolved-odd cone formula

Let unresolved odd selector `o` occupy pair position `q`.

Below the pair root it has exactly:

```text
4 selector-dependent 3-clause gates
+ 1 selector block gate
= 5 nodes.
```

At pair level and above, every structural instance of every dyadic ancestor interval containing `q` depends on `o`, and no other interval instance does.

Therefore:

```text
A_o
=
C_Shannon(S)
+ 5
+ W_P({q}).
```

This is exact.

Consequently the minimum odd cone is:

```text
min_odd A_o
=
C_Shannon(S)
+ 5
+ min_{q notin P} W_P({q}).
```

## Orphan payload lower decomposition

For orphan payload `z`, let `E_z` be the two pair positions containing its two unresolved even support blocks.

Because each even support block remains unresolved, every structural instance of every dyadic interval intersecting `E_z` depends on `z`.

Thus all nodes counted by `W_P(E_z)` belong to `Cone(z)`.

Define the residual/local contribution:

```text
L_z
=
A_z
- C_Shannon(S)
- W_P(E_z).
```

It contains all z-dependent structure below the counted even-support pair roots plus any additional z-dependent structure created by the two projected odd supports that is not already counted by `W_P(E_z)`.

Uniform lower bound:

```text
L_z >= 5.
```

Reason:

- the two unresolved even support blocks contribute at least one z-dependent clause gate plus their block gate each: at least 4 distinct nodes;
- at least one reachable projected-odd residual clause containing z contributes one further z-dependent node;
- any structural sharing can only identify additional residual nodes, not these four even-support local obligations with the residual class.

Hence:

```text
A_z
>=
C_Shannon(S)
+ L_z
+ W_P(E_z),

with `L_z>=5`.

## Exact reduced orphan target

The already-proved orphan savings cap reduces the scheduler barrier to:

```text
A_z - A_o >= 4
```

for some unresolved odd selector `o`.

Using the exact odd formula and the payload decomposition, it is sufficient to prove:

```text
R5_E8_ORPHAN_DYADIC_LOCAL_INEQUALITY_V1

L_z + W_P(E_z)
>=
min_{q notin P} W_P({q}) + 9.
```

Indeed then:

```text
A_z
>=
C_Shannon + minW + 9

while

min_odd A_o
=
C_Shannon + minW + 5,

so

A_z - min_odd A_o >= 4.
```

## Finite controls

For all 41 exact odd-only histories with an unresolved odd selector at `m=8`, the reduced inequality holds.

Random/greedy `m=16` diagnostics also show no violation. These are diagnostic only.

The observed minimum decomposition at `m=8` reaches equality:

```text
L_z = 7
W_P(E_z) - minW = 2

=>
L_z + W_P(E_z) - minW = 9.
```

This shows the constant 9 is tight for the current reduction.

## Remaining theorem

```text
ORPHAN_PAYLOAD_BARRIER
has been reduced to
ORPHAN_DYADIC_LOCAL_INEQUALITY.
```

No full projected DAG size, Shannon-backbone size, or semantic equivalence reasoning is needed.

## Claim ceiling

```text
PAIR_INTERVAL_MULTIPLICITY
=
PROVED

UNRESOLVED_ODD_CONE_FORMULA
=
PROVED

ORPHAN_LOCAL_FLOOR_Lz_GE_5
=
PROVED

ORPHAN_DYADIC_LOCAL_INEQUALITY
=
OPEN

ORPHAN_PAYLOAD_BARRIER
=
OPEN

P_VS_NP
=
OPEN
```
