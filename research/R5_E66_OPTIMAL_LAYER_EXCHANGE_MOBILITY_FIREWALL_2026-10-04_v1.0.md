# R5 E66 — Optimal-Layer Exchange Mobility Firewall

Date: 2026-10-04

Status:
`POST_QUOTIENT_OPTIMAL_LAYER_CAN_BE_HIGHLY_CONNECTED_WHILE_UNSAT__DEFECT_CENTER_IS_GLOBALLY_MOBILE_BUT_NONANNIHILATING__BINARY_KERNEL_WEIGHT_ENUMERATOR_IS_ORIENTATION_SENSITIVE`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

IT TESTS THE E65 HOPE THAT THE EXCHANGE STRUCTURE OF MINIMUM PARITY
REPRESENTATIVES MIGHT DISTINGUISH SAT FROM UNSAT.

THE SIMPLE VERSION OF THAT HOPE IS FALSE.

ON THE UNSAT TUTTE-12 ORIENTATION THE COMPLETE MINIMUM PARITY LAYER HAS
252 REPRESENTATIVES AND IS ALREADY CONNECTED BY THE SMALLEST POSSIBLE
LAYER-PRESERVING KERNEL EXCHANGES.

THE UNIQUE THREE-ROW DEFECT STAR CAN BE MOVED THROUGH ALL 63 POSSIBLE
CENTERS BY SUCH NEUTRAL EXCHANGES, YET IT CAN NEVER BE ANNIHILATED.

THE TRANSPOSE SAT ORIENTATION ALSO HAS A CONNECTED REGULAR OPTIMAL-LAYER
EXCHANGE GRAPH.

THEREFORE CONNECTIVITY, REGULARITY, AND GLOBAL DEFECT MOBILITY DO NOT
DECIDE EXACT-ONE.

P_VS_NP = OPEN.
```

## 1. Carrier and parity-code viewpoint

Let `R` be the `63 x 63` Tutte-12 incidence matrix frozen in E64-E65 and let
`R^T` be its transpose.

E65 proved

```text
R   : Exact-One UNSAT,
R^T : Exact-One SAT,
```

while both have rational nullity `14` and binary nullity `14`.

For every square cubic binary matrix `A`, binary parity solutions satisfy

```text
A x = 1 mod 2.
```

Because every row has odd weight three,

```text
A 1 = 1 mod 2,
```

so every parity solution has the form

```text
x = 1 + k,
k in K_2(A) := ker_F2(A).
```

Hence

```text
|x| = n - |k|.
```

For `n=63`, E58/E65 imply

```text
Exact-One SAT
iff max_{k in K_2(A)} |k| = 42.
```

If the minimum parity defect is `m`, then

```text
min |x| = 21 + 2m,
max |k| = 42 - 2m.
```

Thus the E65 defect problem is exactly the top-shell problem of the binary
kernel code.

## 2. Exact orientation-sensitive kernel weight enumerators

The E66 checker enumerates all `2^14 = 16384` binary kernel words in both
orientations.

For the UNSAT orientation:

```text
W_R(z) =
    1
  + 126 z^16
  + 1596 z^24
  + 2880 z^28
  + 7497 z^32
  + 4032 z^36
  + 252 z^40.
```

In particular,

```text
max weight = 40,
```

so the minimum parity layer has weight

```text
63 - 40 = 23 = 21 + 2.
```

For the SAT transpose orientation:

```text
W_{R^T}(z) =
    1
  + 36 z^14
  + 56 z^18
  + 252 z^20
  + 378 z^24
  + 1764 z^26
  + 1800 z^28
  + 1764 z^30
  + 3591 z^32
  + 4032 z^34
  + 2044 z^36
  + 504 z^38
  + 126 z^40
  + 36 z^42.
