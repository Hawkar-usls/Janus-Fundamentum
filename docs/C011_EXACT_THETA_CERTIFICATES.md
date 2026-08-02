# C011 — Exact theta certificates and finite collision seeds

C011 continues the inherited theta branch by separating four questions that
must not be conflated:

1. can a rational PSD claim be checked exactly? (`H092`)
2. can an exact theta optimum be checked from supplied primal/dual objects?
   (`H093`)
3. can a dual upper bound alone certify UNSAT? (`H094`)
4. does a finite SAT/UNSAT theta collision seed exist? (`H096`)

The first three now have executable certificate formats. The fourth remains an
open search target; no positive fixture is registered.

## Cycle output

- six descendants: `H092-H097`;
- thirty attacks: `A257-A286`;
- six inherited routes re-attacked: `H070`, `H081`, `H084`, `H085`, `H087`,
  and `H089`;
- no terminal result;
- cumulative inversion matrix: `46 × 46 = 2116` logical cells;
- inherited matrix share: `40/46`.

## H092 — rational LDL instead of rational square roots

An ordinary rational Gram certificate `Q = B^T B` can be too restrictive:
even when `Q` has rational entries, a factor `B` may require irrational square
roots. H092 uses

```text
P Q P^T = L D L^T
```

with rational unit-lower `L`, nonnegative rational diagonal `D`, and a
permutation `P`.

The constructor and verifier use exact `fractions.Fraction` arithmetic:

```bash
python experiments/theta/rational_ldl.py --self-test
```

The universal algebraic induction is recorded in
`proof_attempts/H092/RATIONAL_LDL.md`. The remaining weakness is a fully stated
binary bit-growth proof.

## H093 — exact Lovasz-theta optimum certificates

C011 fixes one SDP convention:

```text
maximize <J,X>
subject to Tr(X)=1
           X_ij=0 for graph edges
           X is PSD
```

The dual slack is

```text
S = t I + sum_e y_e A_e - J
```

where `A_e` has ones in the two symmetric edge positions.

A certificate is accepted only when:

- the primal trace and edge constraints hold exactly;
- the primal and dual PSD matrices pass exact H092 LDL replay;
- primal and dual objectives are exactly equal.

```bash
python experiments/theta/lovasz_theta_certificate.py --self-test
```

The self-test certifies `theta(K2)=1` and `theta(E2)=2`, then mutates a valid
certificate and requires rejection.

H093 does **not** claim every optimum is rational.

## H094 — one-sided UNSAT certification

For a CNF conflict graph with `m` clause cliques:

```text
alpha(G) <= theta(G) <= t < m
```

contradicts satisfiability, because SAT would require `alpha(G)=m`.

Therefore a dual feasible rational upper bound below `m` is sufficient. No
primal optimizer and no exact theta value are needed.

The current generic verifier still needs graph-to-CNF hash binding before it is
a complete submission artifact. It is deliberately one-sided: failure to find
a gap never implies SAT.

## H095 — finite seed to infinite family

Disjoint variable ranges make the conflict graph of a conjunction a graph
disjoint union. The code checks:

- no cross-component conflict edges;
- additive vertex and edge counts;
- exact alpha additivity on small fixtures.

```bash
python experiments/theta/disjoint_union.py --self-test
```

The theta-additivity proof under the exact H093 normalization is kept as a
separate written obligation in
`proof_attempts/H095/DISJOINT_AMPLIFICATION.md`.

## H096 — no fabricated positive collision

The collision bundle requires:

- equal positive clause targets;
- opposite exact alpha labels;
- exact H093 certificates for both graphs;
- exactly equal theta values.

```bash
python experiments/theta/theta_collision_bundle.py --self-test
```

The self-test uses one SAT and one UNSAT graph whose theta values differ. The
verifier must reject them. This tests the rejection path without pretending
that JANUS has found the desired collision.

Once a real seed is found, H095 would amplify it into an explicit family.

## H097 — verification is not existence

Exact replay does not prove that short rational certificates always exist.
H097 isolates a conditioned reconstruction theorem:

- primal and dual Slater margins at least inverse polynomial;
- objective separation margin at least inverse polynomial;
- rational approximation preserving feasibility and a constant fraction of
  the gap;
- polynomial total LDL encoding length.

Weakly feasible or exponentially ill-conditioned SDPs remain outside the
claim.

## Reproduction

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python experiments/theta/conflict_graph.py --self-test
python experiments/theta/canonical_profile.py --self-test
python experiments/theta/symmetry_transport.py --self-test
python experiments/theta/rational_gram_verifier.py --self-test
python experiments/theta/rational_ldl.py --self-test
python experiments/theta/lovasz_theta_certificate.py --self-test
python experiments/theta/disjoint_union.py --self-test
python experiments/theta/theta_collision_bundle.py --self-test
```

## Claim boundary

C011 does not:

- find a theta collision;
- prove theta additivity under the chosen convention;
- prove all well-conditioned certificates have polynomial bit length;
- make first-level theta a complete SAT algorithm;
- resolve `P` versus `NP`.

Its concrete progress is a stricter exact-certificate chain and a finite witness
format that cannot silently accept numerical tolerances or answer leakage.
