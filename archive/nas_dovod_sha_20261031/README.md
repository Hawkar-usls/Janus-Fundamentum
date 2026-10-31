# JANUS NAS · DOVOD-SHA negative-control research archive (2026-10-31)

**Source:** owner-NAS `Janus/archive/experiments/sha256_prediction/dovod_sha_v1`. Original files remain on NAS; this archive is not executable by default.

This is an important **failure-analysis and experimental-discipline example**, **not** evidence that SHA-256 is predictable, a cryptographic break, or evidence for P=NP. Preserves original experiment source (historical NAS SHA-256: `225aab8fc62cd2d2a1814f9263f5e95564ea24709c47fce0304346ca3a8282d0`) and the contemporaneous method/leakage reports, with privacy-aware textual copies. GitHub source bytes may differ due to normalization, original SHA comes from original-source manifest.

## Falsifiable limitations

- A 256-byte uniform target has baseline per-byte cross-entropy `ln(256)=5.545177...`. The claimed `loss<4.5` threshold was not statistically preregistered or justified.
- The first no-noise split has **25 of 50 test sequences identical to training sequences**, all 50 test block IDs also occur in training, and the prior target digest bytes appear in context. Memorization and context can explain promising results.
- The adaptive test changed noise, nonce modulus, and sequence length simultaneously. There was **no untouched, independent holdout**.
- Original historical runs do not persist reproducible checkpoints or exact result manifests.
- The newer `preregistered_gate_profile.json` is a **proposed V2 freeze policy**, not proof that the historical test followed it.

## Safety / scientific gates

1. Never train/run this script on the 4GB QNAP archival NAS. The historical resource estimate called for 3 inits x 5000 steps each with PyTorch/NumPy and sustained CPU/GPU, only for an explicitly chosen workstation.
2. Preserve the original report as **negative controls** for JANUS Tranception/Fundamentum experiments. Require sample-level disjointness, contamination tests, fully frozen evaluation, multiple independent seeds and result receipts before any generalization.
3. Do not infer from next-token memorization of SHA digests that any Exact-One/SAT/P=NP problem was solved. It is an independent example of experimental leakage, not a complexity-theory theorem.
4. No scientific or model performance claim is approved; no CI runs training, no new model accepted to Demiurge R2. Static parse/JSON tests only.

