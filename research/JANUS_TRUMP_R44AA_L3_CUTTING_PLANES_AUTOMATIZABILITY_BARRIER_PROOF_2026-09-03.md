# JANUS TRUMP R44AA — direct L3 Cutting Planes proof-search barrier

## Fixed proof language

The selected proof language is standard dag-like **Cutting Planes (CP)** for CNF refutation. Clauses are encoded as integer linear inequalities over Boolean variables; derivations use the standard Cutting Planes inference rules and refute an unsatisfiable input by deriving a contradictory inequality.

This choice is strictly beyond the already-blocked Resolution route in proof-size strength:

1. Cutting Planes polynomially simulates Resolution.
2. There are standard CNF families, notably pigeonhole-principle formulas, with polynomial-size Cutting Planes refutations but exponential-size Resolution refutations.

Therefore this is not a renamed Resolution proof language.

## Published search-hardness theorem

Göös, Koroth, Mertz and Pitassi, *Automating Cutting Planes is NP-Hard*, STOC 2020, DOI `10.1145/3357713.3384248`, prove that given an unsatisfiable CNF formula `F`, it is NP-hard to find a dag-like Cutting Planes refutation in time polynomial in the length of the shortest Cutting Planes refutation of `F`.

Equivalently for the present TRUMP use: unrestricted standard CP is not a polynomial-time automatable proof-search language unless `P=NP`.

## Consequence for Legend obligation L3

L3 asks for deterministic polynomial discovery/local work, charged to the original input size. Moving from Resolution to CP can remove some proof-*size* obstructions, but it does not make generic proof *search* an easier intermediate step.

The admissible conclusion is therefore

`SEARCH_HARDNESS_BARRIER(CUTTING_PLANES)`.

The invalid inference is

`SHORT_CP_PROOF_EXISTS => POLYTIME_CP_PROOF_DISCOVERY`.

The published theorem blocks precisely that inference in the standard automatizability setting.

If a future TRUMP constructor uses CP as only a sublanguage but has additional mathematically specified structure that provably avoids generic CP proof search, that constructor must receive a separate theorem. It cannot inherit polynomial discovery merely from CP's proof-size power.

Likewise, this result cannot be transferred automatically to every proof system stronger than CP. Proof-size simulation is not proof-search simulation.

## Epistemic boundary

This barrier does **not** prove `P!=NP`. It says that standard CP automatization cannot be advertised as an easier route to L3: a polynomial automator would itself imply a collapse at the final complexity frontier.

No benchmark, empirical runtime, solver implementation, or CI run has theorem authority here.

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
