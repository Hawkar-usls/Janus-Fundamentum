# R5 E10A — Bounded-Capacity XLC to Bipartite Exact Matching Transfer

Date: 2026-09-24

Authority:
`JANUS_DERIVED_EXACT_BRIDGE_AFTER_AUDIT__CONDITIONAL_DETERMINIZATION_TRANSFER__NO_EXTERNAL_CANDIDATE_PROMOTION`

Authorizing audit:
`PA-0005-TWO-ROW-GRAPH-LIFT`

Continuation of:
`NM-0002-TWO-ROW-LIFT-GCC-BRIDGE`

Parent scope:
`R5_E10A_TWO_ROW_GRAPH_LIFT_DETERMINISTIC_DISTINGUISHED_F_GATE_V1`

Checker:
`experiments/r5_e10a_xlc_bipartite_exact_matching_bridge.py`

## 1. Purpose

The source-bound fixed-group GCC solver reaches an exact-length circulation
subproblem and is randomized because its published implementation invokes
exact-cost matching machinery.

This artifact asks a narrower structural question:

> For the bounded-capacity, polynomially bounded nonnegative-length XLC
> instances produced by the fixed-group route, can exact-cost feasibility be
> transferred to **bipartite** Exact Matching?

The answer is yes.

The reduction theorem is unconditional.  Any deterministic consequence from the
2026 Du preprint is deliberately conditional and is not promoted to JANUS
authority.

## 2. Exact-length circulation input

Let

```
D=(V,A)
```

be a directed graph.

For each arc `a=(u,v)` let:

```
0 <= x_a <= c_a,
c_a in Z_+,
ell_a in Z_+.
```

The exact-length circulation problem asks whether there is an integral vector
`x` satisfying

```
sum_{a out of v} x_a
=
sum_{a into v} x_a

for every v
```

and

```
sum_a ell_a x_a = L.
```

Assume the total unary capacity expansion and all lengths are polynomially
bounded.  In the fixed finite-group GCC lane, the relevant capacities are
bounded by a function of the fixed group and therefore satisfy this condition.

## 3. Circulation -> bipartite exact-weight b-factor

Create a bipartite multigraph

```
B=(V_L union V_R,E_B).
```

For every directed arc `a=(u,v)` of capacity `c_a`, create `c_a`
unit-capacity token edges

```
u_L -- v_R
```

each of weight `ell_a`.

Define

```
C_out(v) = sum_{a out of v} c_a,
C_in(v)  = sum_{a into v} c_a,

b_v = max(C_out(v), C_in(v)).
```

Add `b_v` zero-weight diagonal slack-token edges

```
v_L -- v_R.
```

Seek a simple b-factor with exact degrees

```
deg(v_L)=deg(v_R)=b_v.
```

### Forward map

Given a circulation `x`, select exactly `x_a` token copies of every arc.
Let

```
t_v =
sum_{a out of v} x_a
=
sum_{a into v} x_a.
```

Select exactly

```
s_v = b_v - t_v
```

diagonal slack tokens.

Then

```
deg(v_L)=t_v+s_v=b_v
deg(v_R)=t_v+s_v=b_v.
```

The b-factor weight is exactly

```
sum_a ell_a x_a.
```

### Reverse map

Given a b-factor, let `x_a` be the number of selected token copies of arc
`a` and let `s_v` be the number of selected diagonal slack tokens.

The two degree equations give

```
out_x(v)+s_v=b_v
in_x(v)+s_v=b_v,
```

hence

```
out_x(v)=in_x(v).
```

Thus `x` is an integral circulation respecting every original capacity.
Again, weight is preserved exactly.

Therefore the sets of achievable exact lengths are identical:

```
{ell(x): x is a feasible circulation}
=
{w(F): F is a feasible b-factor of B}.
```

This is stronger than preservation of only the optimum.

## 4. Bipartite b-factor -> bipartite perfect matching

Use the standard b-factor/perfect-matching gadget.

For each original b-factor vertex `z`, create `b(z)` copy vertices.

For every unit b-factor edge `e=zw`, create two peripheral vertices
`p_{e,z},p_{e,w}` joined by an inner edge.

Connect `p_{e,z}` to every copy of `z`, and similarly at `w`.

Interpretation:

- if `e` is **not** in the b-factor, match the two peripheral vertices by
  their inner edge;
- if `e` **is** in the b-factor, match both peripheral vertices outward to
  one still-unmatched copy at their endpoints.

Exactly `b(z)` incident original edges must therefore be selected at every
`z`.

### Bipartiteness

