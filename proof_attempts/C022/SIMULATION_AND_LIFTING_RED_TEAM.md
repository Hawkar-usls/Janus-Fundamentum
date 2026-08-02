# C022 red-team audit — simulation and lifting chain

## Status

`TWELVE ATTACK CLASSES / NO DECISIVE COUNTEREXAMPLE FOUND / PEER REVIEW STILL REQUIRED`

This document records attacks against the proposed Policy-0T lower-bound chain.
Passing an attack means only that the named failure mode has been addressed; it
does not turn an internal proof into an externally accepted theorem.

## A. Trace-to-Resolution simulation

### A1 — hidden weakening under residual simplification

**Attack.** A residual clause is shorter than its root clause. Treating that
shorter clause as already proved would use weakening in reverse.

**Disposition.** The translator stores the root-derived clause and uses the
shorter restriction only to replay execution. Every local event verifies that
restricting the root resolvent gives the recorded residual. No residual clause
is inserted as a proof axiom.

### A2 — root resolvent becomes tautological although residual resolvent is legal

**Attack.** Extra literals deleted by the assignment might create a hidden
complementary pair in the lifted root resolvent.

**Disposition.** If the complementary variable is assigned, one parent would
contain its true literal and would be satisfied, contradicting survival under
restriction. If it is unassigned, the pair remains in the residual resolvent and
the local policy rejects the event as tautological. Thus a recorded event lifts
to a non-tautological root resolvent.

### A3 — unit reason contains another unit from the same batch

**Attack.** Sequential replay of a simultaneous unit batch may invalidate later
reasons.

**Disposition.** A reason restricting to the unit `(l)` before the batch cannot
contain any other currently unassigned batch literal; otherwise its restriction
would not be unit. It may contain the opposite of another batch literal, which
remains false after that assignment. Reverse chronological reason elimination
therefore remains legal.

### A4 — opposite units need semantic contradiction rather than Resolution

**Attack.** Two residual units may arise from long root clauses and resolving
those roots may produce a tautology or unrelated clause.

**Disposition.** Every non-pivot literal in both root reasons is false under the
current assignment. Complementary non-pivot assigned literals cannot occur,
because one would be true in its parent. Resolving the reasons yields a clause
falsified by the current assignment.

### A5 — duplicate residuals lose required provenance

**Attack.** Canonical merging keeps only one root witness for a residual, while a
later local event might need another.

**Disposition.** A local event depends only on the residual clause content and
pivot. Any root-derived witness restricting to that same residual satisfies the
restriction-commutation lemma. The finite translator keeps one witness and all
recorded events replay.

### A6 — sibling conflicts require weakening to a common decision clause

**Attack.** Child conflicts may be different subclauses and cannot be combined.

**Disposition.** If both retain opposite branch literals, Resolution combines
them. If one omits its branch literal, it is already a derived subclause of the
parent boundary and can be returned directly. Full-boundary weakening is never
required.

### A7 — immediate branch conflict is an uncovered terminal rule

**Attack.** `simplify_one` may return an empty clause before a recursive child
exists.

**Disposition.** Exhaustive unit propagation precedes every branch, so every
remaining clause has width at least two. One assignment deletes at most one
literal from an unsatisfied clause; immediate empty restriction is unreachable.

### A8 — proof size counts a unit or branch more than once

**Attack.** A local unit above a branch may have to be eliminated separately in
both child proofs, breaking `S <= m+r+u+b+o`.

**Disposition.** Child conflicts are first combined at the node. Units assigned
inside that node are eliminated only once from the combined clause. Each trace
unit occurrence emits at most one reverse-reason line; each branch node emits at
most one combination line.

### A9 — proof depth sums both child depths

**Attack.** Combining two subproofs might add their depths rather than their
maximum.

**Disposition.** Resolution proof depth is longest-path depth. A branch line has
depth one plus the maximum of its two parents. A dependency path follows one
root-to-leaf execution path, not both. Local one-pass stages add at most one
layer per visited search node.

### A10 — traced policy is not production Policy0T

**Attack.** The proof applies to an instrumented clone rather than the registered
solver.

**Disposition.** A deterministic differential audit compares 500 non-affine
UNSAT formulas and matches answers, recursive calls, expanded states, branch
edges, terminal calls, maximum depth, Resolution attempts and Resolution
additions exactly. This is finite evidence; source-level review remains useful.

## B. MAJ3 lifting application

### B1 — affine dispatcher reactivates on larger lifted instances

**Attack.** K4 and K3,3 may be accidental non-affine fixtures.

**Disposition.** For every degree and charge, fixing all other gadget blocks
slices the local relation to one non-affine MAJ3 fibre. Hence the whole local
relation is non-affine. The implemented detector is audited for both charges and
degrees one through four, covering the constant-degree families used by the
route.

### B2 — JANUS direct relation encoding differs from theorem lift encoding

**Attack.** Logical equivalence is insufficient for proof complexity; a
polynomial translation between encodings was not charged.

**Disposition.** The clause-wise standard CNF disjunction from the lifting
definition and the JANUS direct exact local relation encoding have identical
canonical clause sets for both charges and degrees one through four. The general
identity follows because each false lifted assignment contributes exactly its
unique full forbidden-assignment clause.

### B3 — parameter substitution reverses the lower-bound inequality

**Attack.** From `D >= Omega(w^2/log S)` and `D=O(n)`, one might incorrectly infer
an upper rather than lower bound on size.

**Disposition.** With `w>=cn` and `D<=An`:

```text
An >= k c^2 n^2 / log S,
log S >= (k c^2/A)n,
S >= 2^{Omega(n)}.
```

Since the simulation gives `S <= aW`, it follows that `W >= S/a` and hence
`W=2^{Omega(n)}`. Constant-degree, constant-gadget encoding gives input length
`L=Theta(n)`.

## Automated pressure

The current workflow runs:

- four hand-designed terminal/branch classes;
- 500 deterministic random non-affine UNSAT translations;
- 500 production-versus-trace differential comparisons;
- an independent serialized proof checker with four mutation classes;
- exact numerical size/depth audits;
- MAJ3 non-affinity and exact encoding-match audits.

## Remaining external gates

1. independent mathematical review of the universal induction;
2. review that the cited base expander-Tseitin family has the required linear
   Resolution width in the theorem's parameter convention;
3. review of the 2026 lifting theorem's exact size/depth and encoding premises;
4. a search for transition classes absent from the registered production code;
5. an attempted explicit shallow polynomial-size `Res(⊕)` proof of the lifted
   family.

## Claim boundary

No counterexample was found within these attack classes. That is not a proof of
novelty, unrestricted lower bounds, or `P != NP`. The target is an exponential
lower bound for one exact non-affine Policy-0T core.
