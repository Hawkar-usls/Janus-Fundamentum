# C036.2 — Proof-Carrying Open-Core Vault

## Canonical lineage

```text
C036   Proof-Carrying Partition Refinement
C036.1 Horn–affine Ping-Pong
C036.2 Proof-Carrying Open-Core Vault
C037   explicit residual OBDD alignment
C038   structured vtree factor alignment
```

The Git branch `research/c038-proof-carrying-open-core-vault` is retained only
as a pre-admission legacy alias. The canonical component identifier is
`C036.2`.

## Purpose

C036.2 adds a verified exact cache for portfolio-scoped `OPEN` results. It does
not infer objective hardness and does not generalize an old failure to a new
formula.

```text
OPEN = f(formula, capability profile, budget profile, canonicalizer)
```

Reduction, similarity, or shared substructure with an OPEN core does not prove
OPEN. Only an exact canonical core digest under the identical capability digest
may reuse an earlier result, and the refusal ledger must replay.

## Capability/refusal closure

The capability manifest commits to the exact ordered detector portfolio. The
OPEN trace must contain exactly the same detector identifiers in exactly the
same order. Missing, additional, duplicated, or reordered refusal entries are
rejected.

Every textual digest uses the strict lexical form:

```text
sha256:<exactly 64 lowercase hexadecimal digits>
```

## Immutable history and logical staleness

An evaluation is keyed by `(core_digest, capability_digest)` and never mutated.
`ACTIVE` versus `STALE` is derived:

```text
ACTIVE iff evaluation.capability_digest == current_capability_digest
STALE  otherwise
```

Changing capability is one singleton UPSERT. Historical evaluations receive no
mass UPDATE.

## Verified exact lookup

```text
exact core digest
+ exact current capability digest
+ verified capability payload and digest
+ exact capability/refusal-ledger closure
+ verified core payload and domain-separated digest
+ verified trace payload and binding
+ independent refusal replay
------------------------------------------------
HIT_VERIFIED_OPEN / CACHED_OPEN_EXACT
```

Any missing verifier or integrity failure returns `HIT_CORRUPT` and forces the
ordinary portfolio path.

## Content-addressed payloads

Heavy payloads live outside SQLite under:

```text
vault/sha256/ab/cd/<digest>.<kind>
```

SQLite stores immutable digests and references. Files are written through a
flushed temporary sibling and atomic rename.

## C036.2 exclusions

No PIOC, OPEN_SLICE, structural fingerprint, similarity, isomorphism,
equivalence mapping, or reduction-based OPEN promotion is present.

## Acceptance gate

```bash
python experiments/direct/janus_c036_2_open_core_vault.py --self-test
```

The test covers deterministic capability hashing, strict 64-hex digests, exact
portfolio/ledger closure, verified hits, logical staleness, corruption,
idempotence, concurrent writers, immutable OPEN-to-CLOSED history, and absence
of structural matching.

## Claim boundary

C036.2 proves only safe version-scoped exact reuse of an independently replayed
portfolio refusal. It does not prove intrinsic hardness, solve unrestricted
SAT, or resolve P versus NP.

```text
P_VS_NP=OPEN
```
