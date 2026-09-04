# JANUS TRUMP R50G6 — Immediate-BVE same-pivot terminality: exact composition lemmas

## Target

The deliberately stronger candidate is

\[
\operatorname{IMMEDIATE\_BVE\_ESCAPE}(F,x)\Rightarrow \operatorname{TERMINAL}(R47J_x(F)).
\]

R50G5 already closed the source-level facts that the same pivot exists, exact DP replay passes, the polynomial per-transition envelope passes, CLV strictly descends, no fresh variables are introduced, the pivot is eliminated, and strict variable descent holds. Therefore machine safety for the same pivot is exactly `TERMINAL OR final_width<=4`.

This note asks whether **terminality itself** follows.

## Lemma 1 — observed R50G5 terminality is R33-direct, not affine/RUP

The frozen R50G5 synthesis reported 29 reachable immediate-BVE states and 29 same-pivot terminals. The terminal label in every recorded row is `DIRECT_EMPTY_CNF`. In R47J this label can arise only when the first certified R33 normalization after DP reduces the formula to the empty CNF. Therefore the observed 29 examples do not require affine recognition or RUP for terminality.

This is evidence about those states only; it is not a universal theorem.

## Lemma 2 — exact DP is component-local on disjoint conjunctions

Let

\[
F=A\land B,\qquad Vars(A)\cap Vars(B)=\varnothing,
\]

and let `x in Vars(A)`. Every positive/negative parent containing `x` lies in `A`; no clause of `B` contains `x`. Hence all cross-polarity resolvents for DP on `x` are generated entirely from `A`. Therefore before subsumption

\[
DP_x(A\land B)=DP_x(A)\land B.
\]

For nonempty clauses over disjoint variable sets, a clause from one component cannot subsume a clause from the other. Thus subsumption minimization also factorizes unless an empty clause is produced. In the SAT component used by the frozen composition test no empty clause is produced.

## Lemma 3 — the R33 rules before BVE preserve component separation

For disjoint `A` and `B`:

* tautology is clause-local;
* unit propagation touches only clauses containing the unit variable;
* pure-literal polarity is determined only by clauses containing that variable;
* subsumption cannot cross two nonempty disjoint-variable clauses;
* blocked-clause testing for literal `l` consults only clauses containing `-l`, hence only the same component;
* BVE parent sets for pivot `x` lie entirely in the pivot component.

Consequently if `A` has immediate BVE as its first R33 micro-proposal and `B` is an R33 fixed point with all variable ids shifted above those of `A`, the same BVE proposal remains first in `A AND B`.

## Lemma 4 — local BVE geometry alone cannot force global terminality

Suppose there exists:

1. a SAT immediate-BVE component `A` whose same-pivot normalization removes/solves the `A` component; and
2. a disjoint component `B` which is already a certified R47J normalization fixed point and is nonterminal.

Then exact same-pivot DP on `A AND B` leaves `B` untouched. Certified normalization may eliminate the solved `A` residue, but it has no local reason to remove a normalization-fixed `B`. Therefore the final formula is nonterminal whenever `B` survives.

Thus

\[
\boxed{\text{IMMEDIATE BVE LOCAL GEOMETRY ALONE} \not\Rightarrow \text{GLOBAL TERMINALITY}}
\]

if the frozen exact composition witness succeeds.

This does **not** refute the reachability-scoped theorem. A composite all-W4 state is a reachable counterexample only if reachability under the exact `U_mu` trajectory is independently proved.

## Consequence if the composition witness succeeds

The over-strong theorem must be abandoned, not patched:

\[
\operatorname{IMMEDIATE\_BVE\_ESCAPE}\not\Rightarrow\operatorname{TERMINAL}
\]

on arbitrary W4 states.

The mathematically relevant remaining target then returns to the exact machine condition already isolated by R50G5:

\[
\boxed{
\operatorname{IMMEDIATE\_BVE\_ESCAPE}(F,x)
\Rightarrow
\bigl(\operatorname{TERMINAL}(R47J_x(F))\lor W(R47J_x(F))\le4\bigr)
}
\]

for the required reachable domain, or a certified alternate door.

No heuristic, statistical selector, or new inference rule appears in this reduction.
