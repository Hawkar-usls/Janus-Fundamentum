# R5 E52 — General Claw-Family Core Forcing

Date: 2026-10-03

Status:
`EXACT_ALL_CLAW_INTERSECTION_UNION_FORCING__STRICTLY_INSIDE_THREE_OR_MORE_CLAW_CORE__POST_CLOSURE_REQUIRES_EMPTY_INTERSECTION_FULL_UNION`

Scientific ceiling:

```text
THIS NOTE APPLIES TO THE FROZEN ALL-POSITIVE SQUARE+CUBIC+LINEAR E12 CARRIER.

FOR ANY CONFLICT VERTEX v WITH NONEMPTY FAMILY C(v) OF INDUCED CLAW LEAF SETS,
DEFINE

  I_v = INTERSECTION_{T IN C(v)} T,
  U_v = UNION_{T IN C(v)} T.

THEN EVERY EXACT-ONE WITNESS OBEYS

  x_u = 1-x_v  FOR EVERY u IN I_v,
  x_w = 0      FOR EVERY w IN N(v) \ U_v.

THIS EXTENDS THE E49/E50 FORCING MECHANISM TO ARBITRARILY MANY CLAW STATES.
AFTER EXHAUSTIVE CLOSURE, EVERY UNRESOLVED VERTEX MUST SATISFY

  I_v = EMPTY,
  U_v = N(v).

P_VS_NP = OPEN.
```

## 1. Setting

Let `G_A` be the conflict graph of a square+cubic+linear all-positive Exact-One
carrier.  For a vertex `v`, let

```text
C(v)
```

be the family of all induced claw leaf sets centered at `v`.

R5 E48 proves that in any witness:

```text
v selected   -> no neighbor of v is selected;
v unselected -> the three selected neighbors of v form one member of C(v).
```

Assume `C(v)` is nonempty.

## 2. All-claw intersection

Take

```text
u in I_v := intersection_{T in C(v)} T.
```

If `v` is selected, independence gives `x_u=0`.

If `v` is unselected, its selected-neighbor claw is some `T in C(v)`.  Since `u`
lies in every claw, `u` is selected.

Therefore in all cases

```text
boxed:
x_u=1-x_v.
```

So every leaf present in every possible claw is complement-linked to the center.

## 3. Outside the claw union

Take

```text
w in N(v) \ U_v,
U_v := union_{T in C(v)} T.
```

If `v` is selected, `w` is zero by independence.

If `v` is unselected, its selected-neighbor set is one claw `T in C(v)`; because
`w` lies in no claw, it is again unselected.

Hence

```text
boxed:
x_w=0.
```

This is an unconditional forcing rule.

## 4. Theorem CLAW-CORE-FORCING

For every vertex with at least one claw:

```text
boxed:
  x_u xor x_v = 1  for u in I_v,
  x_w = 0          for w in N(v)\U_v.
```

The rules are exact and require no branching.

## 5. Earlier claw rules as special cases

R5 E49 (one claw):

```text
I_v = U_v = the unique claw T,
```

so E52 gives exactly the E49 three complement relations and three outside-union
zeros.

R5 E50 (two claws):

```text
I_v=T_0 intersect T_1,
U_v=T_0 union T_1,
```

so E52 reproduces the overlap forcing and outside-union zeros.

Thus E52 is the natural general form of both local rules.

R5 E51 remains distinct: when two claws are complementary, E52 has empty
intersection and full union and therefore no unary/parity forcing; E51 then solves
the residual three-state component globally by permutation propagation.

## 6. Polynomial closure

Each conflict vertex has degree six, so there are only twenty possible 3-subsets of
its neighborhood.  Enumerating all claws, their intersection and union is therefore
constant work per vertex after `G_A` is built.

Run to closure:

```text
1. enumerate C(v) for every active vertex;
2. if C(v)=empty use E48;
3. otherwise compute I_v,U_v;
4. parity-link all u in I_v to complement of v;
5. force every w in N(v)\U_v to zero;
6. run Exact-One row propagation and quotient equal/complement variables;
7. recompute affected local claw families;
8. repeat until stable or contradiction.
```

All operations are polynomial.

## 7. Strict strengthening inside the >=3-claw sector

The companion checker contains an 18-variable square+cubic+linear carrier whose
claw counts are

```text
[3,6,4,5,4,4,6,6,6,4,6,4,6,5,4,6,4,5].
```

Hence every vertex has at least three claws:

```text
E48 zero-claw forcing does not apply;
E49 unique-claw forcing does not apply;
E50 two-claw overlap forcing does not apply;
E51 all-two-complementary-claw terminal does not apply.
```

Nevertheless at vertex `0`:

```text
I_0={16},
N(0)\U_0={17}.
```

Therefore E52 proves in every witness

```text
x_16=1-x_0,
x_17=0.
```

An independent exhaustive check confirms that this finite carrier is UNSAT.  The
purpose of the control is not to claim E52 alone closes it, but to show that E52
still creates exact information strictly beyond E48--E51.

## 8. Canonical post-E52 local core

After exhaustive E52 closure, every unresolved vertex with at least one claw must
satisfy simultaneously

```text
boxed:
I_v=empty,
U_v=N(v).
```

So no neighbor is selected in every claw state and no neighbor is excluded from
every claw state.

Combined with E48--E51, the local unresolved core now has genuine distributed claw
ambiguity rather than hidden unary or parity consequences.

## 9. Scope caveat

As in E48--E51, the theorem relies on the all-positive E12 conflict graph where
selected variables form an independent set.  It is not automatically valid for an
arbitrary signed-literal co-occurrence graph.

## 10. Frontier

A post-E52 hard survivor on the all-positive E12 route must now satisfy, after exact
closure:

```text
every active vertex has at least three claws, OR belongs to a mixed component not
closed by E51;
for every unresolved vertex, all claw leaf sets have empty total intersection;
their union covers all six neighbors;
no existing parity/forcing/quotient/global-language terminal applies.
```

The next local classification target is the finite family of claw systems on the
three source-pairs with these intersection/union conditions.  Because every claw is
a transversal of three pairs, this reduces to subsets of the Boolean cube
`{0,1}^3`; that finite cube structure is the next exact attack surface.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e52_general_claw_core_forcing.py
```
