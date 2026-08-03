# C024 — Post-Unit Cycle-Shield Birth Route Classification

## Status

```text
THEOREM = PROVED
SCOPE = ONE_CONSISTENT_UNIT_RESTRICTION_ON_ARBITRARY_QUOTIENT
ARBITRARY_N = YES
SPANNING_SPANNING_BIRTH = IMPOSSIBLE
INTERNAL_SOURCE_BIRTH = IMPOSSIBLE
BRANCH_SAFE_BIRTH_REQUIRES_DIRECTED_CYCLE_SOURCE = PROVED
GT_REACHABLE_CYCLE_SHIELD_EXCLUSION = OPEN
P_VS_NP = OPEN
```

## Purpose

Post-unit restriction can create a raw same-cut double-bridge pair in abstract
clauses.  Even two branch-safe sources can do so once current quotient
components contain multiple original vertices.

The exact pure-graph boundary is nevertheless sharp:

> a new same-cut pair cannot be born from two component-spanning sources;
> therefore every birth from two branch-safe sources requires at least one
> directed-cycle source whose cycle protection disappears under the unit step.

This theorem classifies the only branch-safe post-unit birth route.  It does not
exclude that route in reachable graph-tautology states.

## Quotient model

Fix a consistent partial comparison assignment and contract its relation
components.  Let the current quotient vertex set be `V`.

Apply one further consistent unit assignment.

- If its endpoints already lie in one quotient component, the quotient is
  unchanged.
- Otherwise let the endpoints be distinct quotient vertices `x,y` and let

```text
q : V -> V/{x=y}
```

be the identification map.

A source clause survives the assignment only if it contains no satisfied
literal.  It may contain the falsified orientation of the assigned comparison;
that literal is deleted.  Its endpoints are exactly `x,y`, so after applying
`q` it would be an internal loop.  Consequently deleting that false literal has
no effect on the post-step external graph.

Thus the external multigraph of every surviving residual clause is precisely
the image under `q` of the source external multigraph, with loops omitted and
literal identities retained.

## Lemma 1 — internal-only cannot become spanning

If a source clause is `INTERNAL_ONLY`, every source literal has both endpoints
inside one current quotient component.

Further identification of quotient vertices cannot turn an internal literal
into an external edge.  Therefore every surviving residual remains
internal-only.

Hence an internal-only source cannot participate in a post-step
component-spanning double-bridge pair.

## Lemma 2 — connectedness survives contraction

Let `G` be the external undirected multigraph of a component-spanning source
clause.  Then `G` is connected on `V`.

Identifying `x,y` maps every source path to a post-step walk.  Therefore the
quotient multigraph `q(G)` is connected on `V/{x=y}`.

Deleting the falsified assigned literal does not affect this conclusion because
that literal maps to a loop at `q(x)=q(y)`.

Thus every surviving residual of a component-spanning source remains
component-spanning.

## Lemma 3 — residual bridges reflect to source bridges

Let a literal edge `p` remain external after the contraction and suppose its
image is a bridge in `q(G)`.

Assume for contradiction that `p` was not a bridge in `G`.  Then the endpoints
of `p` are connected in `G-p` by a path avoiding `p`.

Applying `q` to that path gives a walk between the post-step endpoints of `p`
which still avoids `p`.  Removing repeated vertices and loops gives a path in
`q(G)-p`.  This contradicts that `p` is a bridge in `q(G)`.

Therefore every residual bridge was already a source bridge.

## Lemma 4 — the contracted vertices lie on one side of a surviving bridge

Let `p` be a bridge of connected `G`, and let

```text
S | T
```

be the two connected components of `G-p`.

If `x` and `y` lay on opposite sides of this cut, identifying them would connect
`q(S)` and `q(T)` even after deleting `p`.  Then `p` would not be a bridge in
`q(G)`.

Therefore, whenever `p` remains a bridge after contraction,

```text
x,y in S
or
x,y in T.
```

The post-step bridge cut is exactly the image

