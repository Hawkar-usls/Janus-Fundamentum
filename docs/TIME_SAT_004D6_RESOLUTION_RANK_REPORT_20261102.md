# JANUS TIME-SAT-004D6 / 004D6R · Bounded resolution and rank falsification

**RESEARCH ONLY — NO PERFORMANCE OR PRODUCTION CLAIM.**

Parent: draft PR #591. Four original SHA-pinned, previously tested PUBLIC SAT Competition 2026 CNFs, NOT hidden holdout. Frozen preregistered protocol Git blob 150d16f6cc90551afba81e964adc09ad0fe7c032.

## Method
At most 2 rounds, 128 eligible pivots per round, 8 source/derived parent clauses per sign, 64 pairs per pivot, 2,000 unique derived resolvents per CNF, width at most 4. All original clauses are retained verbatim. Every new clause has a proof DAG with parent IDs and pivot. A distinct same-administrator checker independently replays every resolution step against original source clauses and independently recomputes full XOR sign-mask groups. No SAT solving or independent external proof witness.

## Two-worker source-only results
Original CI 41355380127: Ubuntu 22.04 + 24.04 PASS, 8 new adversarial/exhaustive tests, 9 original 004D5 and 9 original 004D4D tests plus C023 verifier per worker.

| Source | Derived resolvents | New complete parity forms | Limit hit |
|---|---:|---:|---|
| linear-equations | 0 | 0 | No |
| xor-shifting | 2,000 | 169 | Yes |
| minimum-disagreement-parity | 60 | 0 | No |
| binary-tree-parity | 2,000 | 164 | Yes |

The 333 additional complete source-entailed XOR representations are NOT claims of 333 independent equations. The positive two formulas reached their 2,000-resolvent cap, so the search is incomplete.

Original evidence was preserved with SHA-bound original ZIP, full JSON, source SHA and rechecked proofs: archival CI 41355595936 SUCCESS; permanent summary at experiments/time_sat_004_external/time_sat_004d6_evidence/summary.json.

## Post-hoc rank diagnostic 004D6R
CI 41355778801 SUCCESS independently reconstructed all parity keys, checked the original source, and computed exact GF(2) ranks before and after including every new key:

- xor-shifting coefficient and augmented rank: 1,643 before, 1,643 after.
- binary-tree-parity coefficient and augmented rank: 857 before, 857 after.
- linear-equations and minimum-disagreement-parity: zero new keys and zero rank change.

**Total increase in GF(2) rank: ZERO.** All 333 newly recognized parity forms are linearly redundant with existing explicit XOR equations in these four source instances. Correct source derivation is demonstrated; no additional independent linear information, no measured SAT speedup and no P=NP inference.

## Next scientific gate
Do not raise resource caps only to hunt more redundant clauses on these same sources. On fresh preregistered mixed-family public instances, prioritize strictly certified new GF(2) rank relative to source XORs and measure actual feature, proof, native-XOR, solver and full-process costs against strong unmodified baselines. Public benchmarks remain development, not blinded hidden tests. Any independently administered portable UNSAT witness remains an open 004C obligation.

004D PARTIAL / 004C OPEN / 004E OPEN / 004F NOT READY. Production C023/main unchanged; no paid Rowan or persistent NAS/PC load.
