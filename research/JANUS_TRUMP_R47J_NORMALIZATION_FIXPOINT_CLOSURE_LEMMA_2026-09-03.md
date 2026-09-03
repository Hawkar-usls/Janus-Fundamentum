# JANUS TRUMP R47J — Certified Normalization Fixpoint Closure Lemma

Date: 2026-09-03

Status: **PROVED FOR THE FROZEN NORMALIZATION OPERATORS; NOT A UNIVERSAL COVERAGE THEOREM**

## Setting

Let `D` be the canonical exact-DP result for one pivot. The frozen normalization operators are:

1. `R33` certified simplification to its local fixpoint;
2. declared Horn/2-CNF/empty terminals with independent verification;
3. complete affine recognition plus GF(2) certificate verification;
4. `R35B` RUP strengthening with independent certificate replay.

The old R45A implementation executed this stack once and returned immediately after the first RUP pass, even when RUP changed the formula.

R47J replaces only that stopping policy. It adds no new inference rule and no new proof authority.

## Lemma 1 — changing RUP may expose a fresh R33 opportunity

A RUP strengthening changes the clause set while preserving the represented SAT status. The resulting formula need not remain an R33 fixpoint with respect to the new clause set.

The sealed R47I residual gives an explicit witness. For pivot 25:

`[63,155,20] -> DP [63,163,19] -> RUP [63,156,19]`.

The old R45A stopped here and rejected the macro. Re-running the already-certified R33 stack removes one additional clause:

`[63,156,19] -> R33 [62,153,19]`.

Hence the old linear pass was not closed under interactions among its own certified normalization operators.

## Lemma 2 — restart preserves proof authority

R47J restarts only the existing certified stack:

`R33 -> declared/affine terminal check -> RUP -> if changed, restart R33`.

Every RUP pass is independently replayed. Every declared or affine terminal is independently verified. Every R33 event retains its original certificate/reconstruction data. Exact-DP semantics and its independent replay are unchanged.

Therefore restart does not introduce a new semantic oracle, heuristic authority, truth label, or inference rule.

## Lemma 3 — every restart has strict current-state progress

A restart is permitted only when the RUP pass changed the current formula. Frozen R35B successful strengthening strictly decreases canonical CLV. Frozen R33 changes also strictly decrease canonical CLV.

Thus if states at restart boundaries are

`S_0, S_1, ..., S_t`,

then

`CLV(S_{i+1}) < CLV(S_i)`

for every restart.

The normalizers introduce no fresh variables.

## Lemma 4 — polynomial restart height

For the forced-DP starting formula with `C_f` clauses and `V_f` variables, every normalization state has at most `C_f` clauses and at most `V_f` variables after the first strict normalization change. Canonical literal mass is at most `C_f * V_f`.

A coarse lexicographic-state envelope is therefore

`H_f = (C_f+1)(C_f V_f+1)(V_f+1)`.

Every restart strictly decreases CLV, so the number of restarts is less than `H_f`.

R47B already bounds one frozen R33/affine/RUP construction and its independent verification polynomially in the current representation size. Therefore closing this normalization stack to fixpoint preserves polynomial per-macro work.

This statement is about resource safety of the closure. It does **not** prove that some pivot must be accepted on every reachable residual state.

## Lemma 5 — SAT model reconstruction remains compositional

If a normalization round reaches a SAT terminal, reconstruct through all recorded R33 histories in reverse chronological order, then reconstruct the eliminated DP pivot using the existing BVE/DP reconstruction rule. RUP strengthening requires no assignment reconstruction step because the accepted terminal assignment satisfies the strengthened formula and all RUP-added clauses are logical consequences of the preceding formula.

The reconstructed assignment must be replayed against the pre-DP formula before the macro certificate is accepted.

## Frozen R47J witness

The sealed R47I residual has old accepted-pivot set `[]`. Under fixpoint-closed normalization, accepted pivots are:

`[13, 25, 28, 29]`.

For pivot 25:

- input CLV: `[63,155,20]`
- forced DP: `[63,163,19]`
- first RUP: `[63,156,19]`
- restarted R33: `[62,153,19]`
- final normalization fixpoint: `[62,153,19]`
- independent macro replay: PASS.

Thus the R47I counterexample is a counterexample to the **old one-pass R45A stopping policy**, not to the stronger normalization-closure grammar.

## Algorithmic law

`NORMALIZATION_PASS != NORMALIZATION_FIXPOINT`.

For the corrected successor grammar:

`EXACT_DP -> CERTIFIED_NORMALIZATION_CLOSURE -> FIRST_CERTIFIED_ACCEPTED_MACRO`.

## Remaining wall

The new universal obligation is still:

For every reachable genuine residual fixpoint `F`, there exists a polynomially discoverable pivot whose fixpoint-closed normalization reaches a verified terminal or a strict CLV descent.

This remains **OPEN**.

## Epistemic firewall

- R47J repairs one explicit failure family witness; it does not prove universal coverage.
- Old frozen R45A O4 remains explicitly refuted by R47I.
- Extended fixpoint-closure grammar O4 is open.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
