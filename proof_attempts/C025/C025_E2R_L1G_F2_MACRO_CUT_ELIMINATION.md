# C025-E2R-L1G-F2 — Negative-edge budget to macro cut-elimination cost

**Status:** `PROVED_IN_STATED_SCOPE__PROVIDER_PASS`.

Authoritative replay: run `32753914462`, job `97516954725`, head `6dd18e95c663451b5bf9cff5abba691bb9b29156`, `SUCCESS`.

Let `q` be the global number of negative crossing dependency edges and `S>=2` the explicit B2/ER3 proof volume. F1 gives per-literal structural expansion `<=S^((q+2)!)`; ER3 width three gives `B_q<=S^((q+3)!)` per source line.

The promoted v1.1 proof stays inside pure Resolution. For a context `C`, restrict by the assignment falsifying `C`, use closure of Resolution under restrictions, refute the restricted premises, and lift back to derive a subclause of `C`. The provider replay includes an overlapping context/proof-variable fixture.

For positive-closure normal form

`F = L AND (~F_1) AND ... AND (~F_k)`, `k<=q`,

resolve away local complement literals and eliminate frontier children sequentially using the pure context-lifting lemma. No disjointness of child cones is assumed. The safe recurrence yields

`R_q <= S^((q+4)!)`

for refuting `P(F) union N(F)`.

Expanding and simulating every ER3 macro pivot then gives the full bound

`S_local <= S^((q+5)!)`.

Combining with the established polynomial-input NW-parity heavy-width transfer gives, for every polynomial-size escape on the stated existential family,

`q = Omega(log N / log log N)`.

Provider gates passed:

```text
F1_NEGATIVE_EDGE_ACCOUNTING              = PASS
F1_FACTORIAL_EXPANSION_BOUND_FINITE      = PASS
F1_BOUND_MATERIALIZATION_AVOIDED          = PASS
F1_PARITY_NEGATIVE_EDGE_GROWTH           = PASS
F2_NESTED_COMPLEMENT_FIXTURES            = PASS
F2_FACTORIAL_RECURRENCE                   = PASS
F2_PURE_RESTRICTION_CONTEXT_OVERLAP      = PASS
F2_PURE_CONTEXT_SUBCLAUSE_DERIVATION     = PASS
```

Hard boundary:

```text
Q_LOWER_BOUND != SUPERPOLYNOMIAL_EXTENSION_COUNT
F2 != FULL ER_OR_EF LOWER_BOUND
SHORT_PROOF_EXISTENCE != DETERMINISTIC_PROOF_SEARCH
ISSUE_217 = OPEN
P_VS_NP = OPEN
```
