# R50G20 — RUP6 phase collapse to a six-variable width-5 core

## 0. Corrected phase boundary

R50G15/R50G17 derive the oriented BVE-saturation inequality

\[
1+(p-1)n\ge p+n
\iff
(p-2)(n-1)\ge1,
\]

hence `p>=3,n>=2`, from **BVE fixedness**. That certificate belongs to

\[
H_0=\text{the R33-fixed state at entry to a complete RUP pass}.
\]

It does **not** automatically belong to an internal state `H_t` after earlier RUP strengthenings, because frozen `run_candidate` performs several one-literal RUP strengthenings before R33 is called again.

R50G18 is the exact counter-control. Before its seventh RUP strengthening

\[
(2,3,4,5,6,7)\to(3,4,5,6,7),
\]

the literal-2 profile has `p=2,n=1,r=1`, and BVE is already accepted. Thus `H_0 fixed => every H_t fixed` is false. R50G20 never uses that implication.

## 1. Full-clause BCE witness lemma at H0

Let `H0` be canonical, tautology-free and R33-fixed with exactly six variables. Let

\[
R=(\ell_1\vee\cdots\vee\ell_6)
\]

be a width-6 clause. Since there are exactly six variables, `R` contains every variable exactly once.

Because `H0` is BCE-fixed, `R` is not blocked on any literal `ell in R`. Therefore for each `ell` there is a clause

\[
D_\ell=(-\ell)\vee S_\ell
\]

such that the resolvent of `R` and `D_ell` on `ell` is non-tautological.

All variables of `D_ell` are among the six variables of `R`. Non-tautology of the resolvent forbids a literal in `S_ell` from having polarity opposite to its occurrence in `R`. Tautology-freeness forbids `D_ell` from containing both `ell` and `-ell`. Hence

\[
S_\ell\subseteq R\setminus\{\ell\}
\]

as a literal set with the same polarities as `R`. R33 unit-fixedness makes `S_ell` nonempty, although nonemptiness is not needed for the conflict argument if an opposite unit were present.

Now test the one-literal strengthening

\[
R\to R\setminus\{\ell\}.
\]

RUP assumes the negations of every literal in `R\setminus{ell}`. Under those assumptions, `R` becomes unit `ell`; `D_ell` becomes unit `-ell` (or conflicts even earlier). Therefore

\[
\boxed{R\setminus\{\ell\}\text{ is RUP-valid at }H_0}
\]

for **every** literal `ell in R`.

This lemma needs BCE fixedness, not the stronger exact `3x2` saturation count.

## 2. Strengthening-monotonicity of the UP conflict

Suppose unit propagation on `F` under assumptions `A` derives a conflict. Let `F'` be obtained only by replacing clauses by subclauses.

Take the original UP derivation in order. Whenever a clause `C` was used to force literal `q`, all literals of `C\{q}` were false. Its descendant `C' subseteq C` either:

1. still contains `q`, in which case `C'` is unit no later than `C`; or
2. no longer contains `q`, in which case every literal of `C'` is already false and `F'` conflicts earlier.

Thus every original propagation is reproduced no later, unless an earlier conflict occurs. Consequently

