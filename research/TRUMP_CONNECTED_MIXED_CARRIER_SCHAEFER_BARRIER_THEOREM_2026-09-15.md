# TRUMP — Connected Mixed-Carrier Schaefer Barrier

Date: 2026-09-15

Authority: `CLASSIFICATION_BARRIER_THEOREM__NO_P_VS_NP_RESOLUTION`

## Frozen language

Let

- `OR2(x,y)` have relation `{01,10,11}`. This is a bijunctive/2-CNF relation.
- `EVEN_XOR3(x,y,z)` have relation `{000,011,101,110}`. This is an affine GF(2) relation.

Each relation therefore belongs individually to a standard polynomial-time Boolean CSP class.

Let `Gamma = {OR2, EVEN_XOR3}`.

## Exact finite classification

The frozen checker verifies by complete truth-table closure tests:

1. `Gamma` is not 0-valid because `OR2` excludes `00`.
2. `Gamma` is not 1-valid because `EVEN_XOR3` excludes `111`.
3. `Gamma` is not Horn: `011 AND 101 = 001`, excluded by `EVEN_XOR3`.
4. `Gamma` is not dual-Horn: `011 OR 101 = 111`, excluded by `EVEN_XOR3`.
5. `Gamma` is not bijunctive: `majority(011,101,110)=111`, excluded by `EVEN_XOR3`.
6. `Gamma` is not affine: `01 XOR 10 XOR 11 = 00`, excluded by `OR2`.

The checker also independently verifies that `OR2` is bijunctive and `EVEN_XOR3` is affine.

## Source-bound classification consequence

The preregistration binds the Boolean Schaefer dichotomy in the modern formulation of Jonsson, Lagerkvist and Osipov, *CSPs with Few Alien Constraints*, CP 2024, Theorem 2, which states that a finite Boolean constraint language is polynomial-time decidable when it is 0-valid, 1-valid, Horn, dual-Horn/anti-Horn, bijunctive, or affine; otherwise its CSP/SAT problem is NP-complete.

Because `Gamma` belongs to none of those six tractable classes, `SAT(Gamma)` is NP-complete.

This classification statement imports the published theorem; the finite closure failures themselves are independently replayed by the repository checker.

## Connected-instance implication

Any `Gamma` instance decomposes in polynomial time into connected components of its variable-constraint incidence graph. The whole instance is satisfiable exactly when every connected component is satisfiable.

Therefore, if there were a polynomial-time exact mechanism that solved every connected `Gamma` instance, applying it independently to every connected component would give a polynomial-time algorithm for arbitrary `SAT(Gamma)`.

Since `SAT(Gamma)` is NP-complete, such an unrestricted polynomial connected mixed-carrier mechanism would imply `P=NP`.

This is a conditional implication only. It does not prove that the mechanism cannot exist, and it does not resolve `P` versus `NP`.

## Meaning for TRUMP

It is not valid to assume that two individually tractable exact carriers can be combined inside an unrestricted connected core by a routine polynomial glue operation. Even the fixed pair `2CNF + affine-XOR` already spans an NP-complete Boolean constraint language.

Thus every future connected mixed-carrier PASS must rely on an additional preregistered restriction, for example a bounded cross-language interaction parameter, an exact acyclic/factorized structure, a bounded number of alien constraints, a bounded interface/rank condition, or another separately proved exact structure.

## Frozen lineage and execution

- parent factorized-feedback journal head: `e7a1d313cc3fe4665aeb0ca28b94decef3f758ad`
- preregistration: `8c8d9458a3d3f672b10285210164e183111de859`
- checker implementation: `f83c4035f15a35639280a64c186f75c3c91c65a1`
- workflow/head at execution: `59c27c0b04c6b839d7cdd39432a81094383c1c0f`
- Actions run: `34910835360`
- Actions job: `104197729077`
- run conclusion: `success`

All finite classification checks, explicit closure witnesses, source guard, native-class checks, and scientific firewalls passed. The factorized-feedback and affine wide-interface regressions also passed.

## Verdict

`PASS_SCHAEFER_MIXED_CARRIER_BARRIER`

## Firewalls

- `P_VS_NP = OPEN`
- `P_EQUALS_NP = NOT_CLAIMED`
- `P_NOT_EQUAL_NP = NOT_CLAIMED`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- no finite experiment is used as NP-hardness evidence; NP-completeness is source-bound to Schaefer's dichotomy after the exact finite language classification is independently checked
