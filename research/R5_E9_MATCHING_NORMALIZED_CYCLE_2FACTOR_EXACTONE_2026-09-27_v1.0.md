# R5 E9 — Matching-Normalized Cycle-2-Factor Exact-One Form

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_NORMAL_FORM__UNIVERSAL_ON_LINEAR_CUBIC_CARRIER__NO_D1_PROMOTION`

Scientific ceiling:

```text
LINEAR CUBIC POSITIVE 1-IN-3 = NP-COMPLETE (companion EQ3 regularization theorem).
THIS NOTE IS AN EXACT REPRESENTATION CHANGE, NOT YET A POLYNOMIAL DECIDER.
P_VS_NP = OPEN.
```

## 1. Setup

Let `L=(R,C,E)` be the Levi graph of a square linear cubic Positive 1-in-3 instance. Thus `L` is bipartite, every vertex has degree three, and girth is at least six.

A perfect matching `M` exists in every cubic bipartite graph and is constructible in polynomial time. Index each matched row/column pair by one common index `i`. The matching incidences become the identity matching.

The complement `E\M` is 2-regular bipartite, hence a disjoint union of even cycles. Alternating each component yields two additional perfect matchings. Therefore, after relabelling,

```text
A = I + P + Q
```

with permutation matrices `P,Q` and pairwise disjoint supports in every row.

Write

```text
p(i) = column used by P in row i,
q(i) = column used by Q in row i.
```

Row `i` is the triple

```text
{i, p(i), q(i)}.
```

## 2. The cycle graph induced by the normalization

Define an undirected graph `C_M` on the column/variable indices by putting one edge

```text
e_i = {p(i), q(i)}
```

for every row `i`.

### Lemma C2F-1 — `C_M` is a simple 2-factor

Every variable/column `v` occurs once as a `P` image and once as a `Q` image, because `P,Q` are permutations. Hence `v` has degree exactly two in `C_M`.

No edge is a loop because row supports have three distinct variables. Two different rows cannot induce the same unordered pair `{u,v}`: otherwise those two source rows would share both `u` and `v`, contradicting linearity.

Therefore `C_M` is a simple 2-regular graph, i.e. a disjoint union of simple cycles.

Construction is polynomial after the perfect matching / 1-factorization.

## 3. One-row identity

For one source row with variables `(m,u,v)`, Exact-One is

```text
m+u+v = 1 over the integers.
```

For Boolean variables, this is equivalent to the conjunction

```text
m XOR u XOR v = 1,
NOT(u AND v).
```

Proof: the odd-parity assignments are exactly `100,010,001,111`; the binary NAND removes precisely `111`.

Under the normalization, `m=i` and `{u,v}=e_i`.

## 4. Main theorem

### Theorem C2F-2 — affine parity plus cycle independence

For every Boolean vector `x`,

```text
A x = 1 over the integers
```

if and only if

```text
A x = 1 (mod 2)
AND
supp(x) is an independent set of C_M.
```

### Proof

Apply the one-row identity to every row `i`. The parity parts are exactly `Ax=1 mod 2`. The NAND part in row `i` is exactly

```text
not(x_{p(i)}=x_{q(i)}=1),
```

which is the stable-set edge inequality for edge `e_i` of `C_M`. The set of all such `e_i` is exactly the edge set of the cycle 2-factor. Hence all NAND conditions hold exactly when `supp(x)` is independent in `C_M`. QED.

Thus the entire NP-complete linear cubic carrier admits the exact form

```text
AFFINE F2 COSET
INTERSECT
INDEPENDENT SETS OF A DISJOINT UNION OF CYCLES.
```

## 5. Equivalent edge-labelled cycle form

The rows give a bijection

```text
f : V(C_M) -> E(C_M),
f(i)=e_i,
```

because both sets have cardinality `n`.

For an independent set `S`, row `i` is Exact-One exactly when

```text
i in S
iff
neither endpoint of f(i) lies in S.
```

Equivalently,

```text
x_i = NOR(x_u,x_v)
```

for `f(i)={u,v}`, together with the global condition that `S` is independent in `C_M`.

The independence condition must not be dropped: `NOR` alone permits both endpoints of `f(i)` to be one and is therefore only ordinary digraph-kernel semantics, not Exact-One.

## 6. Counting consequence

If `S` is an Exact-One witness then each selected vertex of `C_M` touches two distinct cycle edges and, since `S` is independent, these `2|S|` incident edges are all distinct.

The remaining `n-2|S|` cycle edges have both endpoints outside `S`. By the edge-labelled condition these are exactly the edges `f(i)` with `i in S`. Since `f` is a bijection,

```text
|S| = n-2|S|,
```

so

```text
|S| = n/3.
```

This independently recovers the affine-coset minimum-weight theorem on the exact slice.

## 7. Algorithmic interpretation

A single cycle has a width-2 independent-set automaton. Hence the only possible exponential obstruction in this normal form is not local cycle feasibility; it is the global affine coupling induced by `Ax=1 mod 2` / the edge-label bijection `f`.

This sharply forbids two false shortcuts:

```text
cycle 2-factor => ordinary cycle DP solves the source     [FALSE without carrying affine syndrome]
Gaussian elimination => solves the source                 [FALSE without cycle independence]
```

A genuine polynomial algorithm must compress the affine syndrome carried through the cycle automata to polynomial total state, or find an equivalent global construction that avoids syndrome enumeration.

## 8. Relation to the final P=NP contract

The companion constant-factor EQ3 regularization proves that the source class of this theorem is NP-complete. Therefore a deterministic polynomial algorithm for

```text
AFFINE_CYCLE_2FACTOR_INTERSECTION
```

on these source-generated `(A,C_M,f)` instances, with witness reconstruction, is already sufficient to conclude `P=NP`.

This is not a side-class gate.

## 9. Checker

Executable regression:

`experiments/r5_e9_matching_normalized_cycle_2factor.py`

It checks on frozen Fano / 9_3 SAT / 10_3 UNSAT controls that:

- the unmatched-pair graph is a simple 2-factor;
- Exact-One is pointwise equivalent to parity plus cycle independence for every Boolean assignment;
- source witness counts agree exactly in both representations.

## 10. Ceiling

```text
MATCHING NORMALIZATION A=I+P+Q                = POLYNOMIAL
UNMATCHED-PAIR GRAPH C_M                      = SIMPLE CYCLE 2-FACTOR
EXACT-ONE                                     = AFFINE PARITY + C_M INDEPENDENCE
LOCAL NONLINEAR CONSTRAINT GRAPH              = DISJOINT CYCLES
GLOBAL AFFINE-SYNDROME COMPRESSION             = OPEN
UNIVERSAL POLYNOMIAL DECIDER                  = NOT YET PROVED
P_VS_NP                                       = OPEN
```
