# JANUS TRUMP R50G10 — wide fixpoint forces alternate certified door

## Target

For a reachable persisted `W<=4` state `F` whose first frozen R33 microstep is an immediate BVE escape on pivot `x`, assume same-pivot R47J ends nonterminal with final width `>4`. The target is

\[
\exists y\ne x:\quad R49H(F,y)\lor R47J_{SAFE}(F,y).
\]

R50G9 refuted the stronger local statement that same-pivot R47J must itself be safe. The local witness nevertheless had many alternate doors, so R50G10 isolates exactly what an all-doors-closed counterexample must contain.

## L1 — pre-BVE cleanliness makes every present variable bipolar

The frozen first-rule order checks pure-literal autarky before BVE. Therefore at an immediate-BVE source there is no pure literal. Every variable present in the formula occurs with both signs. Hence every current variable is bipolar.

## L2 — exact characterization of a closed R49H door

For a bipolar pivot `y`, R50A authorizes the R49H direct DP token exactly when

\[
\chi^*(F,y)\le 4,
\]

where `chi*` is the maximum size of a retained non-tautological cross-polarity residual union. Thus at a pre-BVE-clean source

\[
\neg R49H(F,y)\iff \chi^*(F,y)\ge 5.
\]

So closing every alternate R49H door gives, for every `y != x`, an explicit retained parent-pair witness of width at least five.

## L3 — arbitrary bipolar R47J pivot removes its pivot and introduces no fresh variables

R47J starts with exact DP on `y`. Exact DP deletes all parents containing `±y`, adds only resolvents over literals already present in those parents, and therefore introduces no fresh variable. The frozen normalization stack consists of R33 reductions, affine recognition/terminal solving, and RUP strengthening/restarts; none introduces a fresh variable. The eliminated pivot is not reintroduced.

Therefore for every bipolar current pivot `y`:

\[
Vars(J_y(F))\subseteq Vars(F)\setminus\{y\}.
\]

In particular, strict variable descent and no-fresh-variable conditions are automatic whenever the R47J candidate exists.

## L4 — exact characterization of a closed R47J_SAFE door

Because L3 discharges the structural safety predicates, the frozen machine-safe predicate reduces to

\[
R47J_{SAFE}(F,y)
\iff
\bigl(J_y(F)\text{ terminal}\bigr)
\lor
\bigl(W(J_y(F))\le4\bigr).
\]

Hence a closed R47J_SAFE door is exactly

\[
J_y(F)\text{ nonterminal}\land W(J_y(F))>4.
\]

## L5 — all-doors-closed certificate

Combining L1–L4, an alternate-door counterexample at an immediate-BVE source must satisfy, simultaneously for every `y != x`,

\[
\boxed{
\chi^*(F,y)\ge5
\quad\land\quad
J_y(F)\text{ nonterminal}
\quad\land\quad
W(J_y(F))>4.
}
\]

This is much stronger than merely having one same-pivot wide survivor. It is a proof-carrying finite obstruction ledger: each alternate variable must carry both a width-5-or-more R49H blocking witness and an independently replayable R47J wide survivor.

## Support-frontier sufficient subtarget

Let `C` be a surviving wide clause in `J_x(F)`. Because the final state is R33-fixed, every literal of `C` has a distinct nonblocking opposite-polarity support witness. R50G9 further records external escape literals in those witnesses. Define the support frontier

\[
\Phi(C)=Vars(C)\cup\{\text{variables of external escape literals in the support certificate}\}.
\]

The following statement is sufficient for the target:

\[
\boxed{
\exists y\in\Phi(C),\ y\ne x:\ R49H(F,y)\lor R47J_{SAFE}(F,y).
}
\]

R50G10 does **not** assume or claim this statement. The executable lane measures it exactly on the sealed R50G9 witness and on any frozen reachable same-pivot-wide states. If it fails, it must emit the full closed-door ledger for the frontier variable(s), not a heuristic score.

## Exact remaining obstruction

A genuine local counterexample to the alternate-door implication is therefore an immediate-BVE source with a same-pivot wide certified fixpoint and the universal finite ledger

\[
\forall y\ne x:\quad
\chi^*(F,y)\ge5
\land
J_y(F)\text{ nonterminal wide}.
\]

A reachable refutation additionally requires a proof that this exact source belongs to the reachable refined `U_mu` domain. Without that certificate, only the strong local theorem may be refuted.

## Firewall

No finite replay proves the universal reachable theorem. No random search order, score, learned selector, probability, or new semantic inference rule is authorized. `U_mu` remains OPEN; `SAT_IN_P` and `P_EQ_NP` remain NOT_PROVED unless a separate complete proof closes all obligations.
