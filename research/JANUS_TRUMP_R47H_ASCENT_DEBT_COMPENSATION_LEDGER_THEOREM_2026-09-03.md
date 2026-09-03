# JANUS TRUMP R47H — Ascent-Debt Compensation Ledger Theorem

Date: 2026-09-03

Status: **SYMBOLIC ACCOUNTING THEOREM; NOT UNIVERSAL COVERAGE**

## Scope

Let `F` be a canonical genuine residual fixpoint of the frozen pre-macro stack:

`R33 -> affine recognition -> R35B RUP -> subsumption-aware BVE`,

with all of the following true:

1. R33 returns `STALLED_STACK_LEAN_CORE` without changing `F`.
2. The complete affine recognizer does not accept `F`.
3. R35B returns `STALLED_RUP_CORE`, with no strengthening and exact independent replay.
4. `best_sa_bve_candidate(F)` returns `None` after the frozen variable scan.

For a bipolar variable `v`, let `D_v` be the exact DP elimination used by both R42 and R45A: remove the positive/negative parent clauses, emit every distinct non-tautological resolvent, canonicalize, then subsumption-minimize.

Write

`CLV(X) = (C(X), L(X), V(X))`

with lexicographic order.

## Lemma 1 — every immediate DP pivot carries positive residual debt

At a genuine subsumption-aware BVE fixpoint,

`CLV(D_v) !< CLV(F)`

for every bipolar `v`, because otherwise the frozen R42 BVE scan would have returned that pivot as an accepted strict successor.

Exact DP eliminates `v` and introduces no fresh variable, therefore

`V(D_v) <= V(F) - 1`.

Consequently equality in the first two CLV coordinates is impossible at a BVE fixpoint: if

`C(D_v)=C(F)` and `L(D_v)=L(F)`,

then the strict variable drop would imply `CLV(D_v) < CLV(F)`, contradiction.

Therefore every bipolar pivot at a genuine BVE fixpoint satisfies exactly one of the following residual-debt forms:

1. **CLAUSE_DEBT:** `C(D_v) > C(F)`; or
2. **LITERAL_DEBT:** `C(D_v) = C(F)` and `L(D_v) > L(F)`.

Thus the residual macro problem is not immediate descent. It is bounded exact ascent followed by certified debt repayment or a certified terminal escape.

## Lemma 2 — exact repayment condition for a nonterminal macro

Let `G_v = N(D_v)` be the final canonical formula after the frozen R45A normalization pipeline (`R33`, affine terminal check, then RUP where applicable), assuming normalization does not produce a semantic terminal.

Define the DP overage relative to the original state:

`dC_v = C(D_v) - C(F)`

`dL_v = L(D_v) - L(F)`

and the normalization repayment:

`rC_v = C(D_v) - C(G_v)`

`rL_v = L(D_v) - L(G_v)`.

The nonterminal macro is accepted exactly when `CLV(G_v) < CLV(F)`. Equivalently:

- `rC_v > dC_v`; or
- `rC_v = dC_v` and `rL_v > dL_v`; or
- `rC_v = dC_v`, `rL_v = dL_v`, and `V(G_v) < V(F)`.

The third line is legitimate because the eliminated pivot is not reintroduced and the frozen normalizers introduce no fresh variable.

This is an accounting identity, not an existence theorem.

## Lemma 3 — terminal escape is a distinct acceptance lane

R45A also accepts a pivot when normalization reaches an independently verified semantic terminal, even if `CLV(G_v)` is not below `CLV(F)`.

Therefore the exact residual coverage target is the disjunction

`CERTIFIED_TERMINAL_ESCAPE(v) OR CERTIFIED_DEBT_REPAYMENT_DESCENT(v)`.

A terminal certificate is not to be rewritten as fake CLV descent.

## O4 restatement

For every reachable genuine residual fixpoint `F`, prove that a polynomial scan can discover at least one bipolar pivot `v` satisfying

`CERTIFIED_TERMINAL_ESCAPE(v) OR CERTIFIED_DEBT_REPAYMENT_DESCENT(v)`.

R47B already bounds the work of constructing and verifying each frozen pivot macro polynomially. R47 Lemma 3 bounds the number of accepted nonterminal CLV-descending states polynomially. R47D composes these bounds conditionally on this existence statement.

Hence R47H changes the form of the remaining wall but does not close it:

`O4_UNIVERSAL_COVERAGE = OPEN`.

## Attack consequence

Future counterexample hunting should record, per pivot:

- input CLV;
- forced-DP CLV;
- debt class (`CLAUSE_DEBT` or `LITERAL_DEBT`);
- `dC_v`, `dL_v`;
- post-R33 CLV;
- post-RUP/final CLV;
- `rC_v`, `rL_v`;
- terminal kind, if any;
- accepted/rejected;
- independent replay status.

The useful adversary is now a reachable fixpoint for which **every** pivot simultaneously has:

- no certified terminal escape; and
- normalization repayment insufficient to cross back below the original CLV.

## Epistemic firewall

- This theorem does not prove that repayment always exists.
- Finite success on R47C/R47G/R47A9 does not imply universal repayment.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
