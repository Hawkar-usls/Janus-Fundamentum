# C015 — Direct separation funnel

C015 reduces active priority to three chains. Each chain either ends in a formal
route to `P != NP` or eliminates a restricted proposed route to `P = NP`.

## Cycle scope

- six descendants: `H110-H115`;
- forty attacks: `A371-A410`;
- sixteen inherited hypotheses re-attacked;
- no terminal result;
- three executable artifact audits;
- no new broad theta branch.

## Funnel A — Extended Frege rewrite distance

```text
H035
  -> H110 explicit Lipschitz rewrite potential
  -> H111 transparent endpoint composition
  -> superpolynomial rewrite distance
  -> superpolynomial Extended Frege proofs
  -> NP != coNP
  -> P != NP
```

The external rewrite theorem supplies the middle transfer: short Extended
Frege equivalence proofs imply polynomial-length chains under a polynomial-time
relation whose steps add at most seven gates after possible deletions.

C015 does not possess the potential. It fixes exactly what must be proved:
polynomial-time computability, a universal one-step bound, transparent endpoint
equivalence, and a superpolynomial endpoint gap.

## Funnel B — one-sided SAT anti-checkers

```text
H031/H056
  -> H112 false-negative-only anti-checkers
  -> H113 range-avoidance decoder preserving a SAT witness
  -> SAT not in P/poly
  -> P != NP
```

A false negative has an ordinary satisfying assignment. A false positive needs
an unsatisfiability certificate and therefore adds an avoidable coNP burden.
C015 removes that burden.

The remaining wall is still severe: construct a universal polynomial list of
satisfiable counterexamples without solving SAT or evaluating circuit
correctness nonuniformly.

Current range-avoidance work demonstrates strong connections to circuit lower
bounds, including near-maximum lower bounds for exponential-time classes, but
those results do not automatically give the SAT-specific one-sided decoder
H113.

## Funnel C — local compiler impossibility

```text
H106/H107
  -> H114 exact high-girth local SAT/UNSAT twins
  -> H115 locality-to-treewidth transfer
  -> no fixed constant-pass H106 compiler
```

This funnel does not directly prove `P != NP`; it removes one proposed path to
`P = NP` and forces any successful algorithm to use a genuinely nonlocal
resource.

The hard pair must match exact rooted signed-neighborhood multisets through the
full ancestry radius, including multiplicities. H115 must then control global
assembly, canonical treewidth dynamic programming, and recovery annotations.

## Routes deliberately deprioritized

C015 keeps the following historical hypotheses alive but outside the shortest
funnel:

- H032 until tautologicity is independently fixed;
- H036 until a concrete canonical-pair separator invariant is selected;
- H037 until unrestricted full-IPS extraction is available;
- H038 until the PIT-axiom dichotomy is proved exhaustive and constructive;
- H039 as a barrier breaker rather than a direct SAT separation;
- H057-H059 as intermediate circuit-frontier work.

Deprioritized does not mean false.

## Reproduction

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python tools/validate_total_attack_sweep.py
python experiments/direct/sat_error_audit.py --self-test
python experiments/direct/rewrite_chain_audit.py --self-test
python experiments/direct/local_neighborhood_audit.py --self-test
```

All earlier exact theta and rational-certificate tests remain active.

## Claim boundary

C015 does not prove a circuit lower bound, an Extended Frege lower bound, a
locality lower bound, or `P != NP`. It converts three broad directions into
explicit sufficient theorems and removes the two-sided certificate obligation
from the SAT anti-checker route.
