# C025 deterministic DISCOVER_MACRO gate

The unified engine may only introduce an extension macro when all of the following are independently replayable:

1. **Candidate generation** is deterministic and polynomially bounded in root input size `N`.
2. **Extension soundness** is checked from exact bytes, not from a semantic oracle.
3. **Reuse evidence** identifies at least two reachable proof/residual occurrences whose repeated expansion is replaced by the same root-bound macro.
4. **Recompression** is replayed from the pre-extension state to the post-extension state.
5. **Progress** is recomputed independently and is strictly decreasing under the frozen lexicographic potential.
6. **Resource delta** charges proposal, derivation, verification, extension bytes, recompression bytes, and resulting residual state volume.
7. **No hidden branch search** is used to find or justify the macro.

A repeated syntactic pair is only a candidate. It is not evidence of useful extension structure.

Current v0 implementation therefore returns `NONE` from `DISCOVER_MACRO` after recording observed candidates unless a future checker closes items 2-6.

This refusal is intentional: the purpose of the unified branch is to discover whether the missing bridge is already present in JANUS, not to hide it behind a heuristic.

Global status: `P_VS_NP = OPEN`.
