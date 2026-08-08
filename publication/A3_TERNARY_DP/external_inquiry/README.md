# A3 Ternary-DP External Inquiry Handoff

This directory is an external-review handoff for the frozen A3 publication object. It is not a new mathematical authority surface and it does not promote novelty status.

## Immutable target

- Publication target head: `811d954e52296893898062d9abea7aaf572629be`
- Frozen theorem evidence head: `5ee79fc82613f24e621595afa0119312a2f52660`
- Strengthened theorem proof head: `0e505f460ec63cbb358c7f66cde18ab8a52684d3`
- Endpoint-compression proof head: `6ca16581eff08103698250b09ea51aeccd9f800b`
- Admission receipt: `research_targets/audits/A3_KCLASS_ENDPOINT_DP_V1_1_ADMISSION_0E505F46.json`
- Deterministic publication PDF SHA-256: `a3a6e87376d38e9336d9e101640ebfaf5f41499a885f0477e2f46b88cf3cd5e4`
- Frozen publication artifact ID: `9025859191`
- Frozen publication artifact ZIP SHA-256: `4eaa8f7ff4400d0751391f7354cf90452f50e25f80b19efb770db3614b4231d6`

## The claim being reviewed

For finite-field subspace arrangements with `k` distinct geometric subspace classes and arbitrary positive multiplicities, endpoint compression yields an exact bottleneck dynamic program. If `s` classes are singleton and `r` are repeated (`s+r=k`), the compressed state graph has

- exact state count `2^s*3^r`,
- exact transition count `s*2^(s-1)*3^r + 2r*2^s*3^(r-1)`, and
- `O(k*3^k)` combinatorial DP work after `2^k` subset-rank preprocessing.

The connectivity value used by the DP is

`lambda(P,S)=rho(S)+rho(K\P)-rho(K)`.

The claim is restricted to the stated repeated-geometric-class domain. It does not change unrestricted matroid path-width complexity, does not overturn known general NP-hardness, and makes no P-vs-NP conclusion.

## What an external reviewer is asked to do

1. Reproduce the frozen publication PDF and, independently if desired, the DP controls described in `reproducibility.md` and `verification_protocol.tex`.
2. Check the endpoint-compression and ternary-DP proofs against the frozen admission receipt rather than treating the paper as an authority source.
3. Search for prior work that explicitly contains, implies, or subsumes the same combination of arbitrary multiplicities, first/last endpoint compression, the `2^s*3^r` state graph, and the `O(k*3^k)` bottleneck DP parameterized by the number of distinct geometric classes.
4. Report any predecessor, near-predecessor, counterexample, hidden assumption, terminology mismatch, or missing citation.

## Current ceiling

- Internal mathematical evidence: `ES5_GENERAL_ALGORITHMIC_THEOREM_ADMITTED`
- Base novelty: `N3_NOVELTY_CANDIDATE`
- Search strength: `N3_EXHAUSTIVELY_SEARCHED_WITHIN_DECLARED_PROTOCOL`
- External independent replication: `NOT_ESTABLISHED`
- Historical world priority: `NOT_CLAIMED`
- World novelty N4: `NOT_ESTABLISHED`
- P vs NP: `OPEN`

An external inquiry that finds no predecessor is evidence for the search record, not proof of universal literature absence. A novelty promotion requires a separately defined and independently evidenced gate.
