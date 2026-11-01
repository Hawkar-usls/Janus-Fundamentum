# JANUS TIME-SAT-004D4 · Partial XOR recognition in mixed CNF

Status: **RESEARCH PROTOTYPE / NOT A BENCHMARK / NOT PRODUCTION**.

Parent source: 004D3B draft #586, itself based on 004D3 #585.
The 004D3B results are case-dependent and do not establish an algorithmic
speed advantage. This proposal has no claim of further speedup, hidden holdout,
new outside-admin witness, universal SAT solver, or P=NP.

## Correct representation-preserving transformation

For each distinct-variable support S of length k <= 6, inspect the sign
masks in the ORIGINAL CNF. A parity class is extractable only if all
2^(k-1) distinct masks occur. Select exactly one original clause for each
mask; their conjunction is exactly the parity equation XOR(S) = 1 ^ p,
where p is the parity of the falsifying assignment's sign mask.

- Select each source clause at most once. Keep every unselected original clause
  verbatim in the residual CNF, including incomplete blocks, duplicates,
  other parity class masks, tautologies, empty clauses and width >6.
- Keep source index partition and SHA256 of the logical source. Do not infer
  structure from family names or use the catalog answer.
- Every model must satisfy EVERY original CNF clause.
- SAT can be labelled original-model verified only after full replay.
- UNSAT from native CryptoMiniSat alone is SOLVER_ONLY_NO_PORTABLE_CERTIFICATE.
  No external DRUP/LRAT witness; do not count as independently certified.
- Validation fails closed on malformed literals or configured budget limits.
  Incomplete groups are not silently converted to equations.
- Mixed solving sends extracted equations to native CryptoMiniSat XOR and
  untouched residual clauses to its ordinary CNF interface. This is classical
  mixed XOR+SAT solving, not a new P=NP algorithm.

## Immediate tests and limits

The accompanying test suite exhaustively compares original CNF truth with
the transformed XOR+residual conjunction on all assignments of numerous
adversarial and deterministic-random small examples. It additionally checks
original-clause SAT-model replay and clearly labelled solver-only UNSAT.
Two read-only GitHub Actions runners are requested; no Rowan costs, NAS/PC
load, auto-merge, or alteration of C023.

These are **synthetic correctness tests**. They are not evidence of net
performance improvement or external-family transfer.

## Next acceptance gate (not executed by this prototype)

Freeze a new external-origin mixed-family public cohort before examining
source structure. Use unchanged original SHA-pinned CNFs, bounded full-process
benchmarks, and matched unmodified-source and native-XOR baselines. Admit
net performance gains only with paired intervals, bad-tail analysis and
solver-native preprocessing controls. Any UNSAT advance still requires
portable independent checking. Keep all negative outcomes append-only.

004D: PARTIAL; 004C: OPEN; 004F: NOT READY; production C023: UNCHANGED.
