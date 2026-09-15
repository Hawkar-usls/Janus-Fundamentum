# C024 — Exact Classification of the Unsafe Resolution Route

## Status

**PROVED — pure quotient-graph theorem.**

Assume both Resolution parents belong to the branch-safe structural family:

```text
DIRECTED_CYCLE
OR COMPONENT_SPANNING
OR INTERNAL_ONLY.
```

Then a legal non-tautological resolvent can be
`UNSAFE_ACYCLIC_LOW_RANK` only through one exact route:

```text
COMPONENT_SPANNING + COMPONENT_SPANNING
with an external pivot that is a bridge in both parents
and induces the same undirected component cut in both.
```

The same-cut double-bridge condition is necessary, not sufficient: a directed
cycle may still survive inside one side of the cut.

## Quotient setting

Fix one residual state and contract the connected components of its current
Hasse diagram.  External literals are directed edges between quotient vertices;
internal literals are loops for the connectivity analysis.

Let the parents contain complementary pivot literals `p` and `-p`, and let

```text
R = (A \ {p}) union (B \ {-p})
```

be a legal, non-tautological resolvent after duplicate removal.

## Case 1 — an internal-only parent

Suppose `A` is internal-only.  Its pivot `p` is internal, so the comparison
endpoints lie in one quotient component.  The complementary pivot `-p` in `B`
is therefore internal as well.  Removing it cannot alter the external quotient
graph of `B`, while `A \ {p}` contributes no external edge.

Hence the external graph of `R` contains exactly the external graph of `B`.
The resolvent preserves whichever safe class `B` had.  The same argument is
symmetric, and two internal-only parents remain internal-only.

## Case 2 — two directed-cycle parents

Choose a directed cycle `Z_A` in `A` and a directed cycle `Z_B` in `B`.

- If `Z_A` avoids `p`, it survives in `R`.
- If `Z_B` avoids `-p`, it survives in `R`.
- Otherwise `Z_A - {p}` is a directed path from the head of `p` back to its
  tail, while `Z_B - {-p}` is a directed path in the opposite direction.
  Their union is a directed closed walk and therefore contains a directed
  cycle.

Legality of the resolvent excludes opposite-literal cancellation, and duplicate
removal cannot destroy the resulting cycle.  Thus cycle/cycle resolves to a
clause containing a directed cycle.

## Case 3 — one spanning parent and one cycle parent

This is the Spanning/Cycle Resolution Closure lemma.

If deleting the pivot from the spanning parent leaves it connected, its
remaining edges already span the quotient.  Otherwise the pivot is a bridge and
defines a cut `S|T`.  If the resolvent were disconnected, the cycle parent would
have no non-pivot edge across that cut.  A directed cycle using the complementary
pivot must cross the cut again, contradiction.  Therefore either the resolvent
is spanning or a pivot-avoiding directed cycle survives.

## Case 4 — two component-spanning parents

If the pivot is internal in either parent, deleting it does not change that
parent's quotient connectivity, so `R` is spanning.

Assume the pivot is external.  If it is not a bridge in at least one parent,
that parent remains connected after pivot deletion, so `R` is spanning.

The only remaining possibility is that the pivot is a bridge in both parents.
Deleting it gives two connected sides in each parent.  Let the corresponding
undirected cuts be

```text
S_A | complement(S_A)
S_B | complement(S_B).
```

Suppose the cuts differ up to complementation.  If the union

```text
(A \ {p}) union (B \ {-p})
```

were disconnected, any connected component of that union would have to be a
union of connected components of `A \ {p}` and also a union of connected
components of `B \ {-p}`.  Each deletion graph has exactly two connected
components, so a nontrivial union component must equal one side of both cuts.
That would make the cuts equal up to complementation, contrary to assumption.

Therefore different bridge cuts force the resolvent to be component-spanning.
A non-spanning resolvent is possible only when the two bridge cuts are the same.
For the resolvent to be unsafe rather than cycle-safe, it must additionally be
acyclic.

## Exact obstruction theorem

A legal Resolution inference between branch-safe parents can produce an unsafe
acyclic low-rank resolvent only if all of the following hold:

1. both parents are component-spanning;
2. the pivot is external;
3. the pivot is a bridge in both parents;
4. the two bridge deletions induce the same quotient cut; and
5. the union after pivot deletion contains no directed cycle.

Items 1–4 are the unique graph-rank route.  Item 5 distinguishes an actually
unsafe resolvent from a same-cut resolvent that remains protected by a cycle.

## Minimal generic witness

On three quotient components:

```text
A = {0->1, 2->1}
B = {1->0, 2->1}
pivot = 0->1 / 1->0
R = {2->1}
```

Both parents are component-spanning.  The pivot is a bridge in both and induces
the same cut isolating component `0`.  The resolvent is acyclic and has rank one
instead of the spanning rank two.

Thus the obstruction is real in abstract graph clauses; excluding it requires
GT-specific reachability or ancestry structure.

## Consequence for C024

All parent classes involving a cycle or an internal-only clause are now closed
by pure graph arguments.  The arbitrary-`n` local theorem gate is exactly:

> No parent-eligible pre-frontier GT residual contains a co-resolvable pair of
> component-spanning clauses whose complementary pivot is a bridge in both and
> induces the same quotient cut.

A sufficient strengthening, supported by the finite census, is:

> Every co-resolvable double-bridge pair is tail-singleton in both parents.

Complementary tail-singleton orientations isolate opposite endpoints and hence
produce different cuts.

The lexicographic singleton-tail handoff and canonical root shield remain
candidate mechanisms for proving that sufficient strengthening.

## Claim boundary

This theorem classifies one Resolution step on a fixed quotient.  It does not
prove the GT-specific same-cut exclusion for arbitrary `n`, the global cache
frontier transfer, an unrestricted proof-complexity lower bound, or `P != NP`.
