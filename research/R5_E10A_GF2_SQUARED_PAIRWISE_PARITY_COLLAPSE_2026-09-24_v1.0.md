# R5 E10A — Pairwise-Parity Collapse for Prescribed GF(2)^2 Path Costs

Date: 2026-09-24

Authority:
`JANUS_DERIVED_EXACT_STRUCTURE_AFTER_AUDIT__VALUE_COLLAPSE_ONLY__NO_FULL_DETERMINISTIC_SOLVER_CLAIM`

Authorizing audit:
`PA-0005-TWO-ROW-GRAPH-LIFT`

Continuation of:
`NM-0005-GF2-SQUARED-TJOIN-PATH-SEPARABILITY`

Parent scope:
`R5_E10A_TWO_ROW_GRAPH_LIFT_DETERMINISTIC_DISTINGUISHED_F_GATE_V1`

Checker:
`experiments/r5_e10a_gf2_squared_pairwise_parity_collapse.py`

## 1. Setting

Let `G=(V,E)` be an undirected graph with nonnegative edge weights and

```
lambda : E -> GF(2)^2.
```

Fix terminals `s,t`.

For every label `g in GF(2)^2`, define

```
m_g
=
minimum weight of a simple s-t path
whose XOR edge-label is g,
```

with `m_g=+infinity` if no such path exists.

The current JANUS blocker is to compute one prescribed `m_c`
deterministically.

Bentert--Drange--Fomin--Golovach--Korhonen give a one-sided-error randomized
polynomial algorithm for the full prescribed-label problem.  This artifact
does not replace that algorithm.  It proves that deterministic one-bit parity
optimization already determines all but one possible exceptional label cost.

## 2. Every pair of labels is one affine parity class

Take distinct labels

```
a,b in GF(2)^2.
```

Let

```
h = a XOR b != 0.
```

There is a unique nonzero linear functional

```
chi : GF(2)^2 -> GF(2)
```

whose kernel is

```
{0,h}.
```

Therefore

```
chi(a)=chi(b)
```

and the affine fiber

```
{x : chi(x)=chi(a)}
```

is exactly

```
{a,b}.
```

Replace every edge label `lambda(e)` by the bit `chi(lambda(e))`.

Then a simple s-t path lies in the required parity class exactly when its
original label is `a` or `b`.

Hence the minimum path cost in that one-bit parity instance is

```
mu_{a,b}
=
min(m_a,m_b).
```

## 3. Deterministic source-bound pair oracle

For undirected graphs with nonnegative edge weights, minimum-weight odd and even
simple s-t paths are computable in strongly polynomial time by the classical
matching-based parity-path algorithm.  A modern source is
Jüttner--Király--Mendoza-Cadena--Pap--Schlotter--Yamaguchi,
*Shortest odd paths in undirected graphs with conservative weight functions*,
Discrete Applied Mathematics 357 (2024), which explicitly records the
nonnegative-weight strongly-polynomial odd/even-path result.

Therefore all six values

```
mu_{a,b},  a<b,
```

for `GF(2)^2` are deterministically polynomial-time computable.

This is source-bound parity machinery combined with the exact affine-fiber
observation above.

## 4. Exact target formula

For a fixed feasible target `c`, define

```
R_c
=
max_{d != c} mu_{c,d}.
```

Since

```
mu_{c,d}=min(m_c,m_d),
```

we have

```
R_c
=
max_{d != c} min(m_c,m_d).
```

Let

```
M
=
max_{a<b} mu_{a,b}.
```

### Theorem A — target collapse

If `m_c<+infinity`, then

```
R_c = m_c
```

unless `c` is the unique strict maximum among the four label costs.

More precisely:

```
if  m_c <= max_{d!=c} m_d,
then R_c = m_c;

if  m_c > max_{d!=c} m_d,
then R_c = max_{d!=c} m_d < m_c.
```

This is immediate from the max-min identity.

### Theorem B — global one-exception property

For every feasible label `c`,

```
R_c <= m_c.
```

Moreover,

```
R_c < M
=> 
m_c = R_c.
```

For labels with

```
R_c = M,
```

we only know

```
m_c >= M.
```

Among all four labels, **at most one** can satisfy

