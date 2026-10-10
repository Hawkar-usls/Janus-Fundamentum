# R5 E9 — Regular-Uniform Conflict Expansion and Critical-Set Extinction

Date: 2026-09-26

Authority:
`JANUS_DERIVED_ELEMENTARY_INCIDENCE_THEOREM_AFTER_PA0023__NO_COMPLEXITY_LOWER_BOUND`

Authorizing audit:
`PA-0023-REGULAR-UNIFORM-CONFLICT-EXPANSION`

Immediate parent:
`NM-0026-CONTEXTUAL-MIS-KERNEL-TRANSFER`

Checker:
`experiments/r5_e9_regular_uniform_conflict_expansion.py`

## 1. General theorem

Let H=(V,E) be an r-uniform, d-regular hypergraph with d>0.

Let G be its conflict graph / 2-section:

```
uv in E(G)
iff
some hyperedge e in E contains both u and v.
```

Let I be an independent set of G.  Equivalently, I is a strong independent
set of H: every hyperedge contains at most one vertex of I.

Then

```
boxed(
|N_G(I)| >= (r-1)|I|
).
```

No linearity, planarity, girth, satisfiability, or connectivity assumption is
needed.

## 2. Proof by incidence counting

Because H is d-regular, the vertices of I have exactly

```
d|I|
```

incident hyperedges in total.

Because I is strong independent, no hyperedge is incident with two vertices
of I.  Hence these are d|I| distinct hyperedges.

Each such hyperedge contains exactly one selected vertex and r-1 vertices
outside I.  Count pairs

```
(e,u)
```

where e is incident with I and u is one of the other vertices of e.

There are exactly

```
d(r-1)|I|
```

such pairs.

Every counted u lies in N_G(I).

But an outside vertex u has total hypergraph degree d, so it can occur in at
most d of the counted pairs.

Therefore

```
d(r-1)|I|
<=
d|N_G(I)|.
```

Divide by d:

```
|N_G(I)| >= (r-1)|I|.
```

QED.

## 3. Cubic Exact-One specialization

For the literal cubic source,

```
r=3,
d=3.
```

Hence every conflict-graph independent set satisfies

```
boxed(
|N(I)| >= 2|I|
).
```

This is stronger than the generic K1,4-free local statement from NM-0026:
it is a global expansion theorem for every independent set, not only one
neighborhood.

## 4. Immediate alpha bound and exact-cover equality

Because I and N(I) are disjoint subsets of the n source variables,

```
n
>=
|I|+|N(I)|
>=
3|I|.
```

Thus

```
alpha(G) <= n/3.
```

This independently rederives the upper half of NM-0022's
`alpha=n/3` bridge.

More generally, in the r-uniform d-regular setting,

```
alpha(G) <= n/r.
```

If equality holds, then

```
|I|=n/r.
```

The number of source hyperedges is

```
|E|=dn/r=d|I|.
```

The d|I| hyperedges incident with I are distinct, so they are all source
hyperedges.  Therefore every hyperedge contains exactly one member of I.

Thus equality is exactly a perfect strong transversal / exact cover.

For the cubic source:

```
|I|=n/3
iff
I is an Exact-One witness.
```

## 5. Critical-independent-set extinction

For every nonempty independent set I in the cubic source,

```
|I|-|N(I)|
<=
-|I|
<
0.
```

The empty independent set has difference zero.

Therefore the maximum critical difference is zero and:

```
boxed(
THE LITERAL CUBIC SOURCE CONFLICT GRAPH
HAS NO NONEMPTY CRITICAL INDEPENDENT SET.
)
```

So the Butenko--Trukhanov critical-set reduction imported in PA-0022 cannot
make a first move on the untouched literal source.

This does not contradict the source reduction theorem.  Its precondition is
simply never met here.

## 6. Classical crown extinction

A classical vertex-cover crown has a nonempty independent crown side C with
no edges to the rest R and a matching saturating the head H into C.

In particular

```
N(C) subseteq H
```

and saturation of H into C gives

```
|H| <= |C|.
```

Hence any crown would require

```
|N(C)| <= |C|.
```

But the cubic expansion theorem gives

```
|N(C)| >= 2|C|
```

for every nonempty independent C.

Contradiction.

Therefore:

```
boxed(
NO NONEMPTY CLASSICAL CROWN
EXISTS IN THE LITERAL CUBIC SOURCE CONFLICT GRAPH.
)
```

## 7. Reduction-order consequence

This matters for PA-0022's preprocessing order.

On the untouched cubic source:

```
critical-set reduction
=
NO_MOVE

classical crown reduction
=
NO_MOVE.
```

Other contextual reductions remain live.

NM-0026 already gives a literal cubic positive control where a neighborhood
domination rule applies, so the new theorem does not falsely imply that the
entire MIS-kernel stack is vacuous.

After a representation-changing reduction, deletion, folding, or struction,
the graph need no longer be the 2-section of an r-uniform d-regular source.
The expansion proof may cease to apply and critical sets / crowns can reappear.

Therefore those source-bound rules should remain in the downstream closure,
but they should not be searched first on each untouched cubic source instance.

## 8. New lean-source frontier

The literal-source contextual preprocessing order can now be sharpened:

```
1. perfect-graph terminal
2. claw-free terminal
3. domination / other source-applicable exact contextual moves
4. representation-changing exact reductions with alpha-offset/lift
5. only after regularity is broken, rerun critical-set / crown machinery
```

For genuinely untouched residuals, freeze the additional invariant:

```
INDEPENDENT_SET_2_EXPANDING
=
TRUE.
```

The active universal gap remains contextual selector destruction after all
known applicable reductions.

## 9. Verdict

```
NM-0027
REGULAR-UNIFORM CONFLICT EXPANSION
=
PASS

GENERAL
|N(I)| >= (r-1)|I|
=
PROVED

CUBIC
|N(I)| >= 2|I|
=
PROVED

alpha <= n/3
=
PROVED

alpha=n/3
=
EXACT COVER / EXACT-ONE

NONEMPTY CRITICAL INDEPENDENT SET
ON LITERAL CUBIC SOURCE
=
IMPOSSIBLE

CLASSICAL CROWN
ON LITERAL CUBIC SOURCE
=
IMPOSSIBLE

CRITICAL/CROWN AFTER REPRESENTATION CHANGE
=
MAY REAPPEAR

UNIVERSAL CONTEXTUAL DOMINANCE
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
