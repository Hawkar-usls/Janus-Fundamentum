# JANUS-UFR-001 — Ulam–Feigenbaum Structural Renormalization

**Status:** PROPOSED / FINITE EXECUTABLE EXPERIMENT / NOT ADMITTED.
**Claim ceiling:** no Feigenbaum scaling in SAT established; no universal polynomial-time algorithm; P vs NP remains OPEN.

## Purpose

C023 JANUS-FC_local currently caches only byte-for-byte identical residual CNFs and the independent serialized verifier intentionally enforces this. **This PR does not modify C023 or its certificate rules.**

Hypothesis: some syntactically different residual SAT or Exact-One formulas have a **literal-preserving variable-renaming isomorphism**, permitting verified reuse of a Boolean answer or SAT witness. This is a precise, narrow structural notion, not a claim that dynamical-systems Feigenbaum constants transfer to complexity theory. Ulam's spiral, Ulam's stochastic matrices, and Feigenbaum's bifurcation constants are separate concepts.

## Soundness contract

Constraints are signed nonzero integer-literal tuples. SAT means at least one true literal per constraint; EXACT_ONE means **exactly one literal occurrence** true. Repeated literals are retained: (x,x) is UNSAT in Exact-One; (x,-x) is SAT.

The janus_ufr_001.py core returns a relabeled key and a source-to-canonical bijection. It enumerates permutations within occurrence-signature groups (row length and literal sign) under max_variables=12, max_candidates=720. Larger searches use a **sound but incomplete** single-ordering fallback; polynomial-time canonicalization is not claimed.

For every proposed match, independent verify_renaming checks the mapping is total, injective and surjective and that complete mapped rows exactly equal target rows, including polarity and multiplicity. Hence SAT/Exact-One truth is unchanged under the bijection. Any transferred SAT witness is independently checked against the destination formula. No approximation or similarity score can authorize a match.

## Files and commands

- experiments/direct/janus_ufr_001.py: typed normalizer, bounded canonicalizer, independently checked bijection and witness transport.
- experiments/direct/janus_ufr_001_benchmark.py: complete small DPLL with either exact-residual or UFR memo key; reports wall time, Python tracemalloc peak, calls, hits, unique states and witness checks. **This is not a C023 solver comparison.**
- experiments/direct/janus_ufr_001_probe.py: read-only probe against C023 FCTracePolicy completed residuals; output counts **potential** matches, not actual admissible DFS cache hits or speedups.
- tests/test_ufr_001.py: negative/non-bijection, Exact-One multiplicity, empty-constraint, bounded fallback and seeded randomized checks.
- .github/workflows/validate-ufr-001.yml: repeatable CI with unchanged C023 independent serialized verifier.

Run:

    python -m unittest discover -s tests -p 'test_ufr_001.py' -v
    python experiments/direct/janus_ufr_001_benchmark.py
    python experiments/direct/janus_ufr_001_probe.py --fixture diamond
    python experiments/direct/janus_ufr_001_probe.py --fixture gt4

Optional, potentially expensive: python experiments/direct/janus_ufr_001_probe.py --fixture maj3-k4.

## Falsification gates

1. **Soundness:** preserve negative controls and deterministic small exhaustive tests. Any wrong answer or invalid witness invalidates the implementation.
2. **C023 opportunity:** on MAJ3-K4, GT, Tseitin and independent SAT/Exact-One, count nonidentical but verified isomorphic residuals; record their completion order and total matching cost.
3. **Independent proof replay:** before introducing isomorphic cache **edges**, define serialized ISOMORPHIC_CACHE_HIT records containing exact bijection, target state, completed-order proof, formula type and model where necessary; write a **separate verifier** that recomputes all steps. Current C023 verifier remains authoritative and unchanged.
4. **Fair performance:** preregister independent hard instances, seeds, hardware, cutoffs and negative controls. Compare actual wall time, RSS, conversion overhead, canonicalization fallbacks, full certificate size and replay cost. Synthetic renamed clones are only a positive control and may give fewer calls but **worse runtime**.
5. **Asymptotic proof:** any general polynomial upper bound must separately charge canonicalization, branch search, cache lookup, model reconstruction and certificate verification. Finite benchmarks do not prove P=NP or stronger proof systems.

**Do not merge into the production C023 search or claim universal speedup without an admitted proof rule and green independent CI.**
