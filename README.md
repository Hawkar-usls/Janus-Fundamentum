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
6. Every direct-separation funnel uses the actual input length for every circuit-size comparison.
7. Positive examples alone cannot refute arbitrary classifiers unless a formal soundness restriction excludes false-positive supersets.
8. Local type multiplicities do not determine global graph assembly.
9. A local-twin lower bound must exclude identity compilation through an explicit width lower bound and separately control global factorization.
10. Polynomial DAG sharing is charged once per gate before unfolded occurrences are used as a lower-bound resource.
11. An identical connector preserves local equality only after proving separation from every distinguishing feature.
12. Every finite positive list must charge its exact-membership SAT-sound circuit, not only witness-based covers.

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
python experiments/direct/toroidal_tseitin_twins.py --self-test
python experiments/direct/length_parameter_audit.py --self-test
python experiments/direct/connected_toroidal_tseitin_twins.py --self-test
python experiments/direct/exact_list_sound_cover.py --self-test
```

# Current status — C019

```text
NEW DESCENDANTS             3   H125-H127
CURRENT-CYCLE ATTACKS      24   A475-A498
INHERITED TARGETS          12
TERMINAL RESULTS            0
LIVE HYPOTHESES           110
TERMINAL HISTORICAL NODES  17
```

## H125 — connected high-treewidth local twins

H121 used two disjoint toroidal Tseitin lobes. C019 joins them with a five-clause bridge on fresh variables:

```text
(x ∨ z)
(¬x ∨ z)
(y ∨ w)
(¬y ∨ w)
(z ∨ w)
```

For every endpoint assignment, `z=w=1` satisfies the bridge. Thus it does not change the SAT or UNSAT status of the original Tseitin system.

The bridge creates the primal path

```text
x — z — w — y
```

and makes the full primal graph connected.

Its endpoints are placed outside every charge-visible radius. A bounded-radius root sees either a charge-altered gadget or the identical bridge, never both. The exact local equality from H121 therefore survives, and the original toroidal primal component remains as a subgraph.

```text
SAT status:                    preserved
UNSAT status:                  preserved
primal graph:                  connected
local signatures:              equal by separated features
treewidth lower bound:         at least m-1
```

```bash
python experiments/direct/connected_toroidal_tseitin_twins.py --self-test
```

Read [`proof_attempts/H125/CONNECTED_TSEITIN_BRIDGE.md`](proof_attempts/H125/CONNECTED_TSEITIN_BRIDGE.md).

## H127 — the last stated locality theorem

```text
H125 connected high-treewidth local twins
  + H127 common-quotient factorization
  -> no H106 constant-pass low-treewidth compiler
```

Disconnected input components are no longer an escape. The remaining theorem must show that every legal fixed-pass compiler producing `O(log N)` treewidth output factors through a common quotient that loses same-lobe versus split-lobe charge parity.

The conclusion must include the complete output assembly and every witness-recovery annotation. It is not currently proved.

## H126 — exact-list sound cover

For any positive list containing `m` distinct satisfiable formulas of exactly `L` bits, hardwire one equality test per formula and OR them.

The circuit accepts exactly the listed formulas, so it is globally SAT-sound. A loose standard-basis upper bound is:

```text
size <= 3mL.
```

Therefore an H124 list intended to hit every SAT-sound circuit of size `L^k` must contain:

```text
m > L^(k-1)/3
```

distinct formulas. This restriction is independent of witness diversity.

```bash
python experiments/direct/exact_list_sound_cover.py --self-test
```

Read [`proof_attempts/H126/EXACT_LIST_COVER.md`](proof_attempts/H126/EXACT_LIST_COVER.md).

## Remaining direct separation routes

### SAT circuit lower bound

```text
H124 exact-L SAT-sound anti-checker
  + more than L^(k-1)/3 distinct formulas
  + escape from the H120 witness cover
  + incompressibility against every other L^k SAT-sound circuit
  -> SAT not in P/poly
  -> P != NP
```

The formal implication is correct. The uniform list construction and universal incompressibility theorem remain open.

### Extended Frege

```text
H110 globally proof-hard equivalent endpoints
  + computable Lipschitz potential
  -> superpolynomial rewrite distance
  -> Extended Frege lower bound
  -> NP != coNP
  -> P != NP
```

H117 continues to exclude fixed EF-easy gadget composition as an endpoint source.

### Restricted local compiler obstruction

```text
H127 connected toroidal charge-quotient factorization
  -> no H106 compiler
```

This route attacks only the stated compiler class; it does not itself imply `P != NP`.

Read [`docs/C019_CONNECTED_TWINS_AND_LIST_COVERS.md`](docs/C019_CONNECTED_TWINS_AND_LIST_COVERS.md).

## Genesis boundary

Genesis preserves continuity and provenance. It does not turn fictional unlimited time into mathematical evidence. Every result enters this registry only through an explicit proof, counterexample, primary theorem, or reproducible artifact.

No JANUS result currently resolves `P` versus `NP`.
