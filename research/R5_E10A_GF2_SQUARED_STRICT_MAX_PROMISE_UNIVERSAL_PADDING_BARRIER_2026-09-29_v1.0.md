# R5 E10A — GF(2)^2 Strict-Max Promise Universal Padding Barrier

Date: 2026-09-29

Authority:
`JANUS_DERIVED_EXACT_PROMISE_REDUCTION_BARRIER__NO_SOLVER_CLAIM__NO_NOVELTY_CLAIM`

Parent residual:
`R5_E10A_GF2_SQUARED_UNIQUE_STRICT_MAX_LABEL_VALUE_GATE_V1`

Scientific ceiling:

```text
UNIQUE-STRICT-MAX PROMISE
= NOT A TRACTABILITY ASSUMPTION BY ITSELF

DETERMINISTIC PRESCRIBED GF(2)^2 SHORTEST PATH
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```

## 1. Problem

Let `G=(V,E)` be a simple undirected graph with distinct terminals `s,t`, unit
edge lengths, and labels

```text
lambda:E -> GF(2)^2.
```

For `g in GF(2)^2`, let

```text
m_g(G)
```

be the minimum number of edges in a simple `s-t` path of XOR label `g`, with
`+infinity` if no such path exists.

The current E10A residual asks for a prescribed target `c` after earlier
pairwise-parity and optimal-face machinery has certified that `c` is the unique
strict maximum label class.

This note proves that this promise, taken alone, does not shrink the general
prescribed-label shortest-path problem.

## 2. Constant-factor padding construction

Given an arbitrary instance `(G,s,t,lambda,c)`, construct `G'` as follows.

### 2.1 Stretch the original core

Replace every original edge `e=uv` by an internally vertex-disjoint path of
length four:

```text
u - a_e - b_e - c_e - v.
```

Put the original label `lambda(e)` on one segment and label the other three
segments `00`.

Thus every simple path in the subdivided core has exactly the same XOR label as
its projection to `G`, and its length is multiplied by four.

### 2.2 Add three cheap wrong-label terminal routes

Let the three labels different from `c` be `d1,d2,d3` in any fixed order.
Add three fresh internally vertex-disjoint `s-t` routes of lengths

```text
1, 2, 3,
```

with total labels respectively

```text
d1, d2, d3.
```

Concretely, put the desired label on the first edge of each route and `00` on
its remaining edges.

All internal route vertices are fresh and have no incident edges outside their
own route.

Because the original core edges were subdivided, adding one direct `s-t` edge
for the length-one route creates no parallel edge.  The output remains a simple
undirected unit-weight graph.

## 3. Path dichotomy

Every simple `s-t` path in `G'` is exactly one of:

1. a path lying wholly in the subdivided original core; or
2. one of the three newly added terminal routes.

Indeed an added route meets the rest of the graph only at `s` and `t`.  A
simple `s-t` path that enters such a route at `s` must follow it to `t`; it
cannot leave and later re-enter the core without revisiting a terminal.

Inside the subdivided core, all new subdivision vertices have degree two, so
contraction of every length-four edge path gives a bijection with simple
`s-t` paths of `G`.

The bijection preserves XOR label and divides length by four.

## 4. Exact cost identities

For the target label `c`, none of the three new routes has label `c`.
Therefore

```text
m_c(G') = 4 m_c(G).
```

For every `d != c`, its dedicated cheap route gives

```text
m_d(G') <= 3.
```

If `c` is feasible in `G`, then every `c`-path has positive length because
`s != t`, so

```text
m_c(G') >= 4.
```

Hence

```text
m_c(G') > max_{d != c} m_d(G').
```

Thus `c` is the unique strict maximum label class in `G'`.

If `c` is infeasible, it remains infeasible; this case can be separated by the
known deterministic fixed-group feasibility test, or viewed with
`m_c=+infinity`.

## 5. Exact witness and threshold preservation

Every `c`-labelled path in `G'` lies in the stretched core.  Contracting each
four-edge replacement path reconstructs a `c`-labelled path in `G`.

