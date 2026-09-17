# TRUMP Observer-Effect / Information-Leakage Diagnostic v1

Status: PREREGISTERED DRAFT — DIAGNOSTIC ONLY — NO SOLVER/CARRIER AUTHORITY

This entry records a classical experimental-design analogue of the observer-effect intuition: a discovery result is contaminated for blind-authority purposes if target-aware provenance leaks into candidate execution, or if observer/telemetry instrumentation can perturb the exact state consumed by discovery.

## Context recovery / anti-rediscovery finding

The v3.22 Stage C authority already established a strong blind-execution lineage for `EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT`. Its authority audit includes P3 blindness and P11 renaming/order/tuple-permutation invariance. Therefore those ideas are **not** a new mechanism here and must not be re-promoted.

The actual successor diagnostic surface is narrower:

`OBSERVER_TELEMETRY_NONINTERFERENCE + TARGET_METADATA_CANARY + DELAYED_REVEAL_FREEZE`

The question is not whether the existing candidate is invariant under another renaming test. The question is whether attaching an observer can alter candidate-visible bytes or expose information that the candidate was not licensed to see.

## v3.23 ceiling

The currently recovered connected-mixed corpus is exhausted for post-orbit obstruction localization. Any execution here is calibration only and cannot be called new source evidence. No new connected-mixed mechanism is licensed until genuinely new source-bound raw provenance appears and is frozen under the then-current authority.

## Calibration protocol

1. Build and hash immutable blind payload bytes.
2. Keep a target-aware canary only in a separate metadata envelope.
3. Run `NO_OBSERVER`, `READ_ONLY_OBSERVER`, and `HOSTILE_COPY_OBSERVER` from independent decodes of the same payload.
4. The hostile observer deliberately mutates its private copy.
5. Discovery receives a fresh decode of the original committed bytes, never the observer object.
6. Require identical candidate-input SHA and candidate output across observer modes.
7. Retest semantics-preserving representation coherence only as an existing-P11 regression.
8. Freeze candidate hashes before revealing provenance/labels.
9. Reveal metadata after freeze and require the freeze hash to remain unchanged.
10. Run an intentionally unsafe shared-mutable-object negative control and require the harness to detect contamination.

A calibration PASS means only that this orchestration harness resisted the tested leakage/perturbation paths. It does not establish universality, general connected-mixed tractability, general SAT in P, or a P-vs-NP result.
