# C023R P0 correction — inherited resolvents and source-projection ambiguity

Authority: `SELF_CORRECTION__SYMBOLIC__NO_SCIENTIFIC_PROMOTION`

## Correction trigger

Source review of frozen `experiments/direct/janus_tear_policy0a_fc_trace.py` shows:

1. a state cache key is formed after pre-unit propagation;
2. deterministic local Resolution produces `saturated`;
3. post-unit propagation produces `post`;
4. each child input is `simplify_one(post, branch_variable, value)`.

Therefore clauses added by local Resolution are inherited by descendant inputs and can survive into later cache keys.

The prior proof note `TRUMP_C023R_P1_P3_EXACT_COLLISION_DECOMPOSITION_2026-09-15.md` incorrectly treated an arbitrary descendant key as if it were only a union of restricted source truth-table factors. Its source-scope recovery Lemmas P1.3/P1.4 are not valid for the full historical Policy-0A key without an additional provenance argument.

This correction is append-only. The earlier note is preserved as a failed intermediate derivation, not silently rewritten.

## Lemma P0.1 — surviving source clauses remain represented

Fix one unfolded execution occurrence and let `A` be the cumulative partial assignment consisting of all branch decisions and all forced unit assignments applied on the path.

Let `S(A)` be the canonical CNF obtained by applying exactly `A` to the original lifted source CNF, without adding local resolvents.

Because local Resolution only adds clauses and each subsequent restriction/unit step is applied to the whole current clause set, every surviving restricted source clause is still present in the historical key, modulo canonical duplicate collapse.

Hence

`S(A) subseteq K(A)`

as canonical clause sets.

This inclusion is safe. Equality is not claimed.

## Definition — source projection ambiguity

For a reachable historical cache key `K`, define

`Sigma(K) = { S(A) : A is a reachable normalized execution context with K(A)=K }`.

Define

`pi(K) = log2 |Sigma(K)|`.

`pi(K)` measures how many distinct restricted source CNFs can be hidden under one identical provenance-free historical cache key because inherited derived clauses fill or duplicate source-clause differences.

This quantity was absent from the first cache-fiber algebraic decomposition.

## Exact fiber partition

For each `S in Sigma(K)`, let

`F(K,S) = { A : K(A)=K and S(A)=S }`.

Then exactly

`m(K) = sum_{S in Sigma(K)} |F(K,S)|`.

Therefore

`m(K) <= |Sigma(K)| * max_S |F(K,S)|`

and

`log2 m(K) <= pi(K) + max_S log2 |F(K,S)|`.

Within one fixed source projection `S`, the MAJ3 local-restriction and GF(2) syndrome analysis remains potentially applicable. Across different `S`, it is not enough.

## Consequence

The cache-fiber route now has an additional mandatory theorem obligation:

> Bound `pi(K)` sublinearly for every reachable key, or exhibit an infinite family with `pi(K)=Omega(L)`.

A subexponential bound on MAJ3 stifling/cycle-space representatives alone is insufficient if exponentially many distinct source projections collapse to the same inherited-resolvent key.

## Relationship to historical C023 H139

This is not identical to the old reusable-clause problem, but it is structurally related. H139 asked for context-independent reusable reasons for cache targets. `pi(K)` asks how much source/provenance information a provenance-free cache key can erase after deterministic inherited Resolution additions.

No claim is made that H139 is closed.

## Revised collision ledger

Any valid upper bound on one historical cache fiber must charge at least:

- `pi(K)` — source-projection/provenance ambiguity;
- local MAJ3 same-function history multiplicity inside a fixed source projection;
- GF(2) constant-flip/cycle-space ambiguity;
- any remaining small-scope/source-factor conjunction ambiguity;
- execution reachability constraints.

## Scientific effect

`P1.3_SOURCE_RECOVERY_FROM_FULL_KEY = RETRACTED`.

`C023R_CACHE_FIBER_THEOREM = OPEN`.

`C022_NO_CACHE_RESULT = UNCHANGED`.

`P_VS_NP = OPEN`.
