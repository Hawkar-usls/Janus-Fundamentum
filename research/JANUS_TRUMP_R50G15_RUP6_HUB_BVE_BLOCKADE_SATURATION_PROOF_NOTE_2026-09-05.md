# JANUS TRUMP R50G15 — RUP6 hub BVE-blockade saturation

## Scope

Let `H` be the six-variable state immediately before a certified RUP strengthening in an R47J normalization round. The preceding frozen R33 pass is stalled, hence `H` is tautology/unit/pure/subsumption/BCE/BVE fixed under the frozen R33 source definition.

Assume `H` contains a width-six clause

\[
R=C\lor \sigma z,
\]

where `C` has width five and contains every variable except the hub `z`, and certified single-literal RUP replaces `R` by `C`.

The result below is local to this exact RUP6_DROP_HUB situation. It does not eliminate the V7 case by itself.

## L1 — an opposite-hub unit witness must exist

RUP tests `C` by assuming the complements of all five literals of `C`. Under those assumptions all variables except `z` are assigned. `R` becomes unit and forces `sigma z`.

A direct conflict from a clause using only literals of `C` would mean that a clause `D subseteq C` is already present. But `D` would strictly subsume `R`, contradicting that the preceding R33 pass is subsumption-fixed.

Therefore the UP conflict must force the opposite hub polarity. Hence there exists a clause

\[
D=(-\sigma z)\lor S,
\qquad S\subseteq C,
\]

with all literals of `S` having the same signs as in `C`. Under the RUP assumptions `D` becomes unit `-sigma z`.

## L2 — the width-six row collapses to one non-tautological resolvent

Take any clause `N` containing `-sigma z`. Since the six variables are exactly `Vars(C) union {z}`, every other literal of `N` is on a variable of `C`.

Resolving `R` and `N` on `z` has only two possibilities:

1. `N` contains the complement of a literal of `C`; then the resolvent is tautological.
2. Every residual literal of `N` has the same sign as its occurrence in `C`; then the residual of `N` is a subset of `C`, so the resolvent is exactly `C`.

Thus the entire cross-polarity row contributed by `R` contains at most one distinct non-tautological resolvent: `C`.

## L3 — BVE-fixedness forces resolvent saturation

Let

- `p` = number of clauses containing `sigma z`, including `R`;
- `n` = number of clauses containing `-sigma z`;
- `m=p+n` = total clauses removed by exact BVE on `z`;
- `r` = number of distinct non-tautological cross-polarity resolvents.

The frozen R33 BVE rule accepts whenever

\[
r\le m
\]

and the transformed `(C,L,V)` measure strictly decreases.

If `r<m`, clause count strictly decreases after eliminating `z`, so the measure necessarily decreases. Therefore a BVE-fixed state must satisfy

\[
\boxed{r\ge m=p+n.}
\]

The equality case can still be BVE-admissible if literal count decreases; therefore `r>=m` is necessary, not sufficient, for blockade.

## L4 — the collapsed row forces at least 3 x 2 hub incidence

All non-tautological pairs involving `R` contribute at most one distinct resolvent by L2. The remaining `p-1` same-polarity clauses can pair with at most `n` opposite-polarity clauses. Therefore

\[
r\le 1+(p-1)n.
\]

Combining with L3 gives

\[
1+(p-1)n\ge p+n.
\]

Equivalently,

\[
(p-2)(n-1)\ge1.
\]

Hence

\[
\boxed{p\ge3,\qquad n\ge2.}
\]

So every RUP6_DROP_HUB edge that survives the preceding R33 BVE pass carries at least five hub-containing clauses in that post-DP state: the width-six clause plus at least two further clauses of its hub polarity and at least two clauses of the opposite polarity.

## Minimal boundary

For `p=3,n=2`, the pair bound is exactly five:

\[
1+(3-1)2=5=p+n.
\]

Thus a minimal blockade must realize all five required distinct non-tautological resolvents. If any pair is tautological or duplicates an existing resolvent beyond the single unavoidable collapse in the `R` row, then `r<5` and BVE becomes admissible.

Even at `r=5`, blockade is not automatic: the transformed literal measure must fail to decrease. The executable control contains both an under-saturated `2 x 2` state where BVE is forced and a local `3 x 2` equal-count state where literal growth blocks the frozen BVE rule.

## Consequence for R50G14

A `RUP_BEARING_CYCLE` is no longer merely a cycle containing a RUP6 edge. Every such edge must carry a proof-carrying saturation debt:

\[
\boxed{
RUP6\_DROP\_HUB
\Rightarrow
RUP\_WITNESS
+ p\ge3
+ n\ge2
+ r\ge p+n
+ BVE\_BLOCKADE\_MEASURE\_LEDGER.
}
\]

The next obligation is to pull this five-clause-or-stronger hub incidence pattern back through the exact V7 DP ancestry and test whether pre-BVE cleanliness / alternate-door geometry can realize it at all.

## Firewall

This note does **not** prove V7 impossible, does not eliminate RUP-bearing hub cycles, does not prove `U_mu`, does not prove `SAT in P`, and does not resolve `P vs NP`.
