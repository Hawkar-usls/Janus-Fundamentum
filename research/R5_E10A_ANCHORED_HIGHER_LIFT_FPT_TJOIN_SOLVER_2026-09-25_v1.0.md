# R5 E10A — Anchored Higher-Lift FPT T-Join Solver

Date: 2026-09-25

Authority:
`JANUS_DERIVED_EXACT_DETERMINISTIC_FPT_SOLVER_AFTER_PA0013__NO_GLOBAL_P_EQ_NP_CLAIM`

Authorizing audit:
`PA-0013-CUBIC-LINEAGE-HIGHER-LIFT-LIVE-LEAF-SOURCE-AUDIT`

Parent gate:
`R5_E10A_HIGHER_LIFT_STAR_SUPPORT_PARAMETERIZATION_GATE_V1`

Checker:
`experiments/r5_e10a_anchored_higher_lift_fpt_tjoin.py`

## 1. Frozen input

Let a distinguished cubic-lineage live torso have an explicit binary `m`-lift representation

```
A=[B_G;S],
```

where `B_G` is a reduced incidence matrix and the quotient dimension

```
q = dim(C*(N)/rowspan(B_G)) <= m.
```

Assume the exact NM-0010/NM-0012 anchored promise:

```
C*(N)
=
span {
  D in C*(N):
  f in D,
  |D|<=4
}.
```

All edge weights are nonnegative rationals of polynomial bit length.

## 2. Quotient-basis extraction

Enumerate all sets

```
{f} union X,  |X|<=3.
```

There are `O(|E|^3)` candidates.

Test cocycle-space membership by Gaussian elimination and compute each candidate
modulo the graphic cut space

```
U=rowspan(B_G).
```

Because the anchored candidates span `C*(N)`, their quotient images span

```
W=C*(N)/U.
```

Select quotient-independent cocycles

```
D_1,...,D_q,
```

with

```
f in D_i,
|D_i|<=4.
```

This is deterministic polynomial preprocessing once the explicit `m`-lift
representation is given.

## 3. Higher-lift support normalization

Write the old signature rows as a basis of `W`.

Replace them by the quotient basis represented by `D_1,...,D_q`, adding
graphic cut rows as necessary.

These are elementary row operations on the full binary representation.

Hence the represented matroid is unchanged, and the new signature rows are
exactly the characteristic vectors of `D_1,...,D_q`.

Therefore every nonzero group label is supported on

```
F = D_1 union ... union D_q.
```

Since all `D_i` contain `f`,

```
|F|
<=
1 + q(4-1)
=
1+3q.
```

Freeze:

```
ANCHORED f-CONTAINING <=4 COCYCLE SPAN
+
EXPLICIT q-DIMENSIONAL GRAPHIC-LIFT QUOTIENT
        ->
SWITCH / ROW NORMAL FORM
WITH
SIGNATURE SUPPORT <= 1+3q.
```

NM-0013 is the special case `q<=2`.

## 4. Exact shortest-f reduction

As in NM-0013, with nonnegative weights:

```
shortest_f(N)
=
minimum weight binary cycle X containing f.
```

After normalization every edge outside `F` has zero group label.

For every subset

```
R subseteq F
```

satisfying

```
f in R
and
XOR_{e in R} lambda(e)=0,
```

put

```
T_R = partial_G(R).
```

The remaining set `Y subseteq E-F` completes `R` to a binary cycle exactly
when

```
partial_G(Y)=T_R.
```

Thus `Y` is an ordinary minimum-weight `T_R`-join in `G-F`.

Therefore

```
shortest_f(N)
=
min_R [
  w(R)+tau_{G-F}(partial R)
].
```

The equality is exact and witness-preserving.

## 5. Parameterized running time

There are at most

```
2^{|F|}
<=
2^{1+3q}
```

exceptional subsets.

Each residual problem is an ordinary deterministic nonnegative `T`-join.

Hence:

```
T(N)
=
2^{O(q)} poly(|N|).
```

More explicitly:

```
T(N)
<=
2^{1+3q} poly(|V|+|E|).
```

Consequences:

```
q = constant
    -> deterministic polynomial;

q = O(log n)
    -> deterministic polynomial;

unbounded q
    -> this theorem is FPT in q, not a global polynomial theorem.
```

This bypasses generic randomized group-constrained circulation inside the
anchored cubic-lineage subclass.

## 6. Witness reconstruction

