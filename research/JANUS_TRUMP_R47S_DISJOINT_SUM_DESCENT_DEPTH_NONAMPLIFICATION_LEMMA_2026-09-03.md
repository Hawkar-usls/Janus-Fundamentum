# JANUS TRUMP R47S — Disjoint-Sum Descent-Depth Non-Amplification Lemma

Date: 2026-09-03

Status: **SYMBOLIC CONSTRUCTION FIREWALL; TERMINAL-LIFT CAVEAT EXPLICIT**

## Purpose

R47O introduces the certified macro-depth function `d(F)`. A tempting way to manufacture larger depth is to take many independent copies of a hard residual and conjoin them on disjoint variable sets. For strict-descent macros, that construction cannot increase the required depth.

## Domain

Let `F` and `G` be canonical CNFs with disjoint variable sets. Assume both are genuine residual fixpoints of the pre-macro stack: R33 unchanged, non-affine as a whole component, RUP-stalled, and no subsumption-aware BVE successor.

Define `d_down(F)` as the least number of exact-DP layers in a certified macro which acts only on variables of `F`, never relies on a component-only semantic terminal, and ends in a canonical nonterminal `F'` satisfying

`CLV(F') < CLV(F)`.

This is deliberately a descent-only depth. SAT-terminal lifting across a conjunction needs separate treatment.

## Locality facts

Because the variable sets are disjoint:

1. exact DP on a variable of `F` removes and creates clauses only in the `F` component;
2. tautology, unit, pure-literal, subsumption, blocked-clause and BVE tests cannot acquire cross-component witnesses, because no literal variable occurs in both components and a genuine residual contains no empty terminal clause;
3. RUP propagation and RUP clause strengthening on literals of `F` cannot use clauses from `G` to create an implication, because there is no shared variable path;
4. if `G` starts R33/RUP/BVE-stalled and its clauses are unchanged, transformations confined to `F` do not create a new local reduction inside `G`.

Therefore a certified nonterminal descent trajectory confined to `F` lifts to `F ∪ G` with the `G` clauses unchanged.

## CLV lifting

Let a depth-`k` component macro transform `F` to `F'` with

`CLV(F') < CLV(F)`.

For disjoint conjunction, the clause and literal coordinates add:

`C(F∪G)=C(F)+C(G)`

`L(F∪G)=L(F)+L(G)`.

The variable coordinate also adds because the variable sets are disjoint.

Adding the same `CLV(G)` contribution to both sides preserves the first strict lexicographic difference. Hence

`CLV(F'∪G) < CLV(F∪G)`.

The same depth-`k` proof-carrying sequence is therefore a valid global strict-descent macro.

Thus

`d_down(F∪G) <= d_down(F)`

and symmetrically

`d_down(F∪G) <= d_down(G)`.

So

`d_down(F∪G) <= min(d_down(F), d_down(G))`.

## Consequence

Variable-disjoint repetition cannot amplify strict-descent macro depth. In particular, taking many independent copies of a depth-2 hard core cannot produce a family whose required descent depth grows with the number of copies: the algorithm may simply execute the depth-2 descent inside one copy and obtain global CLV descent.

Any attempt to construct an unbounded `d(F_n)` family for R47O must therefore introduce **coupling** between stages/components so that no shallow local descent survives independently.

A valid serial-depth gadget must make the early transformation of one region change the certified opportunities of the next region through shared variables/clauses or another explicitly proof-carrying interface.

## Terminal caveat

This lemma is stated for nonterminal strict descent. If a component macro reaches UNSAT, that UNSAT terminal immediately lifts to the whole conjunction. A SAT terminal for one component alone does not by itself decide a conjunction with an unresolved other component, so SAT-terminal depth does not obey the same simple minimum law without an explicit decomposition/elimination certificate.

This caveat is why the theorem is named **descent-depth non-amplification**, not unrestricted semantic-terminal depth.

## Epistemic firewall

- Disjoint sums do not prove or refute existence of a universal constant `K`.
- Coupled serial gadgets may behave differently and remain an open construction route.
- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
