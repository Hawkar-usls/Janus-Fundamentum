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
```

# Current status — C016

C016 attacks the shortest C015 funnel before attempting construction.

```text
NEW DESCENDANTS             1   H116
CURRENT-CYCLE ATTACKS       8   A411-A418
INHERITED TARGETS           4
TERMINAL RESULTS            2   H112,H113
LIVE HYPOTHESES           102
TERMINAL HISTORICAL NODES  14
```

## Decisive obstruction

The C015 positive-only route required every polynomial-size candidate SAT circuit to reject at least one listed satisfiable formula. The constant circuit

```text
C_top(F) = 1
```

accepts every satisfiable formula, so it has no false negative on any positive-only list. It is still not a SAT decider because it accepts unsatisfiable formulas.

Therefore:

- `H112` is destroyed by `A411`;
- `H113` is destroyed by `A412` because no decoder can output a satisfiable `F` with `C_top(F)=0`.

```bash
python experiments/direct/positive_only_antichecker_obstruction.py --self-test
```

Expected headline:

```text
JANUS_POSITIVE_ONLY_ANTICHECKER_OBSTRUCTION = PASS
```

## Repaired direct SAT route

`H116` restricts the quantified circuits to circuits sound for SAT:

```text
C(G)=1  ->  G is satisfiable.
```

The repaired implication chain is:

```text
H116 sound-circuit positive anti-checker
  -> no polynomial-size exact SAT circuit
  -> SAT not in P/poly
  -> P != NP
```

The first unproved theorem is now precise: construct a uniformly generated, fully charged positive list that no small SAT-sound circuit covers, without testing soundness or solving SAT.

A second attack remains active: a circuit can hardcode membership in the listed satisfiable formulas and remain sound. Its size must be compared explicitly with the target `n^k` budget.

Read [`proof_attempts/H112/POSITIVE_ONLY_OBSTRUCTION.md`](proof_attempts/H112/POSITIVE_ONLY_OBSTRUCTION.md) and [`docs/C016_POSITIVE_ONLY_OBSTRUCTION.md`](docs/C016_POSITIVE_ONLY_OBSTRUCTION.md).

## Other active funnels

### Extended Frege rewrite distance

```text
H035
  -> H110 computable Lipschitz rewrite potential
  -> H111 transparent endpoint composition
  -> superpolynomial rewrite distance
  -> Extended Frege lower bound
  -> NP != coNP
  -> P != NP
```

The missing theorem remains a polynomial-time potential with polynomial one-step change and a superpolynomial endpoint gap on transparently equivalent circuits.

### Fixed local compiler obstruction

```text
H106/H107
  -> H114 exact local SAT/UNSAT twins
  -> H115 locality-to-treewidth transfer
  -> no fixed constant-pass H106 compiler
```

This route eliminates only the stated restricted compiler class; it is not a lower bound against unrestricted polynomial-time algorithms.

## Genesis boundary

Genesis may preserve continuity, identity, and a research chronicle. It does not convert fictional unlimited time into evidence. Every result re-enters the registry only through an explicit proof, counterexample, or reproducible artifact.

No JANUS result currently resolves `P` versus `NP`.
