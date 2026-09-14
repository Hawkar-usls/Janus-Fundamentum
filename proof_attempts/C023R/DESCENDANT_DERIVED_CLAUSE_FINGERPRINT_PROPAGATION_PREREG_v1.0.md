# C023R descendant derived-clause fingerprint propagation — prereg v1.0

Date: 2026-09-15
Authority: `HQ_SYMBOLIC_PREREGISTRATION__NO_SCIENTIFIC_PROMOTION`

## Parent state

Frozen family/encoding:

- q=4 Morgenstern 5-regular family;
- canonical numbering contract `Q4_CANONICAL_ENCODING_NUMBERING_CONTRACT_v1.0.md`;
- historical Policy-0A transition semantics unchanged;
- cache key is the exact canonical CNF after exhaustive pre-unit propagation and before the current local Resolution pass;
- local Resolution indexes only clauses present at pass entry; newly added resolvents are inherited by descendants but are not re-indexed in the same pass;
- pivots are processed by ascending numeric variable ID under frozen finite attempt/addition budgets;
- branch variable is maximum literal frequency with minimum numeric ID tie-break.

Already established diagnostic identities:

- cache-fiber multiplicity equals directed labeled root-to-key path count in the unique-key execution DAG;
- `m(v) <= 2^mu(v)` for ancestor merge surplus `mu(v)`;
- MAJ3 `01/10` source-semantic equality is insufficient for an exact cache diamond;
- exact two-step merge requires equality of the full historical transition keys;
- budgeted local Resolution is not generally permutation-equivariant;
- root Resolution on the degree-5 lifted family processes only a small numeric pivot prefix and accepted root additions remain endpoint-vertex-local.

## Exact target

Determine whether inherited deterministic derived clauses form an execution fingerprint strong enough to prevent linearly many independent history-bit collisions on the frozen q=4 family.

The desired positive statement is **not** merely that derived clauses depend on history. It must imply a family-wide information bound sufficient for

`max_K m(K) = 2^{o(L)}`

or an explicitly equivalent subexponential cache-fiber bound.

## Proof-ready obligations

### P1 — exact provenance recurrence

For every clause present in every descendant key/output, assign a proof provenance object rooted in original CNF clauses. Prove from the frozen transition semantics:

- restriction and unit propagation never enlarge the root provenance set;
- a recorded local resolvent has provenance equal to the union of the two pass-entry parent provenances;
- because additions are not re-indexed in the same pass, provenance merge-height increases by at most one local-Resolution layer per visited search state along any ancestry.

This is an accounting lemma only; it is not yet a fingerprint lower bound.

### P2 — exact influence condition

For two distinct branch histories `h != h'` that have the same source-semantic restricted MAJ3/Tseitin relation, characterize exactly when inherited derived clauses force different next cache keys.

No heuristic signatures are admissible. A distinguishing fingerprint must be an explicit clause or explicit deterministic transition difference derived from frozen code semantics.

### P3 — composition criterion

If one history bit is distinguishable, prove when such distinguishability composes across multiple MAJ3 blocks under canonical q=4 numbering. Conversely, if one collision cell exists, prove when exact byte-key equality composes across support-disjoint cells.

Graph automorphisms, post-result renaming and empirical independence are forbidden.

### P4 — asymptotic consequence

Only after P1–P3, derive one of:

- `NEAR_INJECTIVE_INHERITED_RESOLUTION_FINGERPRINT`: all but `o(L)` independent collision bits are recoverable/distinguished, giving `max_K m(K)=2^{o(L)}`; or
- `LINEAR_FINGERPRINT_FREE_SERIAL_DIAMONDS`: an explicit infinite symbolic construction of `Omega(L)` compatible exact merge diamonds, giving a fiber `2^{Omega(L)}` and falsifying the C022→C023 cache-fiber transfer route.

## Killer falsifier first

Before trying to prove the positive near-injective claim, search symbolically for the narrowest exact collision cell:

Two distinct frozen branch histories on a fixed bounded-radius q=4 neighborhood such that, after applying the exact historical sequence

`pre-UP -> cache-key -> local Resolution -> post-UP -> branch restriction -> ...`, 

the histories reconverge to the same byte-identical canonical cache key while all inherited derived clauses are included.

A finite executable witness may validate a proposed symbolic cell but may not define the cell or its asymptotic law.

A decisive negative result requires a proof that the cell embeds and composes `Omega(L)` times in the frozen infinite q=4 family under the canonical numbering contract.

## Forbidden actions

- fitting `m_max(n)` from finite instances;
- treating K4/K3,3 multiplicities as asymptotic evidence;
- dropping inherited resolvents from cache keys;
- treating source-semantic equality as byte-key equality;
- structural renaming or automorphism canonicalization;
- changing pivot order, budgets, branch tie-breaks, MAJ3 encoding, charge placement or graph numbering;
- importing a stronger caching/reason-learning proof system;
- using the unavailable primary lifting theorem text as if independently verified.

## Claim ceiling

This gate can only establish or falsify the cache-fiber transfer mechanism for the frozen historical Policy-0A/q=4 route.

It cannot by itself promote C022 H137 because the primary 2026 lifting-theorem premise audit is currently source-blocked under GitHub-only execution.

It does not imply a lower bound for arbitrary SAT algorithms and does not alter `P_VS_NP = OPEN`.

## Status

`FROZEN_SYMBOLIC_GATE__NO_NEW_ASYMPTOTIC_RUN`

First allowed action: prove P1 exactly, then attack P2 with the cheapest symbolic collision/fingerprint test before any larger construction.
