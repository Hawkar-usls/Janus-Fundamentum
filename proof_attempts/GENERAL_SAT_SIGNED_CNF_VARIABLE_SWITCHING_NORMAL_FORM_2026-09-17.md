# General SAT — signed-CNF variable-switching normal form

Date: 2026-09-17

Status: `EXACT_NORMAL_FORM_LEMMA_CANDIDATE__NOT_A_SOLVER__NO_P_VS_NP_PROMOTION`

## Purpose

Attack the universality gap directly at the representation level. An arbitrary CNF carries literal-polarity bits on variable/clause incidences. Global complementation of a variable is a semantics-preserving change of coordinates. This note proves exactly what information can be removed by those switches, and just as importantly, what remains.

No novelty claim is made. No tractability claim is made.

## Encoding

Let `F` be a finite CNF. Let `V+` be the set of variables that occur in at least one clause, and let

`I = {(C,v) : variable v occurs in clause C}`

be the literal-incidence set. Assume repeated occurrences inside one clause have first been normalized in the usual exact way; tautological clauses may be removed because they are always true.

For every incidence `(C,v)`, define a polarity / forbidden-value bit

- `p(C,v)=0` when the literal is `x_v`,
- `p(C,v)=1` when the literal is `not x_v`.

Thus a clause `C` is false exactly when every incident variable takes its forbidden bit:

`x_v = p(C,v)` for all `(C,v) in I(C)`.

## Variable switching

For any switch vector `s in {0,1}^{V+}`, introduce new variables

`y_v = x_v xor s_v`, equivalently `x_v = y_v xor s_v`.

Define transformed polarity bits

`p_s(C,v) = p(C,v) xor s_v`.

### Lemma 1 — exact SAT preservation

For every assignment `y`, let `x_v = y_v xor s_v`. Then for every clause `C`,

`C is false under x  <=>  y_v = p_s(C,v) for every v in C`.

Therefore the transformed CNF `F_s` obtained by replacing every incidence polarity `p(C,v)` by `p_s(C,v)` satisfies

`F in SAT  <=>  F_s in SAT`,

with a bijection between satisfying assignments given by `x = y xor s`.

### Proof

A literal on incidence `(C,v)` is false exactly when `x_v=p(C,v)`. Substituting `x_v=y_v xor s_v` gives

`y_v xor s_v = p(C,v)`

iff

`y_v = p(C,v) xor s_v = p_s(C,v)`.

Conjoin over all incidences of the clause, then over all clauses. The map `y -> x=y xor s` is its own inverse, so the assignment correspondence is bijective. QED.

## Switching orbits

The group `{0,1}^{V+}` acts on the incidence-polarity vector `p in {0,1}^I` by toggling every incidence of a selected variable.

### Lemma 2 — the action is free on active variables

If `p_s=p`, then `s_v=0` for every active variable `v`.

### Proof

For every active `v`, choose any incident clause `C`. Equality `p_s(C,v)=p(C,v)` implies `p(C,v) xor s_v = p(C,v)`, hence `s_v=0`. QED.

Consequently every switching orbit has exactly `2^{|V+|}` polarity labelings, and for a fixed incidence hypergraph the number of switching orbits is exactly

`2^{|I|-|V+|}`.

## Rooted normal form and complete defect invariant

For each active variable `v`, choose one designated incident clause `r(v)`. This choice may be any deterministic rule relative to the fixed encoded input; this lemma does **not** claim polynomial canonical graph labeling under arbitrary variable renaming.

Set

`s_v = p(r(v),v)`.

Then the transformed root incidence satisfies

`p_s(r(v),v)=0`.

For every other incidence define the relative defect bit

`d(C,v) = p(C,v) xor p(r(v),v)`.

### Lemma 3 — defects are switching-invariant and complete

For any switch vector `t`,

`[p(C,v) xor t_v] xor [p(r(v),v) xor t_v] = d(C,v)`.

So the defect bits are invariant under variable switching.

Conversely, if two polarity labelings `p` and `q` on the same incidence structure have identical relative defects with respect to the same roots, then there is a unique switch vector `s` such that `q=p_s`, namely

`s_v = p(r(v),v) xor q(r(v),v)`.

Hence the rooted defect vector is a complete invariant of the switching orbit.

### Proof

Invariance follows by cancellation of the duplicated toggle bit. For completeness, define `s_v` from the two root bits. Equality of defects gives

`p(C,v) xor p(r(v),v) = q(C,v) xor q(r(v),v)`.

Rearranging and substituting the definition of `s_v` yields `q(C,v)=p(C,v) xor s_v` for every incidence. Uniqueness follows from freeness. QED.

## Complexity

Given the explicit incidence list and designated roots, constructing the rooted switching normal form, the switch vector, and all defect bits takes `O(|I|)` bit operations apart from ordinary input parsing / deterministic root selection bookkeeping. Reconstruction of an original satisfying assignment is also `O(|V+|)`.

Thus this normalization is exact and polynomial.

## Critical universality obstruction exposed by the lemma

This normalization removes exactly one polarity degree of freedom per active variable and no more. The residual defect dimension is

`D = |I| - |V+|`.

For exact 3-CNF with `m` non-tautological 3-clauses, `|I|=3m`, so

`D = 3m - |V+|`.

`D` can be linear in the input size. For example, any 3-uniform instance with `m=n` active variables and all variables of degree 3 has `D=2m`.

Therefore enumerating all defect states would require `2^D` states in such families. The switching lemma by itself **does not** establish the polynomial-state obligation `U4` and is not a SAT algorithm.

This is the useful result of the attack: the nonessential global polarity gauge is removable in polynomial time, while the true remaining universality problem is an exact compression/solution of a potentially linear-dimensional switching-invariant defect structure coupled through the clause hypergraph.

## Next proof obligation

The next admissible question is not `can we enumerate the defects?` — that is exponentially large in general.

The next obligation is:

`U-SWITCH-1: find an exact polynomial-size sufficient statistic of the rooted defect structure plus incidence hypergraph that determines SAT and supports polynomial SAT reconstruction / UNSAT certification, or freeze a rigorous counterexample to the proposed statistic.`

Any candidate statistic must be preregistered before target-aware tuning and must survive formulas with:

- trivial variable automorphism group,
- linear defect dimension,
- no logarithmic separator,
- large connected core,
- both SAT and UNSAT controls.

Until `U-SWITCH-1` is closed with a universal symbolic bound:

`GENERAL_SAT_IN_P = NOT_PROVED`

`P_VS_NP = OPEN`
