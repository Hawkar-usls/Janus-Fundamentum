# R47C — first certified macro; global argmin is not local proof authority

Let `F` be a current canonical state. For a pivot `v`, the frozen R45A candidate constructor independently checks exact-DP replay and its polynomial intermediate envelope, runs the frozen normalization stack, reconstructs a SAT witness when applicable, and marks the candidate `accepted` iff its result is either independently verified terminal or has strict frozen lexicographic CLV descent.

Suppose the deterministic variable scan reaches a pivot `v` whose candidate `M_v` is accepted and whose independent macro replay passes.

Then no statement about a later pivot `w` is needed to justify applying `M_v`:

1. **Semantic correctness is local.** The certificate/replay for `M_v` establishes the semantics of the chosen transition. A comparison against another candidate cannot strengthen or weaken that certificate.
2. **Progress is local.** Acceptance already gives `TERMINAL(M_v(F))` or `CLV(M_v(F)) < CLV(F)`.
3. **Polynomial work is preserved.** The first-accepted scan inspects a prefix of the at-most-`V` candidates inspected by the full scan. R47B establishes polynomial work per candidate; any prefix is therefore polynomial.
4. **Polynomial accepted-step height is preserved.** The previously sealed CLV-height lemma applies to every accepted nonterminal transition individually; it does not require maximal decrease. Any sequence of strict CLV decreases has polynomially bounded length inside the frozen accepted-state box.
5. **Determinism is preserved.** Variables are visited in canonical increasing order; the first accepted pivot is uniquely determined by the input and frozen implementation.

Therefore:

`FIRST_ACCEPTED_AND_REPLAYED => STOP_SCANNING`

is sound for **local correctness, progress and polynomial termination composition**. The current global `selection_key`/argmin is an optimization/policy choice, not proof authority.

## Coverage boundary

This theorem does **not** establish universal success of the new policy. Choosing the first accepted transition may reach a different later state from choosing the globally best accepted transition. Consequently the theorem-critical O4 obligation becomes:

`FOR ALL states reachable under FIRST_ACCEPTED_POLICY: terminal OR an accepted certified transition exists.`

That obligation remains OPEN. No finite corpus can close it.

Firewalls:

- `FIRST_POLICY_UNIVERSAL_COVERAGE = NOT_PROVED`
- `R47A_UNIVERSAL_COVERAGE = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `P_VS_NP = OPEN`
- `TRUMP_finished = false`
