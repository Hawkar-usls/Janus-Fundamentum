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
```

# Current status — C015

C015 compresses active priority into three funnels.

```text
NEW DESCENDANTS             6   H110-H115
CURRENT-CYCLE ATTACKS      40   A371-A410
INHERITED TARGETS          16
TERMINAL RESULTS            0
LIVE HYPOTHESES           103
TERMINAL HISTORICAL NODES  12
```

## Funnel A — Extended Frege rewrite distance

```text
H035
  -> H110 computable Lipschitz rewrite potential
  -> H111 transparent endpoint composition
  -> superpolynomial rewrite distance
  -> Extended Frege lower bound
  -> NP != coNP
  -> P != NP
```

A short Extended Frege proof is already known to induce a polynomial chain under a polynomial-time local circuit relation with at most seven new gates per step. The missing theorem is now explicit: find a polynomial-time potential with a polynomial one-step change bound and a superpolynomial endpoint gap on transparently equivalent circuits.

```bash
python experiments/direct/rewrite_chain_audit.py --self-test
```

The test checks only finite artifact semantics and cannot prove the asymptotic lower bound.

## Funnel B — one-sided SAT anti-checkers

```text
H031/H056
  -> H112 satisfiable false-negative anti-checkers
  -> H113 range-avoidance decoder preserving a SAT witness
  -> SAT not in P/poly
  -> P != NP
```

A false negative has a polynomially checkable satisfying assignment. A false positive needs an unsatisfiability certificate and adds an avoidable `coNP` obligation. C015 removes false positives from the target entirely.

```bash
python experiments/direct/sat_error_audit.py --self-test
```

The remaining wall is uniform construction: the anti-checker may not solve SAT or circuit correctness while generating its list.

## Funnel C — fixed local compiler obstruction

```text
H106/H107
  -> H114 exact local SAT/UNSAT twins
  -> H115 locality-to-treewidth transfer
  -> no fixed constant-pass H106 compiler
```

H114 requires explicit opposite-label CNFs with identical rooted signed-neighborhood multisets through the complete ancestry radius. H115 must then control global output assembly, treewidth dynamic programming, and all recovery annotations.

```bash
python experiments/direct/local_neighborhood_audit.py --self-test
```

This funnel eliminates only a restricted proposed route to `P = NP`; it is not a general lower bound against polynomial-time algorithms.

## Deprioritized, not rejected

H032, H036-H039, and H057-H059 remain live but outside the shortest current funnels. They still face tautologicity, unrestricted extraction, model-definition, or indirectness barriers.

Read [`docs/C015_DIRECT_SEPARATION_FUNNEL.md`](docs/C015_DIRECT_SEPARATION_FUNNEL.md).

## Previous exact breakthrough retained

C013-C014 produced an exact connected graph-level SAT/UNSAT collision for the standard first Lovasz-theta relaxation. It remains an unconditional limitation of that relaxation, not a solution of `P` versus `NP`.

No JANUS result currently resolves `P` versus `NP`.
