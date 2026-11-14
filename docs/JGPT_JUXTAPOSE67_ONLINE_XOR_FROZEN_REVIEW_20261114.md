# JGPT teacher × JANUS JUXTAPOSE 67 — prospective internal neural learning

**Research-only, not deployed.** Stacked on exploratory PR #643, which itself is stacked on #642. C023, production services, existing Rowan experiments, SAT external evidence and frozen negative R6 remain untouched.

## What is reused from user's own transformer

User's existing MIT-licensed JGPT_CODEX(2).py ByteTransformer inspired the model architecture: PyTorch TransformerEncoderLayer, multi-head attention, residual normalization, GELU, AdamW training, gradient clipping, bounded prequential EMA and checkpoint export.

**No original JGPT weights are imported** — they are byte/text-language-model parameters, not SAT pivot-source numeric features. JGPTSatPivotRanker is newly initialized with one TransformerEncoder layer, four attention heads, 32 hidden units, 12 source-only structural features per pivot and one binary score head. This is a real weight-trained attention encoder, not a byte-level autoregressive pretrained GPT. Be precise: **JGPT-inspired**, fresh SAT weights.

Input excludes current exact labels, numeric pivot IDs, hidden planted model, formula-family tag and future holdout feedback. Model scores before exact resolution and updates only afterward, from verified source-bound proof receipts. It only orders suggestions; exact JANUS proof replay remains the sole mathematical authority.

## Training protocol

Two independently seeded deterministic synthetic trials: 20261114 and 20261117 (fixed before any trial results). Each has 67 distinct original-source-sha SAT CNFs. Every source SAT model is validated against all original clauses.

For each trial:
- Cycles 1–45: prospective online learning. Score nine candidate pivots, then run independently proof-replayed exact candidate probes, train a compact attention model with two bounded AdamW steps per episode, clip gradients and reject nonfinite values, update calibration temperature based only on earlier training-source predictions and labels.
- Cycles 46–67: **frozen holdout**: do not update model weights, probability temperature or search-governance statistics; use exact labels for evaluation only.
- Export exact source SHAs, train-only model tensors and state SHA-256, calibration history, all positive/null outcomes and compute counts.
- Compare JGPT learned model + JUXTAPOSE to old heuristic-JUXTAPOSE, static numeric pivot search and seeded random search. All arms use the same exact proof engine and inputs; COLD/WARM/HOT modes depend only on earlier training fingerprint counts.

## Metrics and falsification

Report exact source-bound XOR rank-positive cases relative to UP+full XOR sign-mask baseline, exact pivot probes, symbolic clause pair work, prospective held-out Brier/ECE, and training/inference wall overhead. No result may be hidden or renamed because negative.

**No SAT end-to-end solver-time benchmark occurs in this trial.** Better pivot ordering is not necessarily an end-to-end solver speedup. Genuine advantage requires paired heldout cost including inference and training overhead, independent new source families and a later properly blinded external custodian.

The source test is 100% synthetic and same-admin; no external independent laboratory proof, new mathematical theorem, universal acceleration or P=NP claim follows.

## Safety

Never treat a model prediction as a SAT proof. No automatic production weight promotion, PR merge, new network service, NAS activity, credit spending, mutation submit, or autonomous research approval. The official R6_FROZEN_SCIENCE_GATE_NOT_PASSED and C023 gates stay closed.
