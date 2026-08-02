# H120 — witness-cover upper bound against positive anti-checkers

## Status

`FORMALIZING`, reproducibility `R2`.

This is a structural upper bound on circuits covering a positive list. It does
not refute H116 by itself because H116 may output more witness diversity than
the target circuit budget.

## Fixed input model

Fix one padded canonical CNF encoding length `L`, at most `v` variables, a fixed
clause count, and a fixed maximum width. For every assignment
\(a\in\{0,1\}^v\), there is a Boolean circuit

\[
\operatorname{Eval}_{a,L}(F)
\]

of size polynomial in `L+v` that parses the fixed-shape encoding and outputs one
exactly when `a` satisfies `F`.

The assignment is hardwired, so no SAT search is performed.

## Cover circuit

Let

\[
T=\{(F_i,a_i):1\le i\le m\}
\]

be a positive list with every `a_i` satisfying `F_i`. Let `A_T` be the set of
distinct assignments occurring in the list.

Define

\[
C_T(F)=\bigvee_{a\in A_T}\operatorname{Eval}_{a,L}(F).
\]

### Soundness

If `C_T(F)=1`, then one of the hardwired assignments satisfies `F`. Therefore
`F` is satisfiable. The circuit is globally SAT-sound, not merely correct on
the list.

### Coverage

For every listed pair `(F_i,a_i)`, the disjunct corresponding to `a_i` accepts
`F_i`. Hence `C_T` accepts the entire positive list.

### Size

If one fixed-assignment evaluator has size `e(L,v)`, then

\[
|C_T|=O(|A_T|\,e(L,v)).
\]

A straightforward evaluator has `e(L,v)=poly(L,v)`.

## Necessary condition for H116

Suppose an H116 list is intended to hit every SAT-sound circuit of size at most
`s(n)=n^k`. The witness-cover circuit above must exceed that budget. Therefore,
up to the fixed encoding constants,

\[
|A_T|\,e(L,v)>n^k.
\]

Repeating formulas, repeating witnesses, or producing many formulas all
satisfied by a small common assignment set cannot establish H116.

The constructor must create enough distinct witness behavior that even the
union of all hardwired witness evaluators exceeds the target circuit size.

## Executable audit

```bash
python experiments/direct/sound_witness_cover.py --self-test
```

The fixture verifies that two hardwired assignments cover four listed positive
formulas while rejecting a contradiction. It is finite implementation evidence,
not an asymptotic circuit lower bound.

## Remaining wall

Even high witness diversity is only necessary. A smaller SAT-sound circuit may
compress the same positive family through a semantic property unrelated to the
listed witnesses.

A successful descendant must prove incompressibility against **all** SAT-sound
circuits, not just witness-union circuits.

## Claim boundary

H120 does not prove `SAT not in P/poly` or `P != NP`. It narrows H116 by making
one universal covering attack and its size accounting explicit.
