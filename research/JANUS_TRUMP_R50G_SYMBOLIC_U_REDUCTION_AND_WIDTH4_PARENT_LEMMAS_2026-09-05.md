# JANUS TRUMP R50G — symbolic reduction of U and strengthened W4 bad-parent lemmas

## Target

For the frozen R50A/R47J machine on persisted canonical formulas of maximum width at most four, the remaining universal obligation is

\[
U:\quad \forall F\in\mathcal R_{W4},\quad R33(F)\;\lor\;\exists v\,R49H(F,v)\;\lor\;\exists v\,R47J_{SAFE}(F,v).
\]

This note proves several exact reductions around a hypothetical counterexample. It does **not** prove U.

## Lemma 1 — a width>4 non-tautological DP resolvent needs a width-4 parent

Let the pivot be `v`. Remove the pivot literal from a positive parent and a negative parent, obtaining residual literal sets `A` and `B`. Because the persisted formula has maximum width four,

\[
|A|\le3,\qquad |B|\le3.
\]

If both original parents have width at most three then `|A|<=2` and `|B|<=2`, hence

\[
|A\cup B|\le4.
\]

Therefore every retained non-tautological resolvent of width greater than four has at least one width-4 parent. More precisely,

\[
BAD(v)\subseteq (P_4(v)\times N_{\ge3}(v))\cup(P_{\ge3}(v)\times N_4(v)).
\]

This strictly strengthens the earlier coarse long×long containment.

## Lemma 2 — width six requires width4 × width4

A width-six resolvent needs six distinct residual literals. Since each residual has size at most three, both must have size exactly three. Thus both original parents have width four and the residuals are disjoint and non-tautological:

\[
WIDTH6(v)\subseteq P_4(v)\times N_4(v).
\]

## Lemma 3 — no-R49H forces width-4 incidence at every variable

Suppose a bipolar pivot `v` occurs in no width-4 parent. Then every parent containing `v` has width at most three, so every retained cross-polarity residual union has width at most four by Lemma 1. Therefore

\[
\chi_F^*(v)\le4,
\]

and R49H authorizes exact DP on `v`.

Consequently, in any R33-fixed state with no R49H pivot, **every current variable occurs in at least one width-4 parent participating in some retained bad cross pair**, and the opposite-polarity parent in such a pair has width at least three.

A weak but exact incidence consequence is

\[
4C_4\ge V.
\]

No contradiction is claimed from this bound alone.

## Lemma 4 — no W4 machine deadcore with at most five variables

For any pivot `v`, a non-tautological resolvent contains at most one literal for each variable other than `v`. Therefore its width is at most `V-1`. If `V<=5`, every retained resolvent has width at most four:

\[
\chi_F^*(v)\le V-1\le4.
\]

If `v` is bipolar, R49H applies. If `v` is pure, R33's pure-literal lane applies. Hence an R33-fixed, no-R49H deadcore cannot exist with five or fewer variables:

\[
\boxed{V_{deadcore}\ge6}.
\]

This is a universal local theorem for the frozen W4 machine, not a finite observation.

## Lemma 5 — for an integrity-valid R47J candidate, final nonterminal W4 is enough for the R50A successor condition

Exact DP eliminates the selected pivot and introduces no fresh variable. R33 reductions, affine recognition/solve, and RUP strengthening do not introduce fresh variables; BVE only eliminates existing variables and forms resolvents over the existing variable set. Thus the eliminated pivot cannot reappear and the final variable set is a strict subset of the input variable set whenever the candidate is nonterminal.

Therefore, modulo the already independently replayed local certificates, a nonterminal R47J candidate is rejected by the current R50A successor rule only when its final normalized formula still has width greater than four. In symbolic work we may therefore reduce the hard case to a surviving-wide-clause obstruction.

## Minimal-counterexample normal form

Assume U is false and choose a counterexample `F*` minimal under `(V,C,L,hash)` among the frozen reachable set. Then all of the following hold simultaneously:

1. `F*` is a literal R33 fixed point and is not an R33 terminal.
2. Every variable is bipolar.
3. Every variable has `chi_star>=5`; otherwise R49H supplies a legal successor.
4. Every variable occurs in at least one width-4 parent participating in a retained bad cross pair.
5. `V(F*)>=6`.
6. For every pivot `v`, exact replayed R47J normalization ends nonterminal with at least one width-5 or width-6 survivor.
7. Every such raw wide resolvent has the parent shape of Lemma 1; every width-six survivor descends from width4×width4 parents.

Thus the remaining bridge is sharply localized:

> Prove that no reachable R33-fixed W4 formula can make **every** pivot retain at least one certified wide survivor after the frozen R47J normalization.

Equivalently, prove that at least one pivot's entire wide inventory admits certified clearance.

## Proof directions authorized after the freeze

The following are legitimate symbolic routes but have no authority until completed:

- double-count width-4 parent incidence and survivor reuse;
- transfer a survivor witness at one pivot into a strictly smaller obstruction at another pivot;
- exploit reachability/provenance constraints of R50A rather than all arbitrary W4 formulas;
- derive a contradiction at the first possible `V=6` counterexample, then induct on `V` if the induction invariant can be stated without semantic advice.

Finite R50B/R50C/R50F data may suggest which route to try but cannot discharge a quantifier.

## Firewall

`WIDTH4_PARENT_LEMMAS = PROVED_LOCAL_COMBINATORICS`.

`MINIMAL_COUNTEREXAMPLE_NORMAL_FORM = CONDITIONAL_ON_NOT_U`.

`U = OPEN`.

`SAT_IN_P = NOT_PROVED`.

`P_VS_NP = OPEN`.

`TRUMP_finished = false`.