\[
\boxed{
UP(F\land A)=CONFLICT
\implies
UP(F'\land A)=CONFLICT
}
\]

for clause-wise strengthening `F'`.

Frozen RUP performs exactly such transformations: a selected source clause is replaced by a strict one-literal subclause, followed by canonicalization. It never widens a clause and never introduces a fresh literal.

Therefore, as long as a particular width-6 clause `R` itself is unchanged, every deletion `R\{ell}` that was RUP-valid at `H0` remains RUP-valid after any number of earlier RUP strengthenings of other clauses.

## 3. R cannot disappear before it is touched

While `R` is unchanged, another RUP strengthening cannot create a duplicate copy of `R` and make canonicalization remove the old copy.

To strengthen another clause into `R`, that source would have to be a strict superclause of `R`. But `R` already contains one literal from all six variables. In a tautology-free formula over exactly those six variables, no strict non-tautological superclause of `R` exists.

Hence an unchanged width-6 `R` remains present until it is itself selected.

## 4. Eventual-touch theorem for the complete frozen RUP pass

Frozen `first_rup_strengthening` deterministically scans the current canonical formula and all removable literals. `run_candidate` repeats this scan after every successful strengthening and stops only when no proposal exists (or UP has already proved UNSAT).

Every successful strengthening strictly decreases the literal-count component of the frozen progress measure, so only finitely many successful steps are possible.

Assume for contradiction that a nonterminal complete RUP pass ends while an original width-6 clause `R` remains unchanged. By Sections 1–3, at least one (indeed all six) one-literal deletions of `R` is still RUP-valid. Therefore `first_rup_strengthening` has a proposal, contradicting termination at `STALLED_RUP_CORE`.

Thus every width-6 clause present at `H0` is strengthened during the pass (unless the pass has already terminated UNSAT).

Since a six-variable tautology-free formula has no clause wider than six, and RUP never widens clauses,

\[
\boxed{
RUP(H_0)=UNSAT
\quad\lor\quad
W(H_{rup\_fix})\le5.
}
\]

This is the R50G20 width-collapse theorem.

## 5. Frozen selector lemma

Within a selected source clause, frozen R35B checks removable literals using `lit_key(lit)=(abs(lit), sign-order)`.

For an all-variable tautology-free width-6 clause there is exactly one sign for each variable, so the first removable literal in that clause is the literal whose variable has minimum absolute identifier:

\[
\boxed{
\ell_{first}(R)=\operatorname*{argmin}_{\ell\in R}|\ell|.
}
\]

By Section 1 every literal deletion is already RUP-valid at `H0`, and by Section 2 this remains true until `R` is touched. Hence when the unchanged `R` is first selected, the frozen implementation removes the minimum-variable literal.

This is an algorithm-order theorem, not an isomorphism-invariant mathematical property. Renaming variable identifiers changes the scanner order; the theorem follows the renamed minimum.

## 6. V7 unsafe-trace corollary

In the R50G12 boundary theorem, any nonterminal R47J fixed point with a surviving wide clause satisfies

\[
V_{final}\ge W_{final}+1.
\]

A same-pivot V7 trace has at most six variables after eliminating the distinguished pivot, and exact normalization introduces no fresh variables.

Suppose such a trace reaches an R33-fixed RUP-entry `H0` with six variables and width six. R50G20 gives, after the complete RUP pass,

\[
UNSAT\quad\text{or}\quad W\le5.
\]

If a later R33 BVE eliminates another variable, at most five variables remain forever. Then a nonterminal final width `>4` would require at least six variables by the R50G12 external-support bound, contradiction. Hence any branch that performs another variable elimination is safe/terminal.

If no later variable elimination occurs, non-BVE R33 rules, affine normalization and subsequent RUP steps do not increase width. Therefore any still-unsafe descendant is confined to

\[
\boxed{V=6,\qquad W=5.}
\]

So width six cannot be the terminal obstruction of the V7 RUP-bearing branch.

Important provenance firewall: a width-5 clause reached by shrinking a width-6 clause is **not automatically a historical `DIRECT5` clause generated directly by the distinguished DP**. The theorem proves

\[
\boxed{
RUP6\text{-entry}\to SAFE/TERMINAL
\quad\lor\quad
V6/W5\text{ core}
}
\]

and does not yet identify the ancestry class of that V6/W5 core.

## 7. Status allowed after validation

If the frozen implementation audit agrees with the source proof, R50G20 may set:

- `RUP6_PHASE_ENTRY_WIDTH_COLLAPSE = PROVED`;
- `RUP6_AS_TERMINAL_WIDTH6_V7_OBSTRUCTION = ELIMINATED`;
- `V7_UNSAFE_DESCENDANT_AFTER_RUP6 = V6_W5_OR_SAFE`.

It may **not** set:

- `RUP_BEARING_V7_HUB_CYCLE_ELIMINATED = true`;
- `V7_IMMEDIATE_BVE_CASE_ELIMINATED = true`;
- `U_MU = PROVED`;
- `SAT_IN_P = PROVED`;
- `P_EQ_NP = PROVED`.

The next obligation is the six-variable width-5 core itself, with ancestry kept explicit (`DIRECT5` versus `RUP6_DESCENDED_W5`).