```text
q(S) | q(T).
```

## Lemma 5 — equal residual cuts lift uniquely

Suppose two connected source graphs `G_A,G_B` contain complementary pivot
bridges and their residual pivot bridges induce the same cut after identifying
`x,y`.

By Lemma 4, `x,y` lie on one side of each source bridge cut.  Hence taking the
full inverse image under `q` uniquely reconstructs each source cut from its
post-step cut.

Equal post-step cuts therefore imply equal source cuts, up to complementation.

Thus a same-cut pair obtained from two component-spanning sources was already a
same-cut pair before the unit assignment.  It is transmitted, not born.

## Theorem — Cycle-Shield Birth Route

Let two source clauses be branch-safe:

```text
DIRECTED_CYCLE
OR COMPONENT_SPANNING
OR INTERNAL_ONLY.
```

Assume they survive one consistent unit assignment and their residuals form a
same-cut complementary double-bridge pair which did not exist between the
source clauses.

Then at least one source clause is `DIRECTED_CYCLE`.

### Proof

If either source were internal-only, Lemma 1 would prevent its residual from
being component-spanning.

If neither source were directed-cycle, both branch-safe sources would therefore
be component-spanning.  Lemmas 2–5 would imply that the residual same-cut pair
already existed before the assignment, contradicting that it is newly born.

Hence at least one source is directed-cycle.  QED.

## Corollary — the cycle shield must collapse

A residual participating in a double-bridge pair is classified
`COMPONENT_SPANNING`, not `DIRECTED_CYCLE`.

Therefore every directed cycle which protected the relevant source from the
unsafe low-rank class has failed to survive as an external directed cycle after
the assignment.  It must have been:

```text
internalized by identifying quotient components;
broken by deletion of the falsified assigned literal;
or transformed into a closed structure containing no surviving directed cycle.
```

A branch-safe same-cut birth is therefore exactly a

```text
CYCLE_SHIELD_COLLAPSE
```

route.

## Minimal abstract witness

On four original vertices, first assign

```text
x_03 = false,
```

creating quotient components

```text
{0,3}, {1}, {2}.
```

Take

```text
C = (-x_13, x_23)                 COMPONENT_SPANNING
D = (-x_01, -x_13, -x_23)         DIRECTED_CYCLE.
```

Assign `x_13=true`.  The false literal `-x_13` disappears and the components
become

```text
{0,1,3}, {2}.
```

The residual clauses form a new same-cut complementary bridge pair on
`x_23/-x_23`.  The directed two-cycle protecting `D` has collapsed inside the
merged component.

This witness demonstrates that the classified route is real.

## Mechanical support

The two-step four-vertex exhaustive census gives:

```text
same-cut births                         6,048
both-safe births                        2,592
both-safe non-unit births               2,592
COMPONENT_SPANNING + DIRECTED_CYCLE     2,304
DIRECTED_CYCLE + DIRECTED_CYCLE           288
COMPONENT_SPANNING + COMPONENT_SPANNING     0
```

The census is evidence and a regression check.  Lemmas 1–5 are the
arbitrary-quotient proof.

## Consequence for C024

The post-unit obligation is no longer an unrestricted contraction problem.
The only branch-safe route left is:

```text
reachable directed-cycle source
+ unit contraction deleting/internalizing its final cycle shield
+ surviving complementary same-cut bridge pair.
```

The remaining GT-specific theorem is:

### GT Reachable Cycle-Shield Exclusion

No post-unit step reachable before the historical frontier can collapse the
last protecting directed cycle of a source clause in a way that leaves a
same-cut complementary bridge pair alive in `P`.

This must use reachability, reason provenance, branch order, or terminal
semantics.  Pure quotient safety is insufficient.

## Claim boundary

This theorem classifies one consistent unit restriction on an arbitrary current
quotient.  It does not prove GT reachable cycle-shield exclusion, branch
handoff extinction, the global cache lower bound, or `P` versus `NP`.
