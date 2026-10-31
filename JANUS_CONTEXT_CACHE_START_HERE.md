# JANUS — START HERE AFTER ANY CONTEXT / STREAM LOSS

This file is the canonical recovery entrypoint for the active JANUS scientific branch.

## Mandatory read order

1. Read `docs/JANUS_CONTEXT_CACHE_CURRENT.md`.
2. Read `registry/JANUS_CONTEXT_CACHE_CURRENT.json` for the machine-readable source HEAD, artifact hashes, transport state, recent commits, and evidence pointers.
3. Fetch the `must_read_artifacts` listed in the JSON before changing any scientific status.
4. Check the current GitHub branch/PR HEAD against `source_head`. If GitHub is newer, regenerate with:

```bash
python tools/janus_context_cache.py
```

5. Run anti-duplication/source checks before creating a new theorem, experiment, or PA/NM promotion.

## What this replaces

Do **not** try to reconstruct the active scientific state primarily from chat history after a stream/cache interruption. Chat history may be truncated, stale, or unavailable.

Use the repository cache as the first recovery surface and then verify against the live Git tree/CI.

## Scope boundary

The cache contains explicit reproducible project/scientific state: Git SHAs, frontier, proof/checker status declarations, file hashes, transport/bootstrap state, recent commits, and next scientific routing.

It does not and cannot contain private model chain-of-thought, hidden runtime cache, credentials, or secrets.

## Scientific firewall

Until a full arbitrary-input theorem and implementation satisfy the E8-D1 contract:

```text
P_VS_NP = OPEN
E8_D1 = EMPTY
UNIVERSAL_SELECTOR = OPEN

finite success != universal proof
existence != polynomial construction
verification != polynomial certificate discovery

T_construct + T_solve + T_reconstruct + T_verify <= poly(|F|)
```

## Current top-level goal

```text
UNIVERSAL_DETERMINISTIC_POLYNOMIAL_3SAT_SOLVER
```

The cache is a continuity instrument. It does not promote mathematical claims by itself; theorem promotion remains governed by JANUS source audit, checker, ledger, and CI.
