# JANUS-PENROSE-002 — Cross-contour causality and independent proof gate

**Status:** experimentally verified on a real MAJ3-K4 UFR proof. Research only; original C023 remains unchanged; draft PR #574 must not merge unless the separate two-worker C023/UFR performance and proof gates pass.

## Motivation and false-friend limitation

Penrose's impossible staircase illustrates that individually plausible strict rises can form a globally contradictory cycle. Here it is **only a falsifiable workflow-consistency analogy**. A genuine reversible quantum circuit can revisit the same register, but strict *event dependency* must have a consistent precedence ordering.

The experimental gate rejects untrusted feedback where the final decision or oracle's result becomes a prerequisite for generating the solver proof it claims to validate.

## Frozen nine-stage causal graph (14 mandatory edges)

1. SOURCE: canonical SAT CNF, fixed input variable count and SHA256
2. UFR_PRODUCE: optional UFR producer runs on that source
3. UFR_CERTIFICATE: complete serialized UFR call/state trace with SHA256
4. INDEPENDENT_REPLAY: replay from SOURCE + serialized proof, no trust in cached producer answer
5. ORACLE_COMPILE: Deutsch-003 block-pebbling reversible oracle built independently from SOURCE
6. SCHEDULE_AUDIT: Penrose-001 DAG rank test for every coherent gate event
7. ORACLE_TRUTH: directly compare bounded deterministic oracle assignments to independently evaluated CNF
8. UFR_ORACLE_COVARIANCE: **only after proof replay**, verify literal-preserving mappings of completed UFR cache hits, reconstruct corresponding residual-clause oracles, and compare transported bounded assignments
9. FINAL_GATE: requires all preceding proof and oracle evidence, with no backward dependency

Only the required edges are authorized. Each stage receipt binds a JSON-canonical SHA256 of its output and the hashes of all mandatory parent receipts. This is tamper *evidence* under the code/verifier trust boundary, not authenticated multi-party cryptographic attestation. The independently reconstructed verifier replays proof, checks the exact source, rebuilds oracles/schedule and the bounded assignment checks; self-consistent forged receipts alone are not sufficient.

## Actual MAJ3-K4 verified research run

[GitHub Actions #41298547419](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41298547419) at code SHA 5b9a3ccb2c102681358689a713a265401ec5eaba.

| Measurement | Value |
| --- | --- |
| Full serialized UFR proof | 56,386,975 bytes |
| Proof SHA-256 | 90c7dda12719033cbf7f183404ee0332d35adb129175346f37a4b9d86990e04c |
| Original CNF SHA-256 | da6f88555c6f0bc6aba6ba1dacb8f3291f7a8eeebf64c369062dbd2dabee936e |
| Independent UFR SAT result | **UNSAT verified** (False) |
| UFR calls / unique states / certified ISO edges | **4,081 / 2,354 / 165** |
| UFR iso edges also sampled with actual reversible residual oracles | **8** |
| Original source CNF/oracle sampled assignments | **34** |
| Deutsch-003 circuit schedule operations | **4,161** |
| Strict intra-circuit event precedences | **4,160** |
| Cross-contour trust stages / strict edges | **9 / 14** |
| Tampered cyclic dependency | **REJECTED**, with explicit cycle witness |
| First build + validation | 42.276 s (single host, not solver-only) |
| Full additional disk-read proof+oracle verification | 16.196 s |
| Small adversarial unit controls | 8/8 PASS |
| Penrose-001 previous integrity controls | 7/7 PASS |
| Independent strict C023 serialized verifier smoke test | PASS |

The offending dependency added in the negative control is FINAL_GATE → UFR_PRODUCE. This makes a closed strict precedence path through the UFR certificate and independent replay into the final gate, and **fails by design**.

The **UFR independent replay checks all 165 isomorphic cache edges**; eight were additionally sampled against the separately compiled reversible oracle. Those eight finite samples do not constitute exhaustive quantum simulation or UNSAT proof. UNSAT is established by the independent serialized UFR replay, not by the 34 source-oracle samples.

## Default size and persistence limits

Default UFR certificate decoder bound stays **25 MB**. The pinned MAJ3-K4 experiment alone opts in to a bounded **200 MB** input (the actual proof ~56 MB); this is not a production change. Production C023 is unchanged. The GitHub Actions archive contains full source-bound JSON receipts and full portable UFR certificate; its GitHub Actions artifact retention is **30 days**. The scientific result, source SHA and proof SHA remain permanently committed in:

experiments/PENROSE_002_CROSS_CONTOUR_EVIDENCE_20261101.json

## Repeatable commands

Run the small tamper and DAG controls:

    python -m unittest discover -s tests -p 'test_penrose_002.py' -v

Run the large real proof verification (time/memory bounded by the trusted experiment):

    python experiments/direct/janus_penrose_002_benchmark.py --fixture MAJ3_K4 --samples 32 --max-iso-edges 8 --out evidence/penrose-002-MAJ3.json --proof evidence/penrose-002-MAJ3-UFR-certificate.json

The benchmark saves both files, **reads them again from disk**, independently revalidates the source/proof/DAG/oracle and intentionally injects a contradictory dependency to ensure rejection. CI runs this as a separate job from the small adversarial tests.

## Scientific and security boundaries

- The replay runs on GitHub Actions in the same repository's permission boundary; this is not a blinded external laboratory or independent operator.
- All nine fixed stage labels and their mandatory parent edges are checked. No implicit "oracle confirms proof" assumption is allowed.
- A valid event graph does not imply a fault-tolerant physically implementable quantum device.
- Quantum statevector simulation remains capped at n<=8. MAJ3-K4 n=18 was **not** run on a quantum device or 2^18-state simulator.
- Reused quantum scratch registers are legal because **events**, not physical register names, are the vertices of the precedence graph.
- No end-to-end speedup was measured. Historical two-runner C023/UFR timing and memory promotion remained NOT_READY.
- Research-only: do not merge PR #574 or replace C023 based on this result.
