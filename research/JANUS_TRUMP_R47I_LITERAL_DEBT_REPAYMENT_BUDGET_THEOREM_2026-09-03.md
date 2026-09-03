# JANUS TRUMP R47I — Literal-Debt Repayment Budget Theorem

Date: 2026-09-03

Status: **SYMBOLIC SUFFICIENT CONDITION; NOT O4 EXISTENCE PROOF**

## Scope

Let `F` be a genuine reachable residual fixpoint of the frozen pre-macro stack, and let `v` be a bipolar pivot with frozen exact-DP result `D_v`.

Assume `v` is in the R47H **LITERAL_DEBT** class:

- `C(D_v) = C(F)`;
- `L(D_v) = L(F) + d`, with integer `d >= 1`;
- exact DP removes `v` and introduces no fresh variable, so `V(D_v) <= V(F)-1`.

Let frozen R45A normalize `D_v` by R33, then affine/declared terminal checks, then R35B RUP where applicable.

Write `H_v` for the canonical nonterminal formula immediately after R33 and `G_v` for the final canonical nonterminal formula after RUP.

## Lemma 1 — R33 cannot make literal debt worse while clause count stays tied

Every accepted internal R33 rewrite strictly decreases the frozen lexicographic `CLV=(C,L,V)` measure. Its frozen rules do not introduce fresh variables.

Therefore:

- if `C(H_v) < C(F)`, the macro has already crossed below `F` in the first CLV coordinate;
- otherwise `C(H_v) = C(F) = C(D_v)`, and necessarily `L(H_v) <= L(D_v)`.

Define the R33 literal repayment on the tied-clause lane:

`q_v := L(D_v) - L(H_v) >= 0`.

## Lemma 2 — every successful frozen RUP strengthening repays at least one literal unless it produces an even stronger clause drop

R35B replaces one source clause by a strict one-literal subclause at each successful strengthening and canonicalizes the formula.

For each successful strengthening, either:

1. clause count drops because canonicalization merges/removes a duplicate, which already yields a stronger CLV descent lane; or
2. clause count stays unchanged and literal mass drops by at least one.

Let `s_v` be the number of successful RUP strengthenings after R33.

If no earlier terminal is reached and the final clause count remains tied with `F`, then

`L(G_v) <= L(H_v) - s_v`.

Hence

`L(G_v) <= L(F) + d - q_v - s_v`.

## Theorem — literal-debt budget closure

For a nonterminal LITERAL_DEBT pivot, any one of the following is sufficient for frozen R45A acceptance:

1. R33 or RUP lowers clause count below `C(F)`;
2. an independently verified semantic terminal is reached;
3. clause count remains tied and

   `q_v + s_v >= d`.

In case 3,

`L(G_v) <= L(F)`.

Because exact DP removed `v`, and the frozen normalizers introduce no fresh variable,

`V(G_v) <= V(F)-1`.

Therefore:

- if `L(G_v) < L(F)`, strict descent occurs in literal mass;
- if `L(G_v) = L(F)`, strict descent occurs in variable count.

Thus

`q_v + s_v >= d  =>  CLV(G_v) < CLV(F)`

on the nonterminal tied-clause LITERAL_DEBT lane.

## Why this matters

R47H restated O4 as universal existence of a terminal escape or sufficient debt repayment. R47I gives a cheaper, certificate-visible sufficient condition for one major residual class:

`LITERAL_DEBT(v) AND (q_v+s_v >= d_v) => CERTIFIED_DESCENT(v)`.

The quantities are directly available from the proof-carrying normalization trace:

- `d_v` from exact DP;
- `q_v` from the R33 before/after literal masses;
- `s_v` from the number of independently replayable RUP strengthening records.

No SAT truth label, oracle, assignment enumeration, or global argmin is required to evaluate this sufficient condition.

## Remaining wall

This theorem does **not** prove that every genuine reachable fixpoint contains such a pivot. It only turns one existence question into a concrete local inequality.

The next O4 attack is therefore:

> For every genuine reachable residual fixpoint, does there exist a bipolar pivot that is terminal, clause-debt overpaid, or LITERAL_DEBT with certificate-visible budget `q+s >= d`?

A reachable core where every pivot fails all such lanes remains a valid counterexample target.

## Epistemic firewall

- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
