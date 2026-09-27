# R5 E9 — Two-Step Boben Adjacent Semantic State-4 Barrier

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_TWO_STEP_BARRIER__3_STATE_A_REDUCTION_LIFT_NOT_CLOSED`

Parents:
- `R5_E9_BOBEN_REDUCTION_EXACTONE_SEMANTIC_AUDIT_2026-09-27_v1.0.md`
- `R5_E9_BOBEN_LOCAL_BOND_DIMENSION_BARRIER_2026-09-27_v1.0.md`
- `R5_E9_A_IRREDUCIBLE_BOUNDED_WIDTH_TERMINAL_2026-09-27_v1.0.md`

Scientific ceiling:

```text
THIS KILLS ONLY THE CONSTANT THREE-STATE EDGE-LIFT SHORTCUT.
IT DOES NOT RULE OUT A FOUR-STATE OR POLYNOMIAL CORRELATION ALGEBRA.
IT DOES NOT PROVE P != NP.
P_VS_NP = OPEN.
```

## 1. Alternating two-step region

Consider four alternating Levi vertices

```text
P1 - L1 - P2 - L2
```

where `P` vertices carry `EQ3` and `L` vertices carry `EXACT1_3`.

Let the three internal incidence bits along the path be `s,t,u`.
Let the six external boundary bits be

```text
P-side: a,b,d
L-side: c,e,f
```

with local constraints

```text
EQ3(a,b,s)
EXACT1_3(s,t,c)
EQ3(t,u,d)
EXACT1_3(u,e,f).
```

Eliminating `s,t,u` gives the exact six-boundary relation `R2`.

Its satisfying tuples, in coordinate order `(a,b,c,d,e,f)`, are exactly

```text
(0,0,0,1,0,0)
(0,0,1,0,0,1)
(0,0,1,0,1,0)
(1,1,0,0,0,1)
(1,1,0,0,1,0).
```

Thus the two-step region already carries a five-tuple correlation rather than a one-step three-tuple partial permutation.

## 2. Pairing into the three structural reconnection edges

After two structural adjacent reductions, the remaining boundary consists of three point-side and three line-side incidences. Any structural reconnection pairs these shores by a perfect matching.

For any permutation `pi in S_3`, define three paired edge symbols

```text
z_i = (p_i, q_{pi(i)}) in {00,01,10,11},
```

where

```text
(p_1,p_2,p_3)=(a,b,d),
(q_1,q_2,q_3)=(c,e,f).
```

For each such pairing, view the resulting ternary relation on `(z_1,z_2,z_3)` and flatten one paired edge against the other two.

Exact enumeration gives the following ordinary ranks of the three `1 | 2` flattenings:

```text
pi=(0,1,2): 3,4,3
pi=(0,2,1): 3,4,3
pi=(1,0,2): 4,3,3
pi=(1,2,0): 4,4,3
pi=(2,0,1): 4,3,3
pi=(2,1,0): 4,4,3
```

Hence:

### Theorem B2S-1

For every perfect matching of the three point-side ports to the three line-side ports, at least one paired structural edge has flattening rank four against the remaining two edges.

The same lower bound holds for Boolean relational factorization: in every rank-four flattening the four nonzero rows have pairwise disjoint supports, so its Boolean rank is also four.

Therefore no exact semantic representation in which every structural reconnection edge carries at most three hidden states and all cross-boundary correlation factors through that edge can represent this two-step region.

Equivalently:

```text
ONE A-STEP: 3 states suffice locally.
TWO LEGAL A-STEPS: a universal 3-state per-edge lift is already insufficient.
```

## 3. This topology occurs in an actual legal Boben sequence

Use the frozen connected linear cubic `10_3` UNSAT control from the semantic audit:

```text
{0,3,5}
{0,1,2}
{2,4,7}
{2,3,6}
{0,4,9}
{1,4,5}
{6,7,9}
{3,7,8}
{1,6,8}
{5,8,9}
```

There is a legal adjacent A-reduction sequence:

First step:

```text
remove row 9 and column 9;
remaining row-9 columns = {5,8};
remaining column-9 rows = {4,6};
reconnect row 4 -> column 8,
          row 6 -> column 5.
```

The reduced graph remains connected, cubic and linear.

Second step:

```text
remove the surviving image of row 8 and column 8
using the opposite legal pairing.
```

The second reduced graph again remains connected, cubic and linear.

Thus the alternating four-vertex topology above is not a synthetic forbidden pattern: it occurs inside an explicit source-valid consecutive A->A reduction sequence.

## 4. Consequence for the Boben universal route

The tempting induction

```text
one adjacent contraction has a 3-state partial permutation
=> every adjacent contraction can use the same 3-state edge alphabet
```

is false.

The mandatory structural path remains valuable:

```text
repeated A-reduction
-> A-irreducible bounded-width terminal
-> polynomial terminal DP.
```

But its semantic lift must now carry either:

1. at least four states on some reconnection edge;
2. explicit multi-edge correlation factors;
3. another exact canonical representation whose total construction/evaluation cost is proved polynomial.

Merely storing the one-step three-state partial permutation is forbidden.

Freeze the sharper gate:

```text
R5_E9_A_REDUCTION_POLYNOMIAL_CORRELATION_ALGEBRA_GATE_V1
```

A PASS must prove closure and polynomial evaluation/reconstruction for arbitrary legal A-reduction sequences, not just bounded local alphabet on one step.

## 5. Ceiling

```text
ONE-STEP ADJACENT MIN STATE
= 3

TWO-STEP EXACT RELATION
= 5 tuples

EVERY THREE-EDGE PAIRING
HAS A 1|2 FLATTENING OF RANK 4
= PROVED

UNIFORM 3-STATE PER-EDGE A-LIFT
= FALSIFIED

LEGAL SOURCE-VALID TWO-STEP WITNESS
= EXPLICIT

FOUR-STATE / POLYNOMIAL CORRELATION ALGEBRA
= OPEN

A-IRREDUCIBLE TERMINAL
= POLYNOMIAL

UNIVERSAL POLYNOMIAL DECIDER
= NOT YET PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
