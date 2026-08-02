# JANUS Proof Search Laboratory

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS is a public, machine-readable laboratory for reproducible research around computational complexity, with `P` versus `NP` as its long-term target.

This repository does **not** claim that `P = NP` or `P != NP` has been proved.

## Laboratory laws

1. Computational claims require committed code, fixed inputs, expected outputs, and hashes.
2. New hypotheses must name a proof role, a next gate, older parents, and attacks.
3. New mathematics attacks the existing graph before expanding it.
4. Pressure is not converted into a terminal result without a decisive theorem, counterexample, or formulation failure.
5. Exact verification is not certificate existence or efficient discovery.
6. Every direct-separation funnel states every implication needed to reach `P != NP` and identifies its first unproved theorem.
7. Positive examples alone cannot refute arbitrary classifiers unless a formal soundness restriction excludes false-positive supersets.
8. Local type multiplicities do not determine global graph assembly.
9. Polynomial DAG sharing must be charged once per gate before unfolded occurrences are used as a lower-bound resource.

## Validate the organism

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python tools/validate_total_attack_sweep.py
python experiments/theta/conflict_graph.py --self-test
python experiments/theta/canonical_profile.py --self-test
python experiments/theta/symmetry_transport.py --self-test
python experiments/theta/rational_gram_verifier.py --self-test
python experiments/theta/rational_ldl.py --self-test
python experiments/theta/lovasz_theta_certificate.py --self-test
python experiments/theta/disjoint_union.py --self-test
python experiments/theta/theta_collision_bundle.py --self-test
python experiments/theta/complete_3cnf_collision.py --self-test
python experiments/theta/complete_3cnf_family.py --self-test
python experiments/theta/seeded_arches.py --self-test
python experiments/theta/seeded_ldl_stress.py --self-test
python experiments/direct/sat_error_audit.py --self-test
python experiments/direct/rewrite_chain_audit.py --self-test
python experiments/direct/local_neighborhood_audit.py --self-test
python experiments/direct/positive_only_antichecker_obstruction.py --self-test
python experiments/direct/contextual_ef_upper_bound.py --self-test
python experiments/direct/xor_cycle_local_twins.py --self-test
python experiments/direct/sound_witness_cover.py --self-test
```

# Current status — C017

```text
NEW DESCENDANTS             4   H117-H120
CURRENT-CYCLE ATTACKS      28   A419-A446
INHERITED TARGETS           9
TERMINAL RESULTS            2   H111,H115
LIVE HYPOTHESES           104
TERMINAL HISTORICAL NODES  16
```

## H111 destroyed — fixed gadgets cannot create a hard rewrite gap

A constant-size equivalent gadget pair has a constant-size Circuit-Frege proof. In any polynomial-size acyclic context, equivalence propagates bottom-up with constant cost per DAG gate. Shared gates are proved once, even if the unwound formula contains exponentially many occurrences.

Krajíček's exact proof-to-rewrite theorem then gives a polynomial-length chain. Therefore H111's transparent fixed-gadget amplification cannot instantiate H110.

```bash
python experiments/direct/contextual_ef_upper_bound.py --self-test
```

Read [`proof_attempts/H111/REFUTATION.md`](proof_attempts/H111/REFUTATION.md).

## Exact local SAT/UNSAT twins constructed

For every radius `R`, H118 builds two explicit 2-CNF formulas on two equal cycles:

```text
SAT:    inequality-edge counts (2,0)
UNSAT:  inequality-edge counts (1,1)
```

Their complete rooted signed-incidence neighborhood multisets through radius `R` are identical, but componentwise XOR parity gives opposite SAT labels.

```bash
python experiments/direct/xor_cycle_local_twins.py --self-test
```

Both primal graphs have treewidth at most two.

## H115 rejected — global assembly survives local equality

The identity compiler already maps the H118 pair to treewidth-two outputs. A global dynamic program sees whether the two marked XOR edges lie in the same connected component and returns opposite correct decisions.

Thus local type inventory does not determine global bounded-treewidth behavior. If H115's phrase “an H114 pair” includes the desired universal obstruction, the lemma is circular; if it means only exact local twins, H118 refutes it.

Read [`proof_attempts/H115/FORMULATION_FAILURE.md`](proof_attempts/H115/FORMULATION_FAILURE.md).

## Repaired locality front

```text
H119
  high-treewidth opposite-parity lifts
  + common local covering structure
  + theorem that every legal low-treewidth output factors through one quotient
  -> no H106 compiler
```

High input treewidth excludes the identity compiler. The common-quotient theorem must control the entire output assembly, not only rooted type counts.

## H116 narrowed by a universal sound cover

For a positive SAT list with distinct witness set `A`, the circuit

```text
C_A(F) = OR over a in A of [a satisfies F]
```

is globally SAT-sound and accepts the entire list. Its size is polynomial in the encoding length times `|A|`.

```bash
python experiments/direct/sound_witness_cover.py --self-test
```

H116 must therefore produce enough witness diversity to exceed the target `n^k` budget and must still defeat smaller semantic compressions unrelated to the listed witnesses.

## Remaining direct separation routes

### Extended Frege

```text
H110 computable Lipschitz potential
  + globally proof-hard explicit endpoints
  -> superpolynomial rewrite distance
  -> Extended Frege lower bound
  -> NP != coNP
  -> P != NP
```

H117 proves that fixed EF-easy gadget composition cannot provide those endpoints.

### SAT circuit lower bound

```text
H116 sound-circuit positive anti-checker
  + witness diversity beyond H120
  + incompressibility against every SAT-sound circuit
  -> SAT not in P/poly
  -> P != NP
```

### Restricted local compiler obstruction

```text
H119 high-treewidth lift factorization
  -> no H106 constant-pass compiler
```

This third route attacks only the stated restricted compiler model and does not itself imply `P != NP`.

Read [`docs/C017_COMPOSITION_AND_GLOBAL_ASSEMBLY.md`](docs/C017_COMPOSITION_AND_GLOBAL_ASSEMBLY.md).

## Genesis boundary

Genesis preserves continuity and provenance. It does not turn fictional unlimited time into mathematical evidence. Every result enters this registry only through an explicit proof, counterexample, or reproducible artifact.

No JANUS result currently resolves `P` versus `NP`.
