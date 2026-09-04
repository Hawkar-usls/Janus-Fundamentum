# JANUS TRUMP R50G10 — one-step reachability lift and all-doors audit

## Motivation

R50G9 exactly refuted the all-W4 same-pivot safety shortcut by a deterministic width-4 source whose immediate BVE escape ends at a nonterminal width-5 normalization fixpoint. The only remaining question is whether that obstruction is excluded by the actual U_mu reachability domain or merely absent from the earlier finite reachable replay.

R50G10 turns that into a direct exact dichotomy.

## One-step lift

Take the R50G9 even-charge prism core K, shifted by +100. Relabel the dangerous R50G9 pivot from 1 to x=2. The reached W4 state is

F = K AND (2,-101,-102,-103) AND (-2,-104,-107).

Now replace the width-4 positive x-parent by two width-3 clauses using a new predecessor pivot y=1:

A = (1,2,-101)

B = (-1,-102,-103).

Define the W3 root

G = K AND A AND B AND (-2,-104,-107).

Exact DP/BVE on y resolves A and B to

(2,-101,-102,-103),

so if y is the first frozen R33 rule and the step is authorized, U_mu reaches F in one transition.

The construction is not a search and does not add a semantic rule. It is an exact inverse-factorization of one width-4 clause into two width-3 parents.

## What must be checked

The frozen execution must establish from source definitions, not by assumption:

1. W(G)<=3 and G is pre-BVE-clean.
2. The first frozen R33 microstep on G is BVE on y=1.
3. Its exact successor is F and remains within W<=4, hence receives U_mu authority.
4. At F, the first R33 microstep is immediate BVE escape on x=2.
5. Same-pivot R47J on x reproduces the R50G9 nonterminal W5 fixpoint.
6. The independent all-doors audit checks R49H and every frozen R47J pivot at F.
7. `refined_exact_step(F)` agrees with that exact audit.

## Exact dichotomy

If every R49H/R47J door is blocked, F is an explicit U_mu-reachable OPEN state. That refutes universal progress of the current refined controller U_mu. It does **not** prove P!=NP; it only refutes this specific proposed polynomial exact machine.

If an existing certified door succeeds, then the result is still decisive: reachable same-pivot safety is refuted, but the wider guarded-door theorem survives this witness. The proof target then returns to

`IMMEDIATE_BVE_ESCAPE => EXISTS_EXISTING_CERTIFIED_DOOR`

rather than the now-false stronger same-pivot theorem.

In both cases the experiment changes the mathematical frontier rather than merely enlarging a corpus.
