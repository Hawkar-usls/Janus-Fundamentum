# JANUS TRUMP R50G12 — reachable double-K5 debt saturation

## Scope

This note attacks only the minimal all-existing-doors-closed boundary left by R50G11. It does not infer universal progress from finite replay and does not claim SAT in P or P=NP.

Let `F` be a canonical persisted `W<=4` state, pre-BVE-clean under the frozen R33 priority. Let `x` be the first frozen R33 BVE pivot and suppose the proposal is an immediate W4 escape. Suppose same-pivot `R47J_x` ends nonterminal at width `>4` and every alternate pivot `y != x` has both existing doors closed:

- `R49H(F,y)` unauthorized;
- `R47J_SAFE(F,y)` false.

R50G11 already proves that every closed alternate pivot carries both `CHI_DEBT` and `R47J_DEBT`, and that any all-doors-closed obstruction has at least six total variables.

## The minimal boundary

Assume now

\[
|Vars(F)|=6.
\]

Write

\[
Vars(F)=\{x\}\cup A,\qquad |A|=5.
\]

Fix any alternate pivot `y in A`.

### Lemma 1 — closed R49H forces chi*=5

Because `F` has width at most four, R50G11 gives

\[
\chi^*(F,y)\le 6.
\]

But with exactly six total variables, an exact non-tautological cross-polarity resolvent on pivot `y` cannot contain `y`, cannot contain both signs of another variable, and has only five other variables available. Hence more sharply

\[
\chi^*(F,y)\le 5.
\]

Closed R49H means `chi_star>=5`. Therefore

\[
\boxed{\chi^*(F,y)=5.}
\]

Any width-five non-tautological witness must contain one literal from every variable in `Vars(F)\{y}`. In particular it contains the distinguished dangerous variable `x` and all four alternates in `A\{y}`.

### Lemma 2 — closed R47J forces final width exactly five

The frozen R47J candidate is exact DP plus certified normalization. For a bipolar pivot it removes `y` and introduces no fresh variables. Closed R47J_SAFE, after the already-proved structural predicates, means exactly

\[
J_y(F)\text{ is nonterminal and }W(J_y(F))>4.
\]

After removing `y`, at most five original variables remain. A non-tautological clause can therefore have width at most five. Hence

\[
\boxed{W(J_y(F))=5.}
\]

Any widest final clause uses every variable in `Vars(F)\{y}`. Thus it also contains `x` and all four alternates in `A\{y}`.

### Theorem — DOUBLE_K5_DEBT_SATURATION

Define two directed graphs on the five alternate variables `A`.

For each `y in A`, draw a CHI edge `y -> z` when `z` occurs in the selected width-five `CHI_DEBT` witness after excluding the distinguished variable `x`. Draw an R47J edge `y -> z` when `z` occurs in a width-five surviving final R47J clause after excluding `x`.

By Lemmas 1 and 2, for every `y` both support sets equal

\[
A\setminus\{y\}.
\]

Therefore

\[
\boxed{G_{\chi}=K_5^{\to}}
\]

and

\[
\boxed{G_{R47J}=K_5^{\to}},
\]

where `K5^->` is the complete directed graph without self loops. Equivalently every alternate pivot has exact outdegree four in both debt graphs.

This is stronger than the R50G11 minimum-outdegree/cycle reduction. At the minimal variable boundary, an all-doors-closed obstruction must be a **double-K5 saturated dependency core**.

## Frozen first-BVE ordering debt

The frozen R33 `bve_candidate` scans variables in ascending numeric ID. Its acceptance predicate for a bipolar pivot `y` is

1. number of distinct non-tautological resolvents `q_y` is at most the number of removed positive+negative parents `p_y+n_y`; and
2. the exact transformed formula strictly decreases frozen R33 measure `(C,L,V)`.

Pre-BVE cleanliness removes the pure-literal possibility, so every present variable is bipolar. Therefore if `x` is the first accepted BVE pivot, every present `y<x` must have failed at least one of those exact admission predicates before `x` was reached. Such a `y` carries an additional replayable `EARLIER_BVE_ORDER_DEBT`.

This conditional ordering debt is **not** itself a contradiction: if `x` is the smallest variable, there are no earlier pivots. It is retained because a future reachability-specific impossibility proof may force or exploit an earlier alternate pivot.

## Reachability control

A separately frozen sibling experiment (PR #417, run `33930214473`) already produced an exact one-step `U_mu` trace from a W3 predecessor to a W4 immediate-BVE state whose dangerous same-pivot R47J ends nonterminal at width five. Thus

\[
\boxed{REACHABLE\_SAME\_PIVOT\_W4\_SAFETY=REFUTED}.
\]

That reached state was nevertheless rescued by existing R49H pivots, so it does **not** refute `U_mu`. R50G12 independently reconstructs that control on the current branch to ensure the strengthened theorem starts from the correct status.

## Remaining obligation

The theorem above establishes only necessary saturation at `V=6`. It does not prove that double-K5 is unrealizable.

The next exact question is:

\[
\boxed{
\text{Can a pre-BVE-clean, U_mu-reachable immediate-BVE state realize both K5 debt systems while satisfying all frozen BVE-order/admission and clause-incidence constraints?}
}
\]

If no contradiction is proved, the correct status remains

`V6_DOUBLE_K5_REALIZABILITY_OR_EXCLUSION = OPEN`.

If an exact reachable V6 all-doors-closed witness is found, preserve the formula, predecessor/reachability certificate, every R49H chi witness, every independent R47J replay, both K5 ledgers, and the explicit OPEN receipt. Do not hide the counterexample.
