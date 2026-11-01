# JANUS-DEUTSCH-002 — Direct Reversible Oracle Synthesis from CNF

**Status:** bounded classical research implementation, independently testable; **NOT** production C023 and **NOT** evidence of a quantum-computational speedup. PR #574 remains draft.

## Scientific relationship

This module follows Deutsch's universal quantum-computation model, using reversible classical control logic as an oracle that can act on a superposition. Its numerical interference/Grover experiments are *classical statevector simulations*, not executions on quantum hardware. The Deutsch–Jozsa promise algorithm and Grover search have different computational guarantees and are not arbitrary SAT oracles.

## Reversible circuit without exhaustive truth-table synthesis

Input: a CNF formula with n variables and m non-tautological, deduplicated clauses. For SAT the CNF is used directly. For Exact-One each constraint of length k is encoded as an at-least-one disjunction and all k(k−1)/2 pairwise at-most-one clauses, retaining exact semantics even with repeated and complementary literals.

For each encoded clause C_j, create a clean work ancilla w_j. Use one mixed-polarity multi-controlled-X to compute a **clause violation** into w_j. Flip output bit b conditioned on every work flag being 0, then run all clause computations in reverse to restore w_j=0.

    |x,b,0...0> -> |x, b XOR F(x), 0...0>

The full mapping is an involution on *all* work-register basis states (not only clean inputs), because it is composed of reversible gates. A clean |-> target enables phase kickback:

    O_F |x> = (-1)^F(x) |x>.

Compilation is structural: it reads clause literals, handles tautologies and duplicate encoded constraints, and emits a finite mixed-polarity MCX network. It **never enumerates 2^n assignments to build the circuit**. Exact-One encoding may grow quadratically with each input constraint width. Sorting/normalization adds its ordinary sorting costs. Circuit *simulation* still scales with statevector dimension, so none of this proves polynomial-time quantum or classical SAT.

## Cost accounting and what it excludes

- m work ancillas, 2m+1 logical mixed-control X gates (m compute, one output, m uncompute), max control count max(max clause width,m).
- For m=1024, the final all-clean comparison is itself a **1024-controlled X**. Calling it a single cheap physical gate would be misleading.
- The resource report includes a conservative textbook clean-chain decomposition estimate: additional clean scratch max(k−2), Toffoli estimates (2k−3) for k>=3, and X conjugations for negative controls. It does not include routing, hardware connectivity, T gates, noise, fault-tolerance, or actual circuit depth.
- Enumerating the number of solutions M for an ideal Grover iteration count remains **a fully charged 2^n classical scan**. For n>8 the classical statevector simulation refuses the request.
- Logical inversion and candidate checks do not establish an efficient UNSAT certificate. Prior C023 independent proof remains authoritative.

## First independent cloud data, before large-instance UFR covariance extension

Source: [workflow 41295387356](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41295387356), SHA \`180bb349b0425f6bf484ecc5b5a1274b2efe11a1\`. The original C023 serialized verifier passed, Deutsch-001 tests 8/8, Deutsch-002 tests 7/7.

| Input | Previous Deutsch-001 ANF compilation (median) | Direct Deutsch-002 compilation (median) |
| --- | ---: | ---: |
| Unique SAT n=3 | 0.0976 ms | 0.0797 ms |
| UNSAT n=3 | 0.0782 ms | 0.0345 ms |
| Balanced SAT n=3 | 0.0631 ms | 0.0358 ms |
| Exact-One n=3 | 0.0764 ms | 0.0430 ms |
| Independent 3-SAT n=6 seed173 | 1.4018 ms | 0.2385 ms |
| Independent Exact-One n=5 seed271 | 0.2489 ms | 0.2072 ms |

Note: these are same-machine five-repetition microbenchmarks of **compilation only**; no performance significance can be inferred from tiny timings. For the 3-SAT n=6 example, direct compilation was approximately 5.9 times faster, but its end-to-end *classical Grover simulation* took approximately 1.753 ms versus 0.348 ms for simple classical enumeration (~5× slower); consequently there is **no demonstrated end-to-end SAT speedup**.

**MAJ3-K4 n=18** (1024 width-9 CNF clauses, long-standing UNSAT):
- Direct CNF-to-circuit compilation median **0.02001 seconds** (3 repetitions); **no 2^18 truth table** constructed.
- Reversible logical network **2049 mixed-polarity MCX** gates, **1024 clause work ancillas**, final **1024-controlled** output X.
- Clean-chain decomposition *estimate* **2065 total input/work/output/scratch qubits**, **32765 Toffoli** gates and **20480 negative-control X conjugation gates**. This is a large theoretical resource footprint, not a feasible execution claim.
- 514 deterministic assignments checked against independently recomputed CNF satisfaction (all match); UNSAT is not inferred from these samples.
- Previously demonstrated C023 independently replayed UNSAT and UFR: **2427 vs 2354 states**, **165 verified iso hits**, with last two-runner promotion gate **NOT_READY**. This module does not rerun quantum statevector execution at n=18, and cannot change that gate verdict.

## Mandatory success and regression checks

1. Exhaustive SAT/Exact-One truth-table equality for all n<=6 seeded cases, including duplicates, tautologies, empty clauses and invalid input.
2. Both clean and arbitrary-dirty work-register basis-state reversibility/involution checks.
3. Deutsch–Jozsa constant/balanced phase and analytical Grover success probability controls.
4. Verified UFR renaming invariance; also on MAJ3-K4 18-variable formula using deterministic sampled assignments.
5. Classical C023 standalone serialized verifier and Deutsch-001 tests unchanged.
6. No deployment into production or merge from the draft until proof/latency/RSS/independent-worker requirements are met.

## Open scientific and engineering blockers

- Lowering work ancilla count below m without hiding the recomputation cost.
- Decomposing high-control output gates into a fault-tolerant native gate set with realistic qubit connectivity.
- Constructing a quantum query oracle that does not require pre-knowing M by a complete classical scan.
- Independent verification of SAT witnesses and reliable treatment of UNSAT.
- Real quantum hardware benchmarking and fair same-instance resource/performance comparison versus current C023.
