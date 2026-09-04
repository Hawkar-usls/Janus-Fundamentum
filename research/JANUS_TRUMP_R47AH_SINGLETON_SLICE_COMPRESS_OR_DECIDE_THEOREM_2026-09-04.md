# JANUS TRUMP R47AH — Singleton Slice: Compress or Decide

## Status

**Conditional reduction theorem + executable structural falsification.**
No polynomial SAT decider is claimed.

## Definitions

Let `Q_BW` be the R44BW explicit binary-equality congruence quotient. It only merges variables when the input contains the certified binary pair

`(not u OR v)` and `(u OR not v)`.

Let the **R44BW singleton slice** be the set of canonical CNF formulas for which every congruence class discovered by this rule is a singleton.

Let `E3` be canonical exact-3-CNF: every retained clause has exactly three distinct variables and is non-tautological.

## Lemma 1 — Exact-3-CNF lies in the singleton slice

An `E3` formula contains no binary clauses. Therefore it cannot contain an R44BW binary equality certificate. Hence every R44BW congruence class is a singleton.

Thus

`E3 subset SINGLETON_SLICE(Q_BW)`.

## Lemma 2 — R44BW is only renaming on exact-3-CNF

Because every congruence class is a singleton, the substitution phase of `Q_BW` changes no literal identity. The remaining quotient operation is deterministic dense variable renaming / canonicalization.

Therefore for every `F in E3`,

`Q_BW(F) = dense_rename(F)`.

In particular, clause count and literal count are unchanged by the quotient on this slice.

## Lemma 3 — SAT is preserved on the singleton slice

Dense variable renaming is a bijection on assignments, so

`SAT(F) iff SAT(Q_BW(F))`.

This is consistent with the stronger R47AG projection/lifting theorem, but R47AH does not need equality lifting on `E3`; no equality class is nontrivial there.

## Theorem — Arbitrary quotient decider implies an exact-3SAT decider

Assume there exists a total algorithm `D_Q` such that for every R44BW quotient image `Q_BW(F)`:

1. `D_Q(Q_BW(F)) = SAT(F)`, and
2. the running time of `D_Q` is polynomial in the quotient encoding length.

For any exact-3-CNF instance `F`, compute `Q_BW(F)` and return `D_Q(Q_BW(F))`.

`Q_BW` is polynomial-time computable. On exact-3-CNF, `Q_BW(F)` is only a dense renaming of `F`, so its encoding size is polynomially equivalent to the input encoding size. Therefore the composition is a polynomial-time exact-3SAT decider.

Hence:

`POLY_DECIDER_ON_ALL_R44BW_QUOTIENT_IMAGES => EXACT_3SAT_IN_P`.

This is a **conditional reduction theorem**, not the construction of such a decider.

## The actual R47AH fork

The remaining target is exactly:

`COMPRESS THE SINGLETON SLICE OR SOLVE IT DIRECTLY`.

### Compression lane

Find a polynomial-time computable nontrivial representation `C(F)` for singleton-slice inputs such that universally

`C(F1)=C(F2) => SAT(F1)=SAT(F2)`.

Then additionally provide a polynomial-time decider operating on `C(F)`.

A mixed fiber

`C(F_sat)=C(F_unsat)`

immediately quarantines the candidate representation for SAT decision authority.

### Direct-decider lane

Provide a total polynomial-time decision algorithm directly over arbitrary `Q_BW(F)`.

A polynomial verifier, bounded finite search, heuristic controller, or exponential fallback does not satisfy this obligation.

## Executable audit

The R47AH experiment exhaustively checks all 256 exact-3-CNF clause subsets on 3 variables and all exact-3-CNF formulas on 4 variables with at most 3 clauses (5,489 formulas), for 5,745 formulas total.

It verifies:

- every tested exact-3-CNF has only singleton R44BW classes;
- every quotient equals deterministic dense renaming;
- no clause/literal size reduction occurs beyond renaming;
- an outside-slice positive control with an explicit equality certificate does compress.

The finite audit is implementation falsification/calibration only. The universal result comes from the structural lemmas above.

## Firewalls

- `POLYNOMIAL_QUOTIENT_CONSTRUCTION != POLYNOMIAL_SAT_DECISION`
- `POLYNOMIAL_VERIFIER != POLYNOMIAL_DECIDER`
- `FINITE_AUDIT != UNIVERSAL_PROOF`
- `SAT_IN_P = NOT_PROVED`
- `P_EQ_NP = NOT_PROVED`
- `P_NE_NP = NOT_PROVED`
- `P_VS_NP = OPEN`
- `TRUMP_finished = false`
