# C024 — Singleton-branch same-cut preservation

Status: **PURE QUOTIENT/ENCODING LEMMA PROVED / GT SELECTOR REACHABILITY OPEN**  
Scope: one Policy-0A branch restriction from a post-result `P` to the raw child `B`.

## 1. Setting

Fix the current relation quotient and assume the selected comparison variable
joins two distinct quotient components

```text
U = {u},
V = {v},
```

both singleton in original GT vertices.  A branch polarity assigns the unique
comparison variable `x_{u,v}`, restricts every clause, and contracts `U,V` to
one relation component `UV`.

Assume every clause before the branch belongs to the branch-safe family

```text
DIRECTED_CYCLE
or COMPONENT_SPANNING
or INTERNAL_ONLY.
```

The claim concerns clauses which survive CNF restriction.  A satisfied clause
is extinct and therefore harmless.

## 2. Directed-cycle persistence

### Lemma 2.1

A surviving non-tautological clause containing a directed quotient cycle before
the singleton branch still contains a directed quotient cycle after restriction
and contraction.

### Proof

Choose a directed cycle `Z` in the source clause.

If `Z` avoids the selected comparison literal, contracting `U,V` maps `Z` to a
directed closed walk.  A directed closed walk contains a directed cycle unless
all of its edges become internal loops.

If `Z` contains the selected literal with the falsified polarity, restriction
removes that literal.  The remaining directed path goes from one endpoint of
the selected comparison back to the other.  Contracting `U,V` closes that path
into a directed closed walk.

The only way for the resulting closed walk to have no external edge is for the
original cycle to have exactly two quotient vertices, both `U` and `V`.  Such a
directed two-cycle requires two distinct surviving literals with opposite
orientations between `U` and `V`.  Because both components are singleton,
there is only one GT comparison variable between them.  The two orientations
would therefore be complementary literals of the same variable, making the
source clause tautological.  Legal Policy-0A clauses exclude this case.

Hence at least one external directed cycle survives. ∎

```text
SINGLETON_BRANCH_DIRECTED_CYCLE_PERSISTENCE = PROVED
```

## 3. Spanning and bridge-cut reflection

Contraction preserves connectedness, so every surviving component-spanning
clause remains component-spanning.

Let a tracked literal `l` be a bridge after contraction.  Then `l` was already
a bridge before contraction.  Otherwise a pivot-avoiding path between its
endpoints would map to a pivot-avoiding walk after contraction, leaving `l`
non-bridge.  Parallel quotient edges are retained as distinct literals; they
cannot be silently collapsed into one bridge.

Moreover, if `l` remains a bridge, `U` and `V` were on the same side of its
source cut.  If they were on opposite sides, identifying them would reconnect
the two deletion components and make `l` non-bridge.  Therefore the child cut
has a unique source lift: replace `UV` by `{U,V}` on the same side.

Consequently, if two surviving spanning clauses have complementary bridge
literals with the same child cut, their source bridge cuts were already equal.
A singleton contraction cannot turn two different source cuts into one
same-cut pair.

```text
SINGLETON_BRANCH_SPANNING_CUT_REFLECTION = PROVED
```

## 4. Internal-only clauses

A clause with no external quotient edge cannot acquire one under restriction
and contraction.  It remains internal-only or becomes extinct.

## 5. Preservation theorem

### Singleton-Branch Same-Cut Preservation

Assume the pre-branch family is branch-safe and contains no co-eligible
same-cut complementary double-bridge pair.  If the selected comparison joins
two singleton relation components, then the raw child family also contains no
same-cut complementary double-bridge pair.

### Proof

- A cycle-bearing source remains cycle-bearing by Lemma 2.1 and cannot become a
  component-spanning bridge parent.
- A surviving spanning bridge and its cut reflect uniquely to the source by
  Section 3, so a child same-cut pair would lift to a forbidden source pair.
- Internal-only clauses cannot become external parents.
- Satisfied clauses disappear.

Thus no new same-cut pair is born. ∎

```text
SINGLETON_BRANCH_SAME_CUT_PRESERVATION = PROVED
```

## 6. Exact finite non-root instantiation

All three non-root unshielded `GT_8` occurrences select variable `8`, whose
comparison joins the singleton relation components of original vertices `1`
and `2`.  Therefore the theorem already blocks Route B — birth of a new
same-cut pair — independently of the stronger two-node tail-wing geometry.

The Two-Node Tail-Wing Handoff remains useful because it classifies the tracked
clause itself:

```text
one polarity   -> CLAUSE_EXTINCT;
other polarity -> TAIL_SINGLETON_SAFE.
```

But same-cut noncreation needs only singleton selected endpoints.

## 7. Sharpened remaining GT gate

The sufficient non-root reachability obligation can now be weakened to:

### Non-Root Singleton-Branch Reachability

For arbitrary `n`, every reachable non-root immediate-local unshielded
occurrence is already handled by another proved safe route, or the exact
Policy-0A selected comparison joins two singleton relation components.

The previously proposed two-node tail-wing and one-subdivision producer normal
forms imply this condition but are stronger than necessary.

A falsifier is a reachable non-root unshielded occurrence whose selected
comparison joins a non-singleton relation component and which is not extinct,
bridge-destroyed, canonically shielded, or otherwise covered by an existing
safe route.

## Claim boundary

The cycle-persistence, cut-reflection, and singleton-branch preservation
statements are proved under their explicit legal-clause and singleton-endpoint
hypotheses.  Arbitrary-`n` GT reachability of the singleton selected branch,
complete T2b/T3, the global cache-DAG lower bound, unrestricted SAT lower
bounds, and `P` versus `NP` remain open.