For the minimizing `R`, reconstruct a minimum `T_R`-join `Y`.

Then

```
X=R union Y
```

is an optimal binary cycle through `f`.

As in NM-0013, extract the circuit component containing `f`, or equivalently
take a maximal independent subset of `X-{f}` and reconstruct the fundamental
circuit of `f`.

The resulting circuit has the same optimum value.

## 7. Sharpened q_graph diagnostic

A second theorem-level diagnostic strengthens NM-0017.

Suppose `N` has rank `r`, ground-set size `m_E`, cogirth `g*`, and

```
q_graph(N)<=q.
```

Then `C*(N)` contains a graphic cut subspace of dimension at least

```
d=r-q.
```

Choose a full-row-rank reduced incidence matrix `B` for that subspace.

Every row of `B` is a nonzero cocycle of `N`, so each has weight at least
`g*`.

Every column of `B` has weight at most two.

Moreover, because the rows are independent and `d>0`, not every column can
have even weight: if all columns had weight zero or two, the XOR of all rows
would be zero.

Therefore at least one column has weight one and

```
sum row weights
<=
2m_E-1.
```

Hence

```
(r-q) g*
<=
2m_E-1.
```

Equivalently:

```
q_graph(N)
>=
r
-
floor((2m_E-1)/g*).
```

For the NM-0017 leaf:

```
r=11,
m_E=16,
g*=4,
```

so

```
q_graph
>=
11-floor(31/4)
=
4.
```

Thus the explicit cubic-lineage leaf is actually certified

```
q_graph >= 4,
```

strictly strengthening the earlier `q_graph>=3` certificate.

## 8. Finite controls

The checker contains:

1. a quotient-rank-four multigraph control whose full cocycle space is spanned
   by `f`-containing support-at-most-four cocycles;
2. deterministic extraction of four quotient-independent small cocycles;
3. verification of the support ceiling

```
|F|<=1+3*4=13;
```

4. exhaustive comparison of the higher-lift T-join solver with brute-force
   binary-cycle optimization on random nonnegative weights;
5. replay of the sharpened NM-0017 diagnostic yielding `q_graph>=4`.

## 9. Source / novelty boundary

Source-bound:

- `m`-lift / group-labelled graph representation language;
- ordinary minimum `T`-join;
- row operations / switching;
- fixed finite-group randomized GCC.

JANUS-derived here:

- anchored higher-lift support ceiling `1+3q`;
- deterministic `2^{O(q)}` exact shortest-`f` solver for the anchored
  subclass;
- polynomiality for constructively represented `q=O(log n)`;
- sharpened incidence/cogirth lower bound on `q_graph`.

## 10. Gate verdict

```
R5_E10A_HIGHER_LIFT_STAR_SUPPORT_PARAMETERIZATION_GATE_V1
=
PASS_DETERMINISTIC_FPT_IN_EXPLICIT_LIFT_RANK
```

and for the explicit NM-0017 leaf:

```
q_graph>=4.
```

## 11. New frontier

The optimization problem is no longer the immediate obstruction once an
explicit low-enough lift representation is supplied.

The surviving global question is:

```
HOW LARGE CAN q_graph GROW
ON ACTUAL CUBIC-LINEAGE
3-CONNECTED S8 LIVE LEAVES,
AND CAN A NEAR-MINIMUM m-LIFT REPRESENTATION
BE CONSTRUCTED EFFICIENTLY?
```

A logarithmic bound is already sufficient:

```
q_graph=O(log n)
+
constructive representation
        ->
global local-leaf polynomial solve
via this theorem.
```

An actual family with

```
q_graph=omega(log n)
```

would falsify that route and expose the next compression requirement.

Freeze next gate:

```
R5_E10A_CUBIC_LINEAGE_LIFT_RANK_GROWTH_AND_CONSTRUCTION_GATE_V1
```

No global E10 promotion yet.

## 12. Scientific ceiling

```
PA-0013
=
PASS

ANCHORED EXPLICIT q-LIFT SHORTEST-f
=
DETERMINISTIC 2^{O(q)} poly(n)

q=O(log n)
=
POLYNOMIAL

NM-0017 LEAF q_graph LOWER BOUND
=
STRENGTHENED TO >=4

CUBIC-LINEAGE q_graph GROWTH
=
OPEN

POLYNOMIAL CONSTRUCTION OF NEAR-MINIMUM LIFT
=
OPEN

GLOBAL SOLVER PROMOTION
=
HOLD

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
