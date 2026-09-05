# JANUS TRUMP R50G12 — RUP external-support theorem

## Frozen setting

Let `H` be a canonical tautology-free formula at the frozen R47J normalization fixpoint. Therefore `H` is R33-fixed (in particular BCE-fixed) and RUP-fixed. Let `C in H`, let `l in C`, and call a clause `D in H` a nonblocking support for `(C,l)` when `-l in D` and the resolvent

`R = (C \\ {l}) union (D \\ {-l})`

is non-tautological.

BCE-fixedness says that for every literal `l` of every surviving clause `C`, at least one such nonblocking support `D` exists; otherwise `C` would be blocked on `l`.

## Lemma 1 — internal support forces RUP strengthening

Assume a nonblocking support `D` satisfies

`D \\ {-l} subseteq C \\ {l}`.

Consider the frozen single-literal RUP candidate that removes `l` from `C`. It assumes the negation of every literal in `C \\ {l}`.

Under these assumptions:

* every literal in `C \\ {l}` is false, so `C` becomes the unit clause `l`;
* every literal in `D \\ {-l}` is also false, so `D` becomes the unit clause `-l`.

Unit propagation therefore derives a conflict. Hence `C \\ {l}` is a valid frozen RUP strengthening.

So in a RUP-fixed formula no nonblocking support can satisfy the internal-support condition above.

## Lemma 2 — every nonblocking support uses an external variable

Take any nonblocking support `D` for `(C,l)` in a tautology-free RUP-fixed formula. By Lemma 1, `D \\ {-l}` is not a subset of `C \\ {l}`. Thus some literal `e in D \\ {-l}` is not a literal of `C \\ {l}`.

Because the resolvent is non-tautological, `e` cannot be the opposite sign of a literal already in `C \\ {l}`. Because the formula is tautology-free, `D` cannot contain both `l` and `-l`. Therefore `abs(e)` is not in `Vars(C)`.

Hence every nonblocking support carries at least one variable outside `Vars(C)`.

## Corollary 3 — external-variable bound for a surviving clause

BCE-fixedness supplies at least one nonblocking support for each `l in C`; Lemma 2 says each such support contains an external variable. In particular at least one external variable exists globally, so

`|Vars(H)| >= |C| + 1`.

For a widest clause of width `w`,

`|Vars(H)| >= w + 1`.

This is a source-level theorem from the frozen BCE and RUP definitions; it is not a finite-search inference.

## Corollary 4 — six-variable immediate-BVE escape is eliminated

Let `F` be a persisted W<=4 immediate-BVE source on pivot `x`, with `|Vars(F)| <= 6`. R50G5 already proves for same-pivot R47J that `x` is removed and no fresh variable is introduced. Thus the normalized final formula `J_x(F)` has at most five variables.

Assume for contradiction that `J_x(F)` is nonterminal and has width greater than four. Then it contains a clause `C` of width at least five. Corollary 3 requires

`|Vars(J_x(F))| >= |C| + 1 >= 6`,

contradicting the at-most-five-variable bound.

Therefore

`IMMEDIATE_BVE(F,x) AND |Vars(F)|<=6`

implies

`TERMINAL(J_x(F)) OR W(J_x(F))<=4`.

So the same pivot itself is machine-safe for every such source. This closes the immediate-BVE case at V<=6 without needing an alternate door.

## Corollary 5 — exact seven-variable boundary normal form

Let `|Vars(F)|=7` and suppose, only for structural reduction, that same-pivot R47J ends nonterminal and wide. R50G5 gives `|Vars(J_x(F))|<=6`. Corollary 3 gives `|Vars(J_x(F))|>=w+1` for final width `w>=5`. Hence necessarily

`|Vars(J_x(F))|=6` and `w=5`.

For any widest width-5 clause `C`, exactly one final variable lies outside `Vars(C)`. Call it `z`. Lemma 2 then forces every nonblocking support of every literal of `C` to use that same external variable `z` (possibly with either polarity).

Thus every seven-variable same-pivot wide survivor has the frozen normal form

`WIDTH5_CLAUSE + SINGLE_EXTERNAL_SUPPORT_HUB(z)`.

This does **not** eliminate V=7; it names the next exact obstruction.

## Firewalls

This proof does not establish the universal reachable alternate-door theorem, full immediate-BVE elimination, U_mu, SAT in P, or P=NP. The valid status promotion from this note alone is only `V6_IMMEDIATE_BVE_CASE_ELIMINATED=true` under the frozen definitions above.
