# Source audit — one-edge-twist 2-lift trade-free nullity amplifier

Date: 2026-09-27

Audit id:
`PA-CANDIDATE-20260927-ONE-EDGE-TWIST-TRADEFREE-NULLITY-AMPLIFIER`

Authorized scope:
`R5_E9_DISSOCIATED_CUBIC_LINEAR_NULLITY_GATE_V1`

Decision:
`PASS_SCOPED_GAP_CONFIRMED`

Scientific boundary:
`P_VS_NP = OPEN`, `E8_D1 = EMPTY`.

## Internal anti-loop

Checked the current PR branch before adding a new theorem. Existing JANUS
artifacts already cover rational-kernel `2^k` routing, row-basis overlap-excess
routing, cubic binary-kernel support contraction, signed-trade donors and
polynomial boundary projection, the 9x9 trade-free unique-model countercontrol,
cubic-linear spectral nullity bounds, and universal-selector / witness-dominance
firewalls.

No existing artifact on the branch states or proves the exact combination

```text
single crossed incidence in a 2-lift
+ signed-trade-free base
=> signed-trade-free lift
+ rational nullity k' >= 2k-1
```

or its iterated linear-nullity consequence.

## External source check

### 2-lifts and signings

Y. Bilu and N. Linial,
*Lifts, Discrepancy and Nearly Optimal Spectral Gap*,
Combinatorica 26(5), 495--519 (2006),
DOI `10.1007/s00493-006-0029-7`.

Source-bound facts used: 2-lifts are encoded by edge signings; the lift splits
into old/base and new/signed sectors.

### Connectivity and signed balance

F. Martin,
*Frustration and isoperimetric inequalities for signed graphs*,
Discrete Applied Mathematics 217 (2017), 276--285,
DOI `10.1016/j.dam.2016.09.015`.

Source-bound facts used: standard 2-lift block form; equivalence between
signings and 2-lifts; for a connected base, balance/unbalance controls whether
the associated 2-lift splits into two components or is connected.

### Trades / null 3-hypergraphs

W. Kocay and P. C. Li,
*On 3-Hypergraphs with Equal Degree Sequences*,
Ars Combinatoria 82 (2007), 145--157.

Source-bound facts used: trades / null 3-hypergraphs are signed degree-zero
structures; trade language is not JANUS novelty.

## Scoped JANUS-derived delta

The candidate theorem specializes these source-bound tools to a square
row/column-weight-three incidence matrix and uses the elementary divisibility
argument at one crossed incidence:

```text
Ap = d e_i
1^T A = 3 1^T
d in {-2,-1,0,1,2}
=> 3 sum(p) = d
=> d=0.
```

This proves preservation of signed-trade-freeness.

The rational nullity lower bound comes from the signed block

```text
S=A-2 e_i e_j^T
```

and the codimension-at-most-one subspace

```text
ker(A) intersect {x_j=0} subseteq ker(S).
```

Iteration from the exact 18x18 seed yields a connected cubic-linear SAT
unique-model signed-trade-free family with

```text
n_t = 18*2^t
nu_Q(A_t) >= n_t/18 + 1.
```

This falsifies the previously open Route-A hypothesis
`trade-free => O(log n) rational nullity`.

## Novelty firewall

No claim is made that graph 2-lifts, signed-graph balance, trades/null
hypergraphs, rank-one perturbations, or kernel dimension arguments are new.
A checked-source search did not locate the exact one-edge-twist
trade-free-preservation plus nullity-amplification theorem. This is a scoped
anti-duplication statement, not a world-priority claim.

## Promotion ceiling

This result does not solve the trade-free high-nullity family. It shows that
the low-nullity shortcut is unavailable.

```text
ROUTE_A_TRADE_FREE_O_LOG_N = FALSIFIED
TRADE_FREE_HIGH_NULLITY_CONTRACTION = OPEN
TRADE_RICH_MIXED_CARRIER_CLOSURE = OPEN
UNIVERSAL_SAT_SOLVER = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
