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
```

# Current status — C018

```text
NEW DESCENDANTS             4   H121-H124
CURRENT-CYCLE ATTACKS      28   A447-A474
INHERITED TARGETS          12
TERMINAL RESULTS            1   H116
LIVE HYPOTHESES           107
TERMINAL HISTORICAL NODES  17
```

## H116 rejected — circuit size used the wrong parameter

H116 bounded candidate circuits by `n^k` while allowing the generated formula length to be `L_k(n)=n^{d(k)}` with a `k`-dependent exponent.

A hypothetical SAT circuit of size `L^3` becomes `n^{3d(k)}`. With the allowed choice `d(k)=k^2`, this exceeds `n^k` for every `k`, so H116's claimed implication to `SAT not in P/poly` did not follow.

```bash
python experiments/direct/length_parameter_audit.py --self-test
```

`H124` repairs the quantifiers: every formula has exactly `L` encoded bits and every attacked circuit has size at most `L^k` on that same input domain.

The construction remains open and still faces H120's SAT-sound witness cover plus arbitrary semantic compression.

Read [`proof_attempts/H116/PARAMETER_FAILURE.md`](proof_attempts/H116/PARAMETER_FAILURE.md).

## H121 — exact high-treewidth local twins

For every fixed radius `R`, set

```text
m = 8R + 13
```

and use two disjoint `m × m` toroidal grids. Edge variables satisfy one degree-four Tseitin parity equation at every grid vertex.

```text
SAT component charges:    (2,0)
UNSAT component charges:  (1,1)
```

The formulas have opposite satisfiability, while their complete translation-normalized rooted signed-incidence signature multisets through radius `R` are exactly equal.

```bash
python experiments/direct/toroidal_tseitin_twins.py --self-test
```

The SAT assignment is constructed through a spanning tree. The UNSAT result follows because XORing all equations in an odd-charge component gives `0=1`.

## Identity compilation is finally excluded

The primal graph of a standard edge-variable Tseitin CNF is exactly the line graph of its underlying graph.

Primary results give:

```text
tw(T_m) = 2m - 1
tw(L(G)) >= (tw(G)+1)/2 - 1
```

Therefore:

```text
tw(primal H121) >= m - 1 = Omega(sqrt(N)).
```

Unlike the H118 cycle pair, the H121 input itself is not an `O(log N)`-treewidth output. The identity compiler is no longer a legal escape.

Read [`proof_attempts/H121/TOROIDAL_TSEITIN_TWINS.md`](proof_attempts/H121/TOROIDAL_TSEITIN_TWINS.md) and [`proof_attempts/H122/PRIMAL_TREEWIDTH_TRANSFER.md`](proof_attempts/H122/PRIMAL_TREEWIDTH_TRANSFER.md).

## The remaining locality theorem

```text
H121 exact high-treewidth local twins
  + H123 common-quotient factorization
  -> no H106 constant-pass low-treewidth compiler
```

H123 must prove that every legal fixed-pass transduction producing `O(log N)` treewidth factors through a common local quotient and therefore loses the bit distinguishing:

```text
two charges in one component
versus
one charge in each component.
```

The theorem must cover the complete output assembly and every witness-recovery annotation. It is not currently proved.

## Remaining direct separation routes

### SAT circuit lower bound

```text
H124 exact-L SAT-sound anti-checker
  + witness diversity beyond H120
  + incompressibility against every L^k SAT-sound circuit
  -> SAT not in P/poly
  -> P != NP
```

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
H123 toroidal charge-quotient factorization
  -> no H106 compiler
```

This route attacks only the stated compiler class; it does not itself imply `P != NP`.

Read [`docs/C018_TOROIDAL_TSEITIN.md`](docs/C018_TOROIDAL_TSEITIN.md).

## Genesis boundary

Genesis preserves continuity and provenance. It does not turn fictional unlimited time into mathematical evidence. Every result enters this registry only through an explicit proof, counterexample, primary theorem, or reproducible artifact.

No JANUS result currently resolves `P` versus `NP`.
