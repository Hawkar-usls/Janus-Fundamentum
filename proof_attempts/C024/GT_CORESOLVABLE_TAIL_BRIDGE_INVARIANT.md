# C024 — Co-resolvable tail-bridge invariant

Status: **FORMALIZING**  
Scope: pre-frontier exact residual keys of the deterministic Policy-0A execution on the graph-tautology family `GT_n`.

## 1. Correction of the previous theorem gate

The earlier wording

> every same-cut double-bridge pair leaves a directed cycle

was not a substantive finite conclusion.  The all-frozen-pair audit through
`GT_8` contains **zero same-cut double-bridge pairs**.  Therefore the directed-
cycle implication was vacuous on the reached family.

The corrected gate is stronger and cleaner:

> **Same-cut exclusion.**  In every pre-frontier exact residual key, no pair of
> component-spanning clauses containing complementary pivot literals can have
> that pivot as a bridge inducing the same component cut in both parents.

The finite evidence through `GT_8` supports this exclusion directly.

## 2. Component-clause definitions

Fix a live acyclic partial assignment and contract every connected component of
its undirected Hasse graph to one vertex.  For a residual clause `C`, let
`G(C)` be the undirected multigraph whose external literals are edges between
these component vertices.  Literal orientation is inherited from the ordered
comparison represented by that literal.

For a literal `l : u -> v` in `C`:

- `l` is a **bridge** when deleting its edge lowers the graphic rank of `G(C)`
  by one;
- it is **tail-singleton** when deleting it isolates the tail component `u` as
  one side of the bridge cut;
- it is **head-singleton** when deleting it isolates `v`;
- otherwise it induces a **non-singleton cut**.

A **co-resolvable double-bridge pair** is a pair of component-spanning clauses
`C,D` with `l in C`, `-l in D`, where both pivot occurrences are bridges.

## 3. Pure graph lemma — proved

### Lemma 3.1 — tail/tail complementary bridges have different cuts

Let `l : u -> v`.  If `l` is tail-singleton in `C`, its bridge cut isolates
`u`.  In the complementary parent, `-l : v -> u`; if `-l` is tail-singleton in
`D`, its bridge cut isolates `v`.

Since `u != v`, the two canonical bridge cuts are different.

### Lemma 3.2 — different bridge cuts preserve spanning rank

Let `C,D` both span all `m` component vertices and let the complementary pivot
be a bridge in both.  Removing the pivot from each parent creates two
bipartitions.  If the bipartitions differ, the union of both pivot-deleted
parent graphs is connected.  Hence the Resolution resolvent has graphic rank
`m-1` and is component-spanning.

Combining Lemmas 3.1 and 3.2:

```text
co-resolvable pair is tail/tail
        => bridge cuts differ
        => resolvent remains component-spanning
        => no unsafe acyclic low-rank resolvent is born.
```

No width bound or local-pass stopping budget is used in this implication.

## 4. Finite exhaustive evidence through GT_8

Across every pre-frontier exact cache key for `GT_4,...,GT_8`:

```text
component-spanning clause occurrences        7,918
bridge literal occurrences                   2,828
  tail-singleton                             2,766
  head-singleton                                18
  non-singleton cut                             44

complementary double-bridge parent pairs       611
  tail-singleton / tail-singleton               611
  any other bridge-role pair                      0
  different bridge cuts                         611
  same bridge cut                                  0
```

Thus the universal single-clause claim

> every spanning bridge is tail-singleton

is false: there are 62 explicit counterexamples.  The surviving property is
intrinsically **pairwise**.

For each of those 62 non-tail bridge occurrences, the complementary literal is
present in the same residual key.  However every component-spanning clause
containing that complement has it as a **non-bridge**:

```text
non-tail bridge occurrences                                  62
with a component-spanning complementary bridge                0
with only component-spanning complementary non-bridges       62
```

This gives the exact inductive formulation below.

## 5. Open GT-specific inductive lemma

### Co-resolvable Tail-Bridge Invariant

For every pre-frontier residual key `K`, every component-spanning clause `C` in
`K`, and every bridge literal `l in C`:

```text
if l is not tail-singleton,
then for every component-spanning D in K with -l in D,
-l is not a bridge of G(D).
```

Equivalent pair form:

```text
every complementary double-bridge pair in K is tail/tail.
```

This is exactly what remains to be proved asymptotically.

## 6. Proposed induction

The induction object cannot be an isolated clause.  It must be the residual-key
relation

```text
Shield_K(C,l) :=
    l is a non-tail bridge of C
    => every spanning complementary occurrence -l lies on an alternate
       component path and is therefore non-bridge.
```

The proof must cover three transitions.

### 6.1 Base GT axioms

- A non-minimality axiom is an oriented star.  Every bridge edge points away
  from its isolated tail, so all its bridge literals are tail-singleton.
- A transitivity axiom projects to a directed triangle, a contracted cycle, or
  an internal clause.  A complementary occurrence capable of shielding a
  non-tail bridge therefore has an explicit alternate path at the base level.

The base case should be written directly on the component quotient, including
contractions caused by the current partial order.

### 6.2 Restriction and component contraction

A branch or unit assignment can delete satisfied clauses, remove falsified
literals, and contract component vertices.  The induction must show that if a
non-tail bridge is created by this transition, every surviving spanning
complementary clause still contains an alternate path avoiding its pivot.

This is the first unresolved preservation case.  Literal deletion cannot be
silently treated as a proof inference; the residual-clause provenance layer
must identify which source edges survived and which component contractions
occurred.

### 6.3 One-pass local Resolution

Fresh resolvents are not eligible as parents again in the same state.  Hence a
new clause can threaten the invariant only in the next residual key, after
post-units and a branch transition.

The required step is:

```text
if a fresh/inherited clause acquires a non-tail bridge l,
then every simultaneously surviving spanning complement -l
contains a pivot-avoiding path.
```

The finite blocker census suggests that this path is not accidental: every one
of the 62 counterexamples has at least one explicit spanning complementary
clause in which the pivot is cycle-redundant.

## 7. Consequence if the invariant is proved

The co-resolvable tail-bridge invariant, together with the graphic-rank lemmas,
would imply that one-pass local Resolution cannot create an unsafe acyclic
low-rank clause before the historical frontier.  Component merges caused by a
learned clause would then remain charged either to novel branches or to explicit
rank-losing Resolution ancestry, while exact cache keys preserve the historical
restriction separation.

A separate counting argument would still be required to transfer the full
Formula-Caching lower bound and state its asymptotic exponent precisely.

## 8. Falsification conditions

The invariant is rejected by any pre-frontier key containing:

1. component-spanning `C,D` with complementary pivot bridges not both
   tail-singleton;
2. equivalently, a non-tail bridge whose complement is also a bridge in a
   component-spanning clause;
3. a restriction or unit-contraction step that destroys every alternate path
   shielding the complementary pivot while preserving both parents;
4. a one-pass resolvent that enters the next key with such an unshielded pair.

The executable certificate searches directly for conditions 1 and 2 through
`GT_8`.  A provenance/path-lifecycle checker is required for conditions 3 and
4.

## Claim boundary

This note proves the elementary graph consequences of the pairwise tail-bridge
condition and records an exhaustive finite invariant through `GT_8`.  It does
**not** prove the GT-specific induction for arbitrary `n`, does not yet transfer
the asymptotic Formula-Caching lower bound to Policy-0A, and does not resolve
`P` versus `NP`.