If the b-factor graph has sides `X,Y`, color:

- copies of `X` and peripherals belonging to `Y` on one side;
- copies of `Y` and peripherals belonging to `X` on the other.

Every inner and outer gadget edge crosses this bipartition.

### Weight preservation

For an original b-factor edge `e=xy` with `x in X`, assign its weight only
to the outer gadget edges incident with the peripheral `p_{e,x}`.
Assign zero to the other outer edges and the inner edge.

A selected original b-factor edge contributes its weight exactly once; an
unselected edge contributes zero.

Hence exact-weight b-factor feasibility is equivalent to exact-weight perfect
matching feasibility on a bipartite graph.

## 5. Polynomial exact weights -> red/blue Bipartite Exact Matching

All perfect matchings in the gadget graph have the same cardinality `h`.

First shift every edge weight by one:

```
q_e = w_e + 1.
```

Thus all `q_e>=1`, and target weight `W` becomes

```
Q = W + h.
```

For each edge `e=ab` of positive integer weight `q_e`, replace it by an
internally vertex-disjoint path of odd length

```
2 q_e - 1
```

from `a` to `b`.

Color path edges alternately red and blue, starting and ending red.
There are exactly

```
q_e red edges
and
q_e-1 blue edges.
```

The path has two possible perfect-matching modes relative to its endpoints:

- selected-edge mode: the matching uses the odd-position path edges and
  contributes exactly `q_e` red edges;
- unselected-edge mode: the internal vertices are paired by the even-position
  edges and contribute zero red edges.

Therefore perfect matchings of exact weight `Q` correspond to perfect
matchings containing exactly `Q` red edges.

Because an original bipartite edge joins opposite sides and the replacement
path has odd length, bipartiteness is preserved.

For polynomially bounded weights the expansion is polynomial.

## 6. Combined theorem

For bounded/unary total capacities and polynomially bounded nonnegative
lengths:

```
EXACT-LENGTH CIRCULATION
<=_p
BIPARTITE EXACT-WEIGHT b-FACTOR
<=_p
BIPARTITE EXACT-WEIGHT PERFECT MATCHING
<=_p
BIPARTITE RED/BLUE EXACT MATCHING.
```

Every step carries a polynomial witness map back to the circulation.

Applied to the source-bound fixed-group GCC route, this gives:

```
FIXED-r GRAPH-LIFT DISTINGUISHED-f
<=_p
BIPARTITE EXACT MATCHING.
```

This does **not** by itself give a deterministic algorithm.

## 7. Du-2026 conditional transfer only

Du's 2026 arXiv preprint claims:

```
BIPARTITE EXACT MATCHING in P
```

with a deterministic `O(n^6)` algorithm.

If that theorem is independently validated in the future, the reduction above
would immediately imply a deterministic polynomial terminal for the bounded-
capacity fixed-group GCC instances, and hence for every fixed-row graph-lift
distinguished-`f` lane reached by the earlier JANUS bridge.

Current JANUS status is deliberately weaker:

```
DU-2026
=
EXTERNAL CANDIDATE_UNVERIFIED.
```

Appendix A of the preprint states that the top-level Lean certification remains
conditional on eight structural hypotheses.  Therefore this artifact records
only:

```
DU-2026 VALID
=>
FIXED-r GRAPH-LIFT DETERMINISTIC P.
```

It does not assert the antecedent.

## 8. Checker controls

The checker verifies:

1. exact-cost spectra of small circulations equal exact-cost spectra of the
   bipartite b-factor construction;
2. explicit capacity-two circulation controls;
3. b-factor/perfect-matching gadget cost preservation on small instances;
4. bipartiteness of the perfect-matching gadget;
5. the positive-weight red/blue path gadget on small bipartite perfect-matching
   instances;
6. witness decoding back to circulation token counts.

The checker is finite evidence only; the proof is the structural argument above.

## 9. Scientific ceiling

```
XLC -> BIPARTITE b-FACTOR
=
PROVED EXACT

b-FACTOR -> BIPARTITE PERFECT MATCHING
=
STANDARD / SOURCE-BOUND + CHECKED

POLY-WEIGHT PM -> BIPARTITE EXACT MATCHING
=
STANDARD / SOURCE-BOUND + CHECKED

FIXED-r GCC -> BIPARTITE EXACT MATCHING
=
PROVED BY COMPOSITION

BIPARTITE EXACT MATCHING in P
=
EXTERNAL CANDIDATE ONLY

UNCONDITIONAL DETERMINISTIC FIXED-r GRAPH-LIFT
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
