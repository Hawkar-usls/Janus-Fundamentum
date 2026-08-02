# C038 — Proof-Carrying Open-Core Vault

## Purpose

C038.0 adds a verified exact cache for portfolio-scoped `OPEN` results. It does
not infer objective hardness and does not generalize an old failure to a new
formula.

The two governing invariants are:

```text
OPEN = f(formula, capability profile, budget profile, canonicalizer)
```

and

```text
reduction or similarity to an OPEN core does not prove OPEN
```

Only an exact canonical core digest under the identical capability digest may
reuse an earlier result, and even then the refusal ledger must replay.

## Placement

C038.0 is a proof-laboratory artifact layered on the C035–C037 line. It does
not modify live NAS services. A runtime adapter may be added only after the
proof artifact and its CI gate pass.

## Objects

### Immutable core

A core stores canonical bytes and content-addressed metadata. Its digest is:

```text
SHA256("JANUS-C038-CORE-V1\0" || canonical_core_bytes)
```

### Immutable evaluation

An evaluation is keyed by:

```text
(core_digest, capability_digest)
```

An old `OPEN` evaluation is never overwritten by a later `CLOSED_POLY`
evaluation. The latter receives a new row under a new capability digest.

### Capability manifest

The capability digest commits to the canonicalizer, ordered portfolio,
solver/verifier/policy digests, budgets, and protocol versions:

```text
SHA256("JANUS-C038-CAPABILITY-V1\0" || canonical_json(manifest))
```

Canonical JSON in C038.0 is deliberately restricted to null, booleans,
integers, strings, arrays and string-keyed objects. Floating-point values are
forbidden. Object keys are sorted and insignificant whitespace is removed.

## Logical staleness

`STALE_OPEN` is not stored as a mutable database status.

```text
ACTIVE iff evaluation.capability_digest == current_capability_digest
STALE  otherwise
```

Changing the current capability is one UPSERT into the singleton
`c038_current_capability` table. No historical evaluation row is updated.

## Verified exact lookup

```text
exact core digest
+ exact capability digest
+ current capability equality
+ valid core payload digest
+ valid trace payload digest
+ trace/core/capability binding
+ successful independent refusal replay
------------------------------------------------
HIT_VERIFIED_OPEN / CACHED_OPEN_EXACT
```

A missing replay verifier is fail-closed and returns `HIT_CORRUPT`, not a cache
hit. Corrupt content is retained for audit but bypassed operationally so the
ordinary portfolio can run.

## Content-addressed payloads

Heavy bytes live outside SQLite:

```text
vault/sha256/ab/cd/<digest>.<kind>
```

Files are written to a temporary sibling, flushed, fsynced, and atomically
renamed. SQLite stores only digests and references.

## C038.0 exclusions

The first version deliberately contains no:

```text
PIOC extraction
OPEN_SLICE minimization
structural fingerprints
similarity search
isomorphism cache
equivalence mapping
reduction-based OPEN promotion
```

## Acceptance gate

The executable self-test checks:

1. canonical key-order independence;
2. invalidation by solver, verifier, budget and canonicalizer changes;
3. verified exact hit;
4. stale result under another current capability;
5. corrupt payload rejection;
6. idempotent reinsertion;
7. concurrent writers producing one evaluation row;
8. logical staleness without mass evaluation updates;
9. preservation of historical OPEN after later CLOSED_POLY;
10. absence of structural matching fields.

Run:

```bash
python experiments/direct/janus_c038_open_core_vault.py --self-test
```

## Claim boundary

C038.0 proves only safe reuse of a previously replayed portfolio refusal for
the identical canonical input and identical capability profile. It does not
prove that the formula is intrinsically hard, does not solve unrestricted SAT,
and does not resolve P versus NP.

```text
P_VS_NP=OPEN
```
