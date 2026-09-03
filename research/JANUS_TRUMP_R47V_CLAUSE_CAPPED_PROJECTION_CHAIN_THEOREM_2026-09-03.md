# JANUS TRUMP R47V — Clause-Capped Projection Chain Theorem

Date: 2026-09-03

Status: **CONDITIONAL SYMBOLIC THEOREM; UNIVERSAL CAP-PRESERVING SUCCESSOR EXISTENCE REMAINS OPEN**

## Motivation

R47O2 sealed an explicit reachable residual state `F` with certified macro depth `d(F) > 2` under the frozen R47J/R47L depth grammar. This refutes the candidate universal constant `K=2`, but it does **not** imply that a larger constant depth exists, and it does not authorize blind depth escalation.

The fixed-depth barrier arises because composing raw exact-DP layers without representation reset can produce the coarse recurrence

`C_{t+1} = O(C_t^2)`,

which yields `C_t = C_0^{2^t}` in the worst case. Therefore a depth growing with the input is not polynomial **unless the representation is reset between projections**.

R47V attacks that exact debt.

## Definition — clause-capped projected successor

Let `F_0` be a canonical normalized residual state with

- `C_0 = C(F_0)` clauses,
- `V_0 = V(F_0)` variables.

A certified transition from a current normalized nonterminal state `F_t` is **clause-capped** relative to `F_0` if:

1. one existing variable `v` is eliminated by exact Davis-Putnam projection;
2. the exact-DP record passes independent replay;
3. the existing certified normalization stack is run to its frozen joint fixpoint or semantic terminal;
4. every internal certificate/replay passes;
5. no fresh variable is introduced;
6. either a verified semantic terminal is reached, or the normalized successor `F_{t+1}` satisfies

   `C(F_{t+1}) <= C_0`.

No requirement is imposed that `CLV(F_{t+1}) < CLV(F_t)` or that `CLV(F_{t+1}) < CLV(F_0)`.

## Lemma 1 — variable count is a strict chain rank

Exact DP removes the selected pivot `v`. The frozen normalizers R33, affine recognition/solve, RUP vivification, and subsumption-aware BVE introduce no fresh variables.

Therefore every nonterminal clause-capped successor satisfies

`V(F_{t+1}) < V(F_t)`.

Hence every such chain has fewer than or equal to `V_0` nonterminal projection steps.

This replaces the old requirement of strict CLV descent at every macro with the simpler rank

`V(F_t)`.

## Lemma 2 — the clause cap automatically bounds literal mass

Every normalized state is canonical and tautology-free. A canonical clause contains at most one literal for each remaining variable. Therefore

`L(F_t) <= C(F_t) * V(F_t) <= C_0 * V_0`.

So every nonterminal chain state has encoding size polynomially bounded by the root parameters.

## Lemma 3 — one exact-DP probe from a capped state has polynomial intermediate size

At a capped state `F_t`,

`C(F_t) <= C_0`.

For a pivot with `p` positive and `n` negative parent clauses, exact DP inspects at most

`p*n <= C_0^2`

parent pairs and creates at most that many distinct non-tautological raw resolvents. No resolvent contains more than `V_0-1` literals.

Thus the forced-DP representation has at most `O(C_0^2)` clauses and `O(C_0^2 V_0)` literal mass.

The existing R47B/R47M normalization and independent verification envelopes are polynomial in this forced representation size.

Crucially, after an accepted nonterminal step the representation is reset to at most `C_0` clauses before another DP layer is allowed. The recurrence `C -> C^2 -> C^4 -> ...` therefore does not compose across chain depth.

## Lemma 4 — polynomial discovery does not enumerate projection sequences

At each current state, scan the at most `V_0` current variables in canonical order. For each variable construct and independently verify one exact-DP-plus-normalization candidate. Accept the first candidate that is either terminal or clause-capped.

This scans variables, not depth-`k` sequences.

There are at most `V_0` chain states and at most `V_0` candidate probes per state. Therefore there are at most `V_0^2` candidate probes over the whole run.

Each probe has polynomial work by Lemma 3.

## Theorem — polynomiality conditional on universal clause-capped successor coverage

Assume the following still-open existence statement:

> For every reachable normalized nonterminal chain state `F_t` generated from every valid 3-CNF root `F_0`, there exists a polynomially discoverable certified pivot whose exact-DP-plus-frozen-normalization result is either a verified semantic terminal or a nonterminal state with `C <= C_0`.

Then deterministic first-certified clause-capped projection decides the root formula in polynomial time.

Proof sketch:

1. semantic correctness/equisatisfiability composes through exact DP and the existing certified normalizers;
2. every nonterminal accepted transition strictly decreases variable count;
3. at most `V_0` nonterminal transitions can occur;
4. every normalized nonterminal state has at most `C_0` clauses and `C_0 V_0` literals;
5. every candidate probe and its independent verifier have polynomial work;
6. at most `V_0^2` probes occur;
7. when no variables remain, canonical simplification is a direct constant terminal (`EMPTY_CNF_SAT` or `EMPTY_CLAUSE_UNSAT`).

Therefore total work is `N^{O(1)}` conditional on the universal cap-preserving successor existence statement.

## Why this is different from fixed macro depth

The old constant-depth route asked for

`exists constant K: every residual descends/terminates within <=K DP layers`.

R47O2 refuted `K=2` for the frozen depth grammar.

R47V instead permits up to `V_0` certified projections but demands a representation reset after **every** projection:

`C(F_t) <= C_0`.

Thus chain depth may grow linearly while representation size remains polynomial. This is not the forbidden `keep adding DP until success` recurrence because no uncapped DP output is allowed to become the input to the next projection.

## New theorem-critical wall

The universal obligation becomes

`CAP-PROJECTION COVERAGE`:

`FOR ALL reachable capped normalized nonterminal F_t, EXISTS pivot v such that Normalize(DP_v(F_t)) is terminal OR C <= C_0.`

This is a new formulation of O4, not a proof of O4.

A single reachable capped state for which every pivot normalizes to more than `C_0` clauses and no terminal is reached is an explicit counterexample to this proposed grammar and must be preserved.

## Firewalls

- `CAP_PROJECTION_COVERAGE = OPEN`.
- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