```

The 36 weight-42 kernel words are exactly the 36 E65 Exact-One solutions under
`x = 1 + k`.

This supplies an orientation-sensitive invariant that the transpose firewall of
E65 does not kill.  It does **not** supply a polynomial algorithm: computing
extremal codeword weights is itself a hard problem for general binary linear
codes.

## 3. External anti-loop anchor from coding theory

Berlekamp, McEliece and van Tilborg proved that the general decoding problem for
linear codes and the general problem of finding codeword weights are
NP-complete:

* E. R. Berlekamp, R. J. McEliece, H. C. A. van Tilborg,
  "On the inherent intractability of certain coding problems",
  IEEE Transactions on Information Theory 24(3), 384-386 (1978),
  DOI 10.1109/TIT.1978.1055873.

This does not settle our much more structured square-cubic-linear incidence
codes.  It is an anti-loop warning: simply renaming the frontier as a code
maximum-weight problem is not a polynomial solution.

A second external consistency anchor comes from the finite-geometry code
literature for `H(2)` and its dual, where orientation-dependent binary codes of
dimension 14 and different minimum-weight structures are explicitly reported.
Again, E66 does not rely on those classifications; the companion checker builds
and enumerates the code directly.

## 4. Optimal-layer pair-distance distributions

Let the top kernel shell of `R` be

```text
T_R = {k in K_2(R) : |k|=40}.
```

It has 252 elements.  Equivalently, the associated parity representatives
`x=1+k` are exactly the 252 E65 minima of weight 23.

For unordered pairs in `T_R`, E66 obtains the complete symmetric-difference
weight distribution

```text
16 : 2268 pairs,
24 : 8064 pairs,
28 : 4032 pairs,
32 : 11214 pairs,
36 : 4032 pairs,
40 : 2016 pairs.
```

The smallest layer-preserving exchange therefore has kernel weight `16`.
Define the minimum-exchange graph `X_R` by

```text
vertices = T_R,
k ~ k' iff |k+k'| = 16.
```

Then

```text
|V(X_R)| = 252,
|E(X_R)| = 2268,
degree    = 18,
X_R       = connected.
```

So the UNSAT optimum layer is not fragmented into isolated local minima.

## 5. The defect-center fibers

E65 proved that every minimum parity representative of the UNSAT orientation
has exactly three triple-covered rows and that those rows are exactly the
support of one selected column.

Call that unique column the `defect center`.

Across the 252 minima:

```text
63 centers occur,
4 minima occur over each center.
```

Thus the minimum layer splits into fibers

```text
F_c, |F_c|=4,
c in {0,...,62}.
```

E66 proves that the subgraph of `X_R` induced by every `F_c` is exactly a
4-cycle:

```text
X_R[F_c] = C4.
```

So even at a fixed defect star there are nontrivial neutral exchanges.

## 6. Global motion of the defect center

Build the column-conflict graph `G` of `R`: two selectable columns are adjacent
when they occur in a common Exact-One row.

Because the carrier is linear and cubic, `G` is simple 6-regular.

For every minimum-exchange edge joining two different defect fibers, E66 finds

```text
d_G(c,c') = 3.
```

No cross-fiber weight-16 exchange occurs at any other center distance.

Conversely, **every** pair of centers at conflict distance 3 is represented by
cross-fiber exchanges, and exactly two lifted exchange edges join the two
four-vertex fibers.

Define the center-mobility graph

```text
M:
V(M)=columns(R),
c~c' iff d_G(c,c')=3.
```

The checker obtains exactly

```text
M = SRG(63,32,16,16),
M is connected.
```

There are

```text
1008
```

adjacent center pairs and each carries exactly two lifted minimum-exchange
edges, giving

```text
2016
```

cross-fiber edges, plus

```text
63 * 4 = 252
```

within-fiber C4 edges, for the total

```text
2268.
```

This is the main E66 firewall:

```text
boxed:
the unique minimal defect is globally mobile through all 63 centers by
neutral minimum exchanges, but it cannot be annihilated.
```

Mobility is not repairability.

## 7. SAT transpose optimal layer

For `R^T`, the top kernel shell has exactly 36 words of weight 42, corresponding
to the 36 Exact-One solutions.

Their pairwise symmetric-difference weights are

```text
24 : 378 pairs,
36 : 252 pairs.
```

Define `X_{R^T}` using the smallest layer-preserving exchange, weight 24.
The checker proves

```text
X_{R^T} = SRG(36,21,12,12),
X_{R^T} is connected.
```

Thus both sides of the transpose SAT/UNSAT pair have highly organized,
connected, regular optimal-layer exchange geometries.

Therefore the following candidate criteria are all insufficient:

```text
optimal-layer connectivity,
existence of many neutral exchanges,
regularity of the exchange graph,
global mobility of a localized defect,
small exchange diameter as a qualitative notion.
```

## 8. What survives E66

The exact decision statement remains

```text
Exact-One SAT
iff
max_{k in ker_F2(R)} |k| = 2n/3.
```

E66 adds two constraints on any useful next invariant:

```text
1. it must be orientation-sensitive;
2. it must detect defect annihilation, not merely defect mobility inside an
   already optimal shell.
```

A useful E67 target is therefore not another connectivity statistic.  It should
attempt a **certificate for the top-shell ceiling**:

```text
UNSAT: prove max |k| <= 2n/3 - 2,
SAT  : construct k with |k| = 2n/3.
```

For the Tutte-12 pair this means explaining algebraically, without exhaustive
`2^14` enumeration, why

```text
R   : max |k| = 40,
R^T : max |k| = 42.
```

Candidate tools include orientation-sensitive linear/semidefinite relaxations,
Delsarte-type inequalities, dual-code constraints, and finite-geometry
intersection numbers.  Any proposed method must then be attacked on the frozen
E12/RXC3 quotient family before being considered universal.

## 9. Replay

Companion checker:

```text
experiments/r5_e66_optimal_layer_exchange_mobility_firewall.py
```

It independently verifies:

```text
* both complete 2^14 binary kernel enumerations;
* both exact kernel weight enumerators;
* top-shell sizes 252 and 36;
* complete top-shell pair-distance distributions;
* connected regular minimum-exchange graphs;
* 63 defect-center fibers of size 4;
* C4 inside every UNSAT fiber;
* distance-3 characterization of all cross-fiber exchanges;
* SRG(63,32,16,16) center-mobility graph;
* exactly two lifted edges per adjacent center pair;
* SRG(36,21,12,12) SAT exact-exchange graph.
```

Scientific status remains:

```text
P_VS_NP = OPEN.
```
