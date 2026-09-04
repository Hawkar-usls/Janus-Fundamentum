# JANUS TRUMP R47Y — Cap-Slack Survivor-Pressure Lemma

Status: **SYMBOLIC NECESSARY/SUFFICIENT PRE-NORMALIZATION CAP TEST; UNIVERSAL PIVOT EXISTENCE OPEN**

## Scope

Fix a root formula `F0` with root clause cap

\[
C_0 := |F_0|.
\]

Let `F` be any reachable nonterminal state in a clause-capped projection chain, so

\[
C:=|F|\le C_0.
\]

Define the available clause slack

\[
\sigma(F):=C_0-C\ge 0.
\]

For a current pivot `v`, use the exact R47A5/R47U decomposition:

- `B_v(F)` = clauses not containing either polarity of `v`;
- `R_v(F)` = canonical unique non-tautological exact-DP resolvents;
- `T_v(F) = SUBSUMPTION_MINIMIZE(CANONICAL(B_v(F) union R_v(F)))`;
- `d_v = |F|-|B_v(F)|` = removed-parent pressure;
- `s_v = |T_v(F)|-|B_v(F)|` = post-subsumption survivor pressure above the unaffected base;
- `g_v = |F|-|T_v(F)| = d_v-s_v` = exact post-subsumption DP clause gain.

## Lemma 1 — exact slack identity

A forced exact-DP projection on `v` is within the root clause cap immediately after post-subsumption iff

\[
|T_v(F)|\le C_0.
\]

Using `g_v=C-|T_v(F)|` and `\sigma=C_0-C`, this is equivalent to

\[
C-g_v\le C+\sigma,
\]

hence

\[
\boxed{|T_v(F)|\le C_0\iff g_v\ge-\sigma(F)}.
\]

Equivalently, with `g_v=d_v-s_v`,

\[
\boxed{|T_v(F)|\le C_0\iff s_v-d_v\le\sigma(F)}.
\]

Thus root slack acts as an exact additive budget for temporary post-subsumption clause expansion.

## Lemma 2 — frozen R47M normalization cannot create clause overflow

The frozen R47M producer first performs exact DP and then runs the existing certified joint normalization stack.

Every nontrivial R47J normalization segment is required by code to satisfy strict lexicographic CLV descent relative to its segment input. Therefore its clause coordinate cannot increase.

Every inserted R42 SA-BVE restart is independently replayed and required to satisfy strict lexicographic CLV descent relative to the immediately preceding normalized state. Therefore its clause coordinate also cannot increase.

Consequently, for the frozen producer,

\[
\boxed{C(\operatorname{Normalize}_{R47M}(T_v(F)))\le |T_v(F)|}.
\]

This statement uses only the already-certified monotonicity checks of the frozen existing stack. It does not add a new inference rule.

## Corollary 3 — polynomial cap-safe pivot certificate

If a current pivot satisfies

\[
\boxed{g_v\ge-\sigma(F)},
\]

then its exact post-subsumption DP state already has at most `C0` clauses. Frozen R47M normalization cannot increase that clause count, and exact DP removes `v` while the frozen grammar introduces no fresh variables.

Therefore, provided the existing DP replay / polynomial-envelope / reducer replay checks pass, the pivot is a certified clause-capped successor (or terminal):

\[
\boxed{g_v\ge-\sigma(F)\Rightarrow\text{CAP-SAFE R47M SUCCESSOR}.}
\]

The quantity `g_v` is polynomially computable by the existing R47A3 post-subsumption producer, so this gives a cheap pre-normalization sufficient test before running the heavier full closure.

## Corollary 4 — exact necessary condition for a cap obstruction

A genuine nonterminal cap obstruction for the frozen grammar is a capped state `F` for which no current pivot yields a terminal or a nonterminal normalized successor under `C0`.

By Corollary 3, every pivot in such an obstruction must fail the slack test:

\[
 g_v<-\sigma(F).
\]

All quantities are integers, hence

\[
\boxed{g_v\le-\sigma(F)-1\quad\forall v.}
\]

Using `g_v=d_v-s_v`, equivalently

\[
\boxed{s_v-d_v\ge\sigma(F)+1\quad\forall v.}
\]

This is the **all-pivot surplus-over-slack condition**.

It strictly strengthens the old R47A5 direct-descent obstruction condition `g_v<=0` whenever `sigma>0`, and at zero slack sharpens it to strict expansion:

\[
\sigma=0\Rightarrow g_v\le-1\quad\forall v.
\]

So a root-cap obstruction cannot contain even a clause-neutral post-subsumption pivot at a zero-slack state.

## Algorithmic consequence

The cap-chain controller may safely insert a cheap first stage:

1. compute `sigma=C0-C`;
2. for pivots in deterministic order compute exact post-subsumption `g_v`;
3. if `g_v>=-sigma`, the pivot is already certified to remain under the root clause cap after frozen normalization;
4. run the existing full R47M replay/normalization only for the first such pivot to obtain the actual successor/certificate;
5. if every pivot has `g_v<-sigma`, record an **all-pivot surplus-over-slack candidate obstruction** and only then invoke heavier forensic/alternate certified machinery.

This does not prove that a slack-safe pivot always exists. It converts CAP-PROJECTION COVERAGE into the sharper universal existence question

\[
\boxed{\forall\text{ reachable capped nonterminal }F,\ \exists v:\ s_v-d_v\le\sigma(F).}
\]

## Why this matters for the fixed-depth wall

R47V showed on the sealed R47R witness that local CLV descent is unnecessarily strict: temporary literal debt can be tolerated while clauses remain under `C0` and variables strictly decrease.

R47Y identifies the exact clause-budget inequality controlling that mechanism. Long projection chains no longer require a universal constant macro depth if each state admits a pivot whose post-subsumption survivor excess fits inside the currently available root slack.

The remaining theorem-critical wall is therefore not raw depth. It is simultaneous all-pivot survivor excess:

\[
\boxed{\text{Can every pivot simultaneously satisfy }s_v-d_v\ge\sigma+1\text{ in a reachable capped normalized state?}}
\]

If no, CAP-PROJECTION COVERAGE follows for this frozen producer. If yes, the explicit configuration is the next obstruction that must be compressed or supplied with a stronger certified reducer.

## Epistemic firewall

- `CAP_SLACK_IDENTITY = PROVED`
- `R47M_NORMALIZATION_CLAUSE_NONINCREASE = PROVED_FROM_FROZEN_CLV_MONOTONICITY_CHECKS`
- `CAP_SAFE_PIVOT_IF_G_GE_MINUS_SLACK = PROVED_CONDITIONAL_ON_EXISTING_CERTIFICATE_CHECKS`
- `ALL_PIVOT_SURPLUS_OVER_SLACK_NECESSARY_FOR_CAP_OBSTRUCTION = PROVED`
- `UNIVERSAL_SLACK_SAFE_PIVOT_EXISTENCE = NOT_PROVED`
- `CAP_PROJECTION_COVERAGE = OPEN`
- `O4_UNIVERSAL_COVERAGE = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `P_EQ_NP = NOT_PROVED`
- `P_NE_NP = NOT_PROVED`
- `P_VS_NP = OPEN`
- `TRUMP_finished = false`
