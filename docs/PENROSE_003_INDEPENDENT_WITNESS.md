# JANUS-PENROSE-003 — Independent cloud-runner proof witness

**Status:** research-only, untrusted producer artifact + distinct clean **Ubuntu 22.04 and Ubuntu 24.04** witness jobs. This is runner/process isolation, **NOT an independently governed external laboratory or separate trusted source-code authority**. No secret tokens or private sources are required. Main C023 remains unchanged, and UFR PR #574 remains DRAFT.

## Purpose

Penrose-002 verified a complete source-bound UFR→reversible oracle→independent replay chain, but both producer and verifier executed in **one GitHub job**. Penrose-003 crosses an actual job boundary by uploading a proof artifact and downloading it on **two distinct fresh GitHub-hosted runners**. A different OS runner cannot access the producer's memory, but both run trusted-source code from the same GitHub repository SHA. This is stronger operational isolation, not independent validation of the software implementation.

## Trust and dependency contract

Producer:
- Compiles canonical MAJ3-K4 formula, generates UFR portable certificate (~56 MB), replays it, builds Deutsch-003 oracle, checks Penrose-002 9-stage/14-edge DAG, and uploads: report JSON, UFR portable certificate, and untrusted SHA256 handoff manifest.
- The manifest includes GitHub workflow run ID and head SHA, original CNF hash, certificate digest, exact byte lengths, report digest and graph dimensions. Manifest is **not a signature**. Producer uploads read-only artifact (retention 30 days), not changes to main.

Witness (each on another GitHub runner):
- Checks downloaded files against the event SHA/run ID from the **separate GitHub Actions runtime**, not from the producer's manifest.
- Rebuilds MAJ3-K4 from a source fixture checked out by the witness; compares original CNF SHA and all strict graph dependencies to a locally pinned model.
- Replays the entire serialized UFR certificate with bounded opt-in 200 MB research cap (25 MB default otherwise), independent of the producer's cached result.
- Recompiles the Deutsch oracle and circuit schedule, independently checks sampled source formula truth, verifies UFR literal bijections and sampled residual formula covariance, and recalculates all dependency receipts.
- Requires replayed UNSAT, preserved **165 completed ISO hits / 2354 UFR states**, at least eight checked UFR→oracle mappings, and 4161 reversible gate events.
- Executes **10 malicious transfer mutations** and requires explicit rejection of all of them: corrupted proof/report, stale workflow run, wrong checked-out code SHA, wrong CNF SHA, truncated proof, crossed proof hash, self-consistent forged oracle verdict with *recomputed* stage receipts/transport hashes, injected future feedback cycle, and a crossed formula.
- Uploads separate machine-readable witness evidence for each Ubuntu worker. A workflow with both witnesses PASS is positive evidence of successful runner isolation; never claim a single job's success as cross-runner PASS.

## Core protections

1. experiments/direct/janus_penrose_003_transfer.py: producer's untrusted manifest, strict byte bounds and code/run provenance gate.
2. experiments/direct/janus_penrose_003_witness.py: replay and ten deliberately corrupted transfers on a separate runner, full evidence JSON.
3. tests/test_penrose_003.py: small hostile handoff cases to prevent accidentally trusting SHA-only self-attestation.
4. .github/workflows/validate-penrose-003.yml: isolated producer, two independent consumer workers, archived producer and witness files, no write permissions, bounded time.
5. The existing Penrose-002 and Deutsch-003 source code must not be replaced; production C023 remains unchanged.

## Scientific boundaries

- All witnesses share GitHub's infrastructure and a repository source SHA. To reach true independent **trust domain** isolation, a separately maintained verifier should execute under a different administrator/account/service, pinned to audited code and immutable hash.
- These tests are not physical quantum-computer experiments. No SAT speedup, quantum advantage, P=NP statement, or C023 promotion is authorized.
- A UFR proof verifies UNSAT; the sampled reversible oracle alone does not.
- A consistent hash graph alone is not trustworthy; the witness must **independently replay** semantic evidence even when attacker recomputes hashes.
- Do not permit the final reviewer gate to create upstream producer dependencies. Legitimate reversible register reuse remains allowed in Deutsch-003, because strict DAG edges are between operation events, not registers.
- The earlier UFR vs C023 two-runner timing/RSS gate is a **separate and still binding** promotion criterion.
