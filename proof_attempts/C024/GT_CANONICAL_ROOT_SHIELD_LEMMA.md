# C024 — Canonical root-shield lemma

Status: **FORMALIZING**  
Scope: pre-frontier exact residual keys of the deterministic Policy-0A run on `GT_n`.

## 1. Reduction from pairwise bridge safety

The co-resolvable tail-bridge certificate established the correct finite
pairwise invariant through `GT_8`:

```text
non-tail bridge l in a spanning clause C
    => every spanning complementary occurrence -l is a non-bridge.
```

The remaining question is why the complementary occurrence is always shielded.
The trace exposes a canonical shield already present in the original formula.

## 2. Root non-minimality clauses

For every vertex `a`, the graph-tautology formula contains the axiom

```text
N_a = OR_{x != a} (x -> a),
```

asserting that `a` has a predecessor.

Let `l : a -> b`.  The complementary literal `-l : b -> a` belongs to `N_a`.
Thus any structural reason that keeps another vertex `c` in the same current
Hasse component as `b`, while `a` remains in a different component, produces a
quotient-parallel edge `c -> a` beside `b -> a` inside `N_a`.

## 3. Pure root-shield lemma — proved conditionally

### Lemma 3.1 — singleton tail leaves `N_a` untouched

Assume the current Hasse component of `a` is the singleton `{a}`.  Any assigned
comparison between `a` and another vertex `x`, regardless of truth value, adds
the undirected comparison edge `{a,x}` and therefore places `a` and `x` in the
same Hasse component.  This contradicts singletonhood.

Hence no comparison involving `a` has been assigned.  Every literal of `N_a`
therefore survives restriction, and

```text
N_a | alpha = N_a.
```

In particular `N_a` is unsatisfied and remains an exact root clause in the
residual key.

### Lemma 3.2 — merged head supplies parallel shield edges

Assume additionally that the Hasse component `B` containing `b` has size at
least two.  Choose `c in B`, `c != b`.  Since `a` is outside `B`, both literals

```text
b -> a
c -> a
```

remain external literals of the untouched clause `N_a`.  After quotienting the
Hasse components, both are parallel edges between `{a}` and `B`.

Consequently deleting `b -> a` leaves `c -> a`; the complementary pivot is not
a bridge in `N_a`.

More precisely, the number of quotient-parallel alternatives to `b -> a` in
`N_a` equals

```text
|B| - 1.
```

### Corollary 3.3 — canonical root shield

If a non-tail bridge `l : a -> b` satisfies

```text
component(a) = {a}
and
|component(b)| >= 2,
```

then the untouched root axiom `N_a` is a component-spanning complementary
parent in which `-l` is a non-bridge.  Therefore `l` cannot participate in a
same-cut complementary double-bridge pair.

This argument uses no width limit, Resolution budget, parent enumeration order,
or learned-clause ancestry.

## 4. Exhaustive finite certificate through GT_8

Every one of the 62 non-tail bridge occurrences has exactly this form:

```text
non-tail bridge occurrences                 62
singleton tail component                    62
head component of size at least two         62
untouched root non-minimality axiom N_a      62
exact parallel multiplicity |B|-1           62
```

The joint histograms are:

```text
head component size       2   3   4   5
occurrences              12  21  17  12
parallel alternatives     1   2   3   4
occurrences              12  21  17  12
```

The broader path audit finds 119 complementary alternate paths, but the root
shield is canonical: exactly one untouched `N_a` witness exists for each bad
bridge occurrence.  Other inherited complementary clauses provide redundant
one- or two-edge shields.

## 5. The sole remaining structural lemma

### Singleton-tail / merged-head birth lemma

For every pre-frontier exact residual key and every component-spanning clause
containing a bridge literal `l : a -> b` that is not tail-singleton:

```text
component(a) = {a}
and
|component(b)| >= 2.
```

The second condition is nearly definitional once the bridge is not
 tail-singleton and the first condition is known: the finite traces show that
all non-tail bridges point from an untouched singleton vertex into a component
created by earlier novel contractions.

Thus the real arbitrary-`n` burden is:

> **A pre-frontier non-tail bridge can never have a non-singleton tail Hasse
> component.**

Once this is proved, Lemmas 3.1–3.2 supply the root shield automatically and the
same-cut obstruction disappears.

## 6. Proposed birth/lifecycle induction

Track the first call at which a fixed clause occurrence and literal become a
non-tail bridge.

Possible birth mechanisms are:

1. **Fresh local resolvent.**  The resolvent is born after the one-pass local
   stage.  It cannot be used as a parent again in that state.
2. **Branch contraction.**  An inherited clause changes bridge geometry when a
   novel branch contracts two Hasse components.
3. **Unit contraction.**  A pre- or post-local unit merges components before the
   next exact key.
4. **Literal restriction.**  A falsified literal is deleted while the remaining
   quotient graph becomes a bridge structure.

The lifecycle verifier must determine which mechanisms actually occur and
prove that each first birth merges the head side while leaving the oriented
tail vertex untouched.  A counterexample is any first birth with tail component
size greater than one.

## 7. Consequence for C024

The singleton-tail / merged-head birth lemma plus the already proved graph-rank
lemmas would imply:

```text
no unsafe acyclic low-rank resolvent is born before the historical frontier.
```

This closes the local structural obstruction.  A final global counting step is
still required to transfer the historical Formula-Caching lower bound to the
exact Policy-0A execution and state the asymptotic bound rigorously.

## Claim boundary

The root-shield implication is a direct graph argument, and its hypotheses are
exhaustively certified through `GT_8`.  The arbitrary-`n` singleton-tail birth
lemma and the final lower-bound transfer remain open.  Nothing here resolves
`P` versus `NP`.
