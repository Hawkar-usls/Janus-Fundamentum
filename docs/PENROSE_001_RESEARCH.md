# JANUS-PENROSE-001 — Global Consistency Witness for Reversible Schedules

**Status:** research-only safety check for JANUS-DEUTSCH-003. **No SAT speedup, no new P=NP theorem, no physical Penrose staircase, and no quantum-hardware result.** Production C023 is untouched. PR #574 remains draft.

## Historical and scientific source

Lionel S. Penrose and Roger Penrose, *Impossible Objects: A Special Type of Visual Illusion*, British Journal of Psychology 49(1), 31–33 (1958), DOI 10.1111/j.2044-8295.1958.tb00634.x.

The staircase image looks locally consistent at each step, yet any strictly ascending closed loop would require the same height to be higher than itself. This is used here **only as a logical analogy**, not as a claim that the visual illusion provides a quantum algorithm.

Independent contextual descriptions:
- https://wellcomecollection.org/works/gtyrttpz
- https://collection.sciencemuseumgroup.org.uk/objects/co59923/first-models-of-the-impossible-triangle-and-impossible-staircase

## Formal audit rule

For every strict scheduling precedence requirement u -> v, demand an integer event rank h such that:

    h(v) >= h(u) + 1

On a closed directed cycle of k strict increases, summing implies:

    h(start) >= h(start) + k

which is contradictory when k>0. Local event constraints are individually harmless; together they may be impossible.

JANUS-PENROSE-001 uses Kahn topological sorting (O(V+E)) to construct a satisfying longest-path rank potential for an acyclic graph. If no such ranking exists, an independent iterative DFS returns an **explicit directed cycle witness** for inspection. This does not solve SAT; it is a straightforward graph-scheduling consistency check.

**Critical distinction:** a reversible quantum circuit may legitimately toggle the *same physical register* during computation and again during uncomputation. Such reuse does NOT create a prohibited strict temporal cycle. The graph nodes are **individual operation events**, not register names or state values. Invalid future-before-past dependencies are what the Penrose analogy detects.

## Integration in JANUS-DEUTSCH-003

- experiments/direct/janus_penrose_001.py: graph consistency audit and independently constructed reversibility schedule witness.
- tests/test_penrose_001.py: reject four-corner impossible strict-rise cycle, accept acyclic staircases, reject malformed/self/cyclic dependencies, verify exact compute–target–uncompute instruction schedule, test intentionally corrupted schedules, validate safe repeated register reuse, and compare MAJ3-K4 oracle outputs on deterministic samples.
- experiments/direct/janus_penrose_001_benchmark.py: JSON with positive/negative controls and MAJ3-K4 metrics, including operation count and precedence-rank witness summary.
- .github/workflows/validate-deutsch-003.yml: makes the Penrose negative-control and valid-schedule tests required research CI steps.

For MAJ3-K4, Deutsch-003 has **4,161 logical reversible operation events** in one strict, acyclic temporal sequence. Validator checks unique event identities, a constructive rank certificate, exact clause toggles, reversible symmetry around the target operation, and unmodified 113-qubit/32-control resource estimates.

The deliberately injected edge from the last event to the first event creates a positive directed cycle. It **must fail** with a graph cycle witness. A false positive would be treating legitimate compute/uncompute of reused work registers as a scheduling impossibility.

## Boundaries

- This is a workflow/circuit-integrity check, not a theorem about quantum advantage.
- It is not an UNSAT proof. Those remain under the independent C023 certificate verifier.
- A DAG schedule is necessary for this sequential circuit model, not sufficient to demonstrate physically valid qubit decomposition.
- The Penrose analogy MUST NOT be used to permit cyclic dependencies without explicit nonmonotonic timing, a fixed-point semantics, or other independently audited meaning.
- UFR vs C023 two-worker speed/RSS promotion remains NOT_READY until retested and passed. This audit cannot authorize merging PR #574 or replacing C023 in main.