Therefore a shortest target witness round-trips exactly:

```text
P'_c shortest in G'
<->
contract(P'_c) shortest in G.
```

For every integer threshold `L`:

```text
m_c(G) <= L
iff
m_c(G') <= 4L.
```

Likewise exact equality is preserved:

```text
m_c(G) = L
iff
m_c(G') = 4L.
```

The construction has constant-factor size blow-up and is deterministic linear
time.

## 6. Consequence

Let

```text
GENERAL-XCSP2
```

denote unit-weight prescribed-label shortest simple path over `GF(2)^2`, and
let

```text
STRICTMAX-XCSP2
```

be the promise restriction in which the prescribed feasible target label is
the unique strict maximum among the four label-class optima.

The construction proves an exact polynomial reduction

```text
GENERAL-XCSP2
<=_p
STRICTMAX-XCSP2.
```

The reverse algorithmic implication is trivial because `STRICTMAX-XCSP2` is a
subclass of the general problem.  Therefore, at the level of deterministic
polynomial solvability, the strict-max promise is equivalent to the full
prescribed-label problem.

In particular:

```text
DETERMINISTIC POLY SOLVER FOR THE STRICT-MAX RESIDUAL
=>
DETERMINISTIC POLY SOLVER FOR GENERAL GF(2)^2
PRESCRIBED-LABEL SHORTEST SIMPLE PATH.
```

## 7. Interaction with the JANUS stack

Previous E10A results remain useful:

- T-join separability reduces two-row graph lift to prescribed-label path;
- pairwise parity collapse solves all but at most one label-class optimum;
- optimal-face blossom-parity DP deterministically decides whether the top
  plateau contains the target label.

However, once the target is certified as the unique strict maximum, that
promise itself supplies no additional generic tractability.  Any further
polynomial closure must use **additional source-origin structure** beyond
strict maximality, or it effectively solves the full `GF(2)^2` prescribed-path
primitive.

The origin-valid family in
`R5_E10A_ORIGIN_PRESERVING_UNBOUNDED_GK_FRAGMENT_PASSAGE_2026-09-24_v1.0.md`
already shows that strict-max excess can grow unboundedly, so bounded-excess
repair is also not authorized.

## 8. Checker

Executable finite regression:

```text
experiments/r5_e10a_strict_max_promise_universal_padding_barrier.py
```

It enumerates all simple `s-t` paths on seeded small labelled graphs, applies
the padding construction, and verifies:

```text
m'_c = 4 m_c,
m'_d <= 3 for d != c,
strict-max whenever c is feasible,
exact threshold scaling,
shortest target witness contraction.
```

The checker is finite evidence; the theorem is the path-dichotomy proof above.

## 9. New live gate

The correct next target is not another promise-only manipulation.  It is:

```text
R5_E10A_GF2_SQUARED_SOURCE_ORIGIN_STRICT_MAX_CONTRACTION_GATE_V1
```

Required:

exploit structure inherited from the actual cubic/matroid source before or
during the two-row graph-lift transformation, beyond the generic unit-weight
`GF(2)^2` path object, to decide the source lower-bound-tight threshold in
deterministic polynomial time.

Forbidden:

- treating unique strict maximum as a tractable promise;
- assuming a bounded strict-max excess;
- assuming general Exact Matching / BCPM derandomization;
- using the quarantined Du-2026 claim as authority.

## 10. Ceiling

```text
GENERAL XCSP2 -> STRICT-MAX XCSP2
= EXACT CONSTANT-FACTOR POLYNOMIAL REDUCTION

STRICT-MAX PROMISE AS GENERIC SIMPLIFIER
= CLOSED / FALSIFIED

SOURCE-ORIGIN EXTRA STRUCTURE
= STILL AVAILABLE TO EXPLOIT

DETERMINISTIC UNIVERSAL SOLVER
= NOT PROVED

P_VS_NP
= OPEN
```
