# JANUS I0 × Fundamentum Exact-One: private/public proof-coverage bridge

**Date:** 2026-10-28. **Scope:** research-only, read-only, no mining network. **Universal P vs NP:** OPEN.

## Source identification (pinned)

- Private JANUS I0: `Hawkar-usls/janus-io`, `e23c4f25862d80a156de1410f66438119611612b`, private operational evidence is **not copied**, fetched or uploaded.
- The URL supplied as `Hawkar-usls/janus-io-publicf` returned HTTP 404. The accessible published counterpart is `Hawkar-usls/janus-io-public`, pinned `41b1c9b6af6629a551d2814aa69c5dfcac042620`. This fallback is explicitly marked, not assumed to prove the missing repository exists.
- Both previously inspected source trees contain an identical offline analysis file `scripts/butterfly_director.py`, Git blob SHA-1 `697ef1b46d6253f034e3c7b33783836e99c96052`; documented `docs/structured-traversal-and-random-control.md` blob `5d4cc973e68f26a956e6de5be402621edc177be7`.
- Public status `PROJECT_STATUS.json`: hardware energy savings and cryptographic attack advantages are NOT established. The public A18.42 Native Flow Gate result is restricted to tested admission-wave segmentation.

## Mathematical and measurement integration

The implementation `research/exactone_i0_paired_control_audit.py` creates a frozen set of deterministic signed Exact-One SAT/UNSAT cases, including difficult-for-one-operator high-width and disjoint high-global-nullity instances. Every case is evaluated by **all three** existing proof-carrying operators: bounded primal width 2; bounded affine nullity 4; and component factorization with local affine nullity 3. Each receives the same original clause set. Each SAT/UNSAT status requires the independent original mathematical certificate verifier. Small inputs (<=8 variables) are also compared against an independent full truth-table oracle (test only, never solver).

The audit records statuses per solver, original case hashes, input exposure, sizes and verified provenance. It explicitly **does not measure CPU wall time, hashes checked, memory, energy or matched computational budgets**; therefore it cannot report a solver speedup or fair matched work-cost advantage. Structured portfolio coverage is expected to be at least equal to its individual methods by construction, not a statistical discovery. No PoW nonce/tail performance metric can be transferred to a SAT complexity claim.

We transfer the I0 methodology, not its mining code: pre-declared input cases, matched exposure, randomized fixed seed for diverse fixtures, preserving all OPEN and UNSAT failures, bounded proof authority, and a conservative publication gate.

## Genuine cross-repository execution

The new offline GitHub workflow checks out public I0 at exact SHA and executes its **actual** `scripts/butterfly_director.py --self-test`, verifying its Git object identity and published status/limitations. The private version is referenced by a separately connector-verified identical blob SHA, but cannot be checked out with a default public GitHub Actions token and should never be substituted for raw private evidence. It also executes the exact JANUS Lapis converter (annotation-only IR), AIFC strict canonicalizer, and the new proof-coverage audit; original SAT/UNSAT evidence remains exclusively controlled by Fundamentum.

Security: no remote Stratum/pool, no network mining, no raw proof archives, no wallet labels, no NAS or ESP32 intervention; no main branch modification, no new provider jobs or credits.

## Research boundary

The benchmark can distinguish which known *restricted* operators recognize specific inputs and where OPEN remains. It does not provide polynomial compact relations for arbitrary irreducible high-primal-width/high-affine-nullity Exact-One instances. No SHA-256 break and no P=NP proof.
