# R5 E50 — Two-Claw Overlap Propagation

Date: 2026-10-03

Status:
`EXACT_TWO_CLAW_OVERLAP_FORCING__COMMON_LEAVES_COMPLEMENT_CENTER__OUTSIDE_UNION_FORCED_ZERO__POST_E49_CORE_REQUIRES_COMPLEMENTARY_CLAWS`

Scientific ceiling:

```text
THIS NOTE APPLIES TO THE FROZEN ALL-POSITIVE SQUARE+CUBIC+LINEAR E12 CARRIER.

IF A CONFLICT VERTEX v HAS EXACTLY TWO INDUCED CLAWS WITH LEAF SETS T0,T1,
THEN EVERY EXACT-ONE WITNESS OBEYS

  x_u = 1-x_v  FOR u IN T0 INTERSECT T1,
  x_w = 0      FOR w IN N(v) \ (T0 UNION T1).

THEREFORE A TWO-CLAW VERTEX IS LOCALLY IRREDUCIBLE ONLY WHEN THE TWO CLAWS
ARE DISJOINT, IN WHICH CASE THEY PARTITION THE SIX NEIGHBORS.

THIS STRICTLY STRENGTHENS R5 E48/E49 BUT DOES NOT CLOSE THE COMPLEMENTARY
TWO-CLAW CORE.

P_VS_NP = OPEN.
```

## 1. Setting

Let `G_A` be the conflict graph of a square+cubic+linear all-positive Exact-One
carrier. Let `v` be a vertex with exactly two induced claw leaf sets

```text
T_0,T_1 subseteq N(v),
|T_0|=|T_1|=3.
```

As in R5 E48, if `v` is unselected then its three selected neighbors must be the
leaf set of an induced claw centered at `v`. Since exactly two such claws exist,
the selected-neighbor set is either `T_0` or `T_1`.

If `v` is selected, all six neighbors are unselected.

## 2. Common leaves

Take

```text
u in T_0 intersect T_1.
```

If `v` is unselected, both possible claw states select `u`, so

```text
x_u=1.
```

If `v` is selected, independence gives

```text
x_u=0.
```

Thus in both cases

```text
boxed:
x_u=1-x_v.
```

So every common claw leaf is complement-linked to the center.

## 3. Neighbors outside both claws

Take

```text
w in N(v) \ (T_0 union T_1).
```

If `v` is selected, `w` is zero by independence.

If `v` is unselected, the selected-neighbor set is exactly `T_0` or exactly `T_1`,
so `w` is again zero.

Hence

```text
boxed:
x_w=0.
```

This is an unconditional unary forcing rule.

## 4. Theorem TWO-CLAW-OVERLAP

Let

```text
I_v=T_0 intersect T_1,
Z_v=N(v) \ (T_0 union T_1).
```

Then every Exact-One witness satisfies

```text
boxed:
  x_u xor x_v = 1  for every u in I_v,
  x_w = 0          for every w in Z_v.
```

Because each claw has size three and `|N(v)|=6`, two distinct claws are free of any
new forcing exactly when

```text
I_v=emptyset
```

which is equivalent to

```text
T_1=N(v)\T_0.
```

Therefore:

```text
boxed:
After exhaustive E48/E49/E50 closure, every unresolved vertex with exactly two
claws must have two complementary claw leaf triples.
```

## 5. Polynomial propagation

Each vertex has six neighbors, so all induced claws are enumerated from only twenty
neighbor triples.

For a two-claw vertex:

```text
1. compute I_v and Z_v;
2. parity-union every u in I_v with complement relation to v;
3. force every w in Z_v to zero;
4. run Exact-One row propagation;
5. repeat to closure.
```

Contradictory parity or row states certify UNSAT.

The entire closure is polynomial.

## 6. Strict strengthening over E48/E49

The companion checker contains a 12-variable square+cubic+linear carrier with claw
counts

```text
[3,2,2,3,3,2,3,2,3,3,2,2].
```

Thus:

```text
no vertex has zero claws  -> E48 does not fire;
no vertex has one claw    -> E49 does not fire.
```

Vertices

```text
2,5,7
```

have exactly two overlapping claws. E50 forces unconditional zeros; ordinary
Exact-One row propagation then reaches contradiction and proves UNSAT.

So E50 closes an actual carrier untouched by both preceding claw rules.

## 7. Local binary-choice form of the remaining two-claw sector

When the two claws are complementary, write

```text
N(v)=T_v^0 disjoint_union T_v^1.
```

If `v` is unselected, exactly one whole triple `T_v^0` or `T_v^1` is selected.
If `v` is selected, all six neighbors are zero.

Thus such a vertex has exactly three local witness states:

```text
CENTER: v selected;
SIDE-0: v unselected and T_v^0 selected;
SIDE-1: v unselected and T_v^1 selected.
```

This exposes the next frontier as a genuine three-state consistency problem rather
than an arbitrary local Exact-One relation.

## 8. Scope caveat

As with E48 and E49, this theorem uses the all-positive E12 conflict graph. It is not
a theorem about arbitrary signed-literal co-occurrence graphs.

## 9. Router update

After E49 closure:

```text
TCL0 inspect vertices with exactly two claws;
TCL1 overlap -> complement-link common leaves;
TCL2 outside union -> force zero;
TCL3 propagate parity and Exact-One rows;
TCL4 contradiction -> UNSAT;
TCL5 otherwise retain only complementary two-claw vertices and >=3-claw vertices.
```

## 10. Frontier

The unresolved local ambiguity now begins at:

```text
(A) exactly two complementary claw states, or
(B) at least three claw states.
```

The most valuable next question is whether a carrier whose every active vertex lies
in case (A) reduces to a global Z_3/potential language, or whether an explicit
non-potential two-claw firewall exists.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e50_two_claw_overlap_propagation.py
```
