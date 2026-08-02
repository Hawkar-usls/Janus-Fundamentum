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
6. Deterministic seeds may select finite artifacts only; exact verification must follow.

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
```

# Current status — C014

Seed: `9379992`.

```text
NEW DESCENDANTS             6   H104-H109
CURRENT-CYCLE ATTACKS      40   A331-A370
TERMINAL RESULTS            2   H100,H102
LIVE HYPOTHESES            97
TERMINAL HISTORICAL NODES  12
```

## Connected theta arches

C013 produced an exact SAT/UNSAT first-theta collision and a disjoint-copy family. C014 connects consecutive copies with exact zero-entry bridge edges selected by seed `9379992`:

```text
SAT arch    (31,22)
UNSAT arch  (22,13)
```

For `r` copies the primal remains

```text
(1/r) J_r tensor X
```

and every arch occupies an exact zero entry. The old dual remains feasible by assigning multiplier zero to each arch.

Therefore both arched graphs are connected and have exact theta `8r`, while:

```text
SAT side     alpha = 8r
UNSAT side   alpha <= 7r
```

```bash
python experiments/theta/seeded_arches.py --self-test
```

Expected headline:

```text
JANUS_SEEDED_ARCH_THETA_FAMILY = PASS
```

This is `H104`. The result is graph-level; CNF conflict-graph realizability of the added arches remains open.

## H102 destroyed

H102's typed interface circuit required:

- explicit original-variable leaves;
- disjoint support at every AND;
- deterministic alternatives at every OR.

That is a d-DNNF of the same size. Existing explicit exponential DNNF lower bounds therefore destroy the claimed universal polynomial compiler without a projection loophole.

Read [`proof_attempts/H102/REFUTATION.md`](proof_attempts/H102/REFUTATION.md).

## H100 rejected and replaced

H100's decreasing potential and prohibition on a global acceptance channel were not syntactically defined. A local work-tape simulation with a decreasing clock remained admissible.

`H106` replaces it by exactly `q` synchronous radius-`r` passes and radius-`qr` ancestry for every output symbol.

## Certificate arches

`H108` supplies a candidate polynomial bit bound for rational LDL certificates:

- clear denominators;
- use fraction-free symmetric elimination;
- express entries as ratios of minors;
- bound minor bit length by Hadamard's inequality.

`H109` proves a conditional strict-dual rounding route: with PSD margin `delta`, objective gap `gamma`, and multiplier bound `2^B`, a sufficiently fine dyadic grid preserves half of both margins and yields polynomial-bit exact data.

The remaining wall is whether H097's original assumptions imply a polynomial multiplier bound.

## Attack-born descendants

```text
H098/H099/H103 -> H104 connected theta arches
H102/H016/H061 -> H105 exact d-DNNF transfer
H100/H009/H027 -> H106 constant-pass local compiler
H103/H088/H104 -> H107 pseudoexpectation transport
H092/H089/H084 -> H108 LDL bit bound
H097/H093/H108 -> H109 strict dual rounding
```

Read [`docs/C014_SEEDED_ARCHES.md`](docs/C014_SEEDED_ARCHES.md).

## Remaining walls

1. CNF or CSP realization of the connected theta arches.
2. Uniform pseudoexpectation transport through every H103 one-pass gadget.
3. A restriction-robust mixed XOR/non-affine generator for H101.
4. Locality lower bounds against H106.
5. Deriving bounded dual multipliers from conditioning alone.
6. The major full proof-system lower-bound and upper-bound duels.

No JANUS result currently resolves `P` versus `NP`.
