# C008 — Theta Inversion 20×20 Seed

## Principle

C008 does not replace the existing JANUS proof graph. It places a shared inversion layer over it.

The seed matrix contains:

- 15 hypotheses inherited from C006/C007;
- 5 new theta descendants, H070-H074;
- 20 reusable backside tests;
- 400 logical matrix cells, stored sparsely with `UNRUN` as the default;
- 45 cells already marked `ACTIVE`, `WEAKENED`, or `SURVIVED`.

The target is a later 100×100 matrix, but expansion is permitted only when new rows or columns add a distinct falsification mechanism.

## Why theta methods

The Lovasz theta function gives a polynomial-time semidefinite upper bound on graph independence. Under the standard clause-literal conflict graph reduction, a CNF with `m` clauses is satisfiable exactly when the graph has an independent set of size `m`.

The first theta relaxation is therefore a natural UNSAT-certificate candidate: a certified value below `m` proves that the formula is unsatisfiable. However, Feige and Ofek show that this generic route fails on a broad random-3CNF density regime, so C008 does not treat ordinary theta as a universal solver.

Theta bodies extend the first relaxation to a hierarchy related to Lasserre/Sum-of-Squares. C008 uses theta rank as a candidate measure of the complexity that remains after local lifts, auxiliary variables, and affine elimination.

## Existing hypotheses reused

### Direct and certificate routes

- H030 — explicit NP circuit lower bounds;
- H031 — certified SAT anti-checkers;
- H040 — complete residual quotienting;
- H046 — deterministic extension-PC proof search;
- H049 — certified exact model-counting decomposition.

### Structural compilers and their attackers

- H041 — finite-gate proof-carrying elimination;
- H042 — affine-cardinality decomposition;
- H043 — finite local submodular lift;
- H044 — finite local totally-unimodular lift;
- H045 — finite local constant-level SoS lift;
- H050 — elimination-to-DNNF simulation;
- H051 — communication lower-bound transfer;
- H053 — mixed XOR/random residual expansion;
- H062 — affine-stable mixed residual family;
- H067 — counting compiler escape from DNNF.

## New descendants

### H070 — Certified Lovasz-Theta Gap SAT Compiler

A concrete positive route. It requires a compiler from every CNF to a graph with an inverse-polynomial theta gap in the UNSAT case, plus polynomial-bit rational primal/dual certificates.

The generic reduction is already weakened by the Feige-Ofek failure regime. The surviving statement must therefore use a genuinely new compiler and must pass the hidden-oracle audit.

### H071 — Finite-Lift Theta-Rank Obstruction

An adversarial descendant of H045, H051, and H062. It asks for one explicit CNF family whose theta rank remains polynomially large after every permitted finite local extension grammar.

The unresolved issue is auxiliary-variable stability: existing SDP lower bounds do not automatically survive arbitrary extended formulations.

### H072 — Affine-Stable Theta-Rank Residual

A quantitative descendant of H042, H053, H062, and H064. It replaces the qualitative phrase “hard non-affine residual” with an explicit theta-rank lower bound after all certified Gaussian elimination and affine substitutions.

Pure XOR families are rejected as witnesses because the permitted compiler can eliminate them directly.

### H073 — Theta-Certificate / Proof-System Transfer

This bridge demands exact translations between rational theta-body certificates and a fixed SoS or Lovasz-Schrijver proof system, preserving degree, proof size, coefficient bits, and moment-matrix dimensions.

Conceptual equivalence is not enough: the repository needs a uniform size-sensitive theorem before theta lower bounds may be described as proof-complexity lower bounds.

### H074 — Bounded-Theta Inversion Indistinguishability

This is the backside twin route. For every fixed level and permitted preprocessing grammar, it seeks explicit SAT and UNSAT families with the same bounded theta profile.

Small finite twins are useful counterexamples to proposed invariants, but only an explicit infinite family could establish the registered universal obstruction.

## The twenty inversion tests

The matrix columns are shared attack mechanisms:

1. hidden-oracle audit;
2. two-sided correctness and coverage;
3. witness/refutation recovery;
4. bit complexity;
5. DNNF transfer;
6. Resolution/Res(XOR) transfer;
7. communication transfer;
8. polyhedral extension complexity;
9. SDP extension complexity;
10. first-level theta gap;
11. theta-rank growth;
12. auxiliary-variable stability;
13. affine-elimination stability;
14. moment-matrix size;
15. rational dual certificates;
16. explicitness and uniformity;
17. natural-proofs audit;
18. relativization/algebrization audit;
19. proof existence versus proof search;
20. inheritance and non-duplication.

## Certification

Floating-point solver output is not accepted as a proof. Any later theta computation must record:

- exact graph and polynomial-system hashes;
- solver and version;
- primal and dual residuals;
- all numerical tolerances;
- rational reconstruction or an independently checkable symbolic certificate;
- matrix dimensions and coefficient bit lengths.

## Reproduce

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
```

For a small DIMACS fixture:

```bash
python experiments/theta/conflict_graph.py fixture.cnf --exact-alpha
```

The exact-alpha option is exponential and exists only to verify the reduction on tiny inputs.

## Claim boundary

C008 creates an auditable attack surface over inherited hypotheses. It does not provide a probability estimate, a progress percentage, or a proof of `P = NP` or `P != NP`.