```
m_c > M.
```

Indeed two distinct labels cannot both exceed `M), because their pairwise
minimum would then exceed `M), contradicting the definition of `M`.

Thus the six deterministic pairwise minima determine the exact optimum value
for every label except possibly one unique strict maximum.

They do not identify which top-plateau label, if any, is exceptional.

## 5. Feasibility firewall

If the prescribed target `c` is infeasible, then `m_c=+infinity`, and the
value formulas above should not be used as an optimization answer.

Prescribed-label s-t path **feasibility** is polynomial for every fixed finite
abelian group (Huynh; summarized explicitly by
Kawase--Kobayashi--Yamaguchi).

Therefore the deterministic pipeline first checks whether label `c` is
feasible.

Only the finite case enters the pairwise-collapse theorem.

This does not promote feasibility to shortest optimization.

## 6. Witness ceiling

The theorem is strongest as a **value/decision collapse**.

A one-bit parity optimizer for the pair `{c,d}` returns a shortest path whose
label may be `d`, even when

```
m_c = m_d.
```

Thus knowing numerically that

```
m_c = R_c
```

does not, by itself, reconstruct a shortest `c)-labelled witness.

There is one certified early exit:

if a pairwise parity call attaining `R_c` actually returns a path of label
`c`, then that path is an optimal prescribed-`c` witness.

No general witness reconstruction is claimed beyond this certified case.

## 7. Why two-forbidden-label feasibility does not close the gap

Kawase--Kobayashi--Yamaguchi deterministically solve the problem of finding an
s-t path whose label avoids two forbidden values, and characterize the case in
which the complete path-label set has size at most two.

That theorem concerns feasibility and label-set structure.

It does not optimize the weight of one specified surviving label and therefore
does not orient the remaining top-plateau ambiguity.

## 8. Du-2026 recheck

The current v3 PDF of Yuefeng Du's
*Bipartite Exact Matching in P* still describes the accompanying Lean work as a
**partial** formalization.

The abstract says that the main theorem is reduced to eight explicit
hypotheses.  Appendix A states that the top-level brace certification remains
conditional because eight structural inputs are represented as hypotheses
rather than proved in Lean.

Therefore JANUS keeps:

```
DU-2026
=
EXTERNAL_CANDIDATE_UNVERIFIED.
```

It is not used to close the present deterministic gap.

## 9. Exact new residual

The current deterministic ambiguity can be frozen as

```
R5_E10A_GF2_SQUARED_TOP_PLATEAU_DISAMBIGUATION_GATE_V1
```

Input:

- a feasible prescribed label `c in GF(2)^2`;
- nonnegative edge weights;
- all six pair minima `mu_{a,b}` computed deterministically;
- `R_c=M`.

Required:

decide deterministically whether

```
m_c = M
```

or

```
m_c > M.
```

The second case means exactly that `c` is the unique strict worst / most
expensive label class.

Equivalent global formulation:

from the four unknown optimum values, pairwise parity optimization leaves at
most one exceptional unique maximum whose identity and excess above `M`
remain unresolved.

## 10. Controls

The checker:

1. enumerates all simple s-t paths on seeded random small graphs;
2. computes the four exact label-class optima;
3. verifies every affine-functional pair reduction;
4. verifies all six pairwise minima;
5. verifies the target max-min formula;
6. verifies the global at-most-one-exception theorem;
7. includes an explicit strict-maximum control with label costs

```
2,3,4,7.
```

Development audit:
250 random exact instances + the explicit strict-maximum control passed.

## 11. Scientific ceiling

```
ALL SIX PAIRWISE LABEL MINIMA
=
DETERMINISTIC POLY

ALL BUT AT MOST ONE LABEL-CLASS OPTIMUM VALUE
=
DETERMINED BY PAIRWISE MINIMA

POSSIBLE UNIQUE STRICT MAXIMUM
=
UNRESOLVED

GENERAL OPTIMAL TARGET WITNESS
=
NOT RECONSTRUCTED

FULL PRESCRIBED-LABEL SHORTEST PATH
=
NOT SOLVED DETERMINISTICALLY

D1
=
EMPTY

P_VS_NP
=
OPEN
```
