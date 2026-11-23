# JANUS-TACHYON-001 — The Future Echo as a speculative, falsifiable search hint

**Status:** bounded research-only code. Not a tachyon, retrocausality, quantum speedup, polynomial SAT, P=NP, or a production solver replacement. C023 and the independent certificate gate remain unchanged; PR #574 is DRAFT.

## Physical reference, without claiming time travel

- R. P. Feynman, "The Theory of Positrons", *Physical Review* 76, 749 (1949), DOI: 10.1103/PhysRev.76.749. The Feynman–Stueckelberg *mathematical interpretation* describes antiparticles using backwards-directed components of a field calculation; experimentally, positrons are ordinary future-directed antiparticles. This does not transmit messages to the past.
- Cloud chambers visualize droplets condensing along charged-particle ionization paths under illumination. The track alone under a flashlight does not unambiguously identify a positron. Carl Anderson's 1932 positron identification required the direction/curvature and energy loss in a magnetic field with a lead absorber.
- Robert Holte et al., "Bidirectional Search That Is Guaranteed to Meet in the Middle", AAAI 2016, DOI: 10.1609/aaai.v30i1.10436. Bidirectional and goal-oriented searching are established algorithms, not temporal messaging.

## Exact computer-science analogy

The "future" is a **hypothesized terminal state**, built only from the present formula. The "past" is the original canonical SAT or Exact-One constraint set. The "track" is a reproducible trace of decisions, propagated domains, or a candidate satisfying assignment. No information arrives from physical future time.

Algorithm:
1. Read bounded SAT/Exact-One rows (n <= 10, each constraint <= 8 distinct variables); preserve repeated literal multiplicity in Exact-One.
2. Generate a candidate "future echo" by deterministically weighing signed input literals. This is a fallible heuristic, not a discovered SAT solution.
3. Test the entire hypothesized assignment against every clause; if it passes, it is a valid candidate and is independently verified.
4. If it fails, propagate *sound local support constraints*, then explore both values for each remaining branch. Use the echo only to prefer which branch to try first. The opposite branch is never deleted, even when it contradicts the echo.
5. An UNSAT result requires complete branch exploration and an independent exhaustive truth-table check for the bounded research n. At larger scale C023 remains the authoritative proof producer/replayer.
6. Penalize *all* work, including formula normalization, echo synthesis, hypothesis validation, propagation, recursion and independent SAT or UNSAT checking.
7. Validate against **independent UFR Boolean semantics** and invert the hints as negative control.

The "annihilation of the tachyon" metaphor corresponds to **rejecting an invalid predicted model**, not proof of impossibility. A correct predicted model can be accepted only after ordinary direct Boolean verification.

## Connection to PENROSE-003

PENROSE-003 forbids a true strict edge FINAL_GATE -> UFR_PRODUCE because it would create a circular trust dependency. TACHYON-001 therefore uses a **speculative, sandboxed prediction** that cannot alter certified UFR evidence or turn a guessed answer into a verified one. There is no violation of causal DAG scheduling: all calculations still execute forward in time.

For Deutsch reversible computation, inverse U^(-1) is the computational inverse of a gate circuit, not a physical return to the past; this research doesn't invoke quantum hardware.

## Validation and measurable success

- tests/test_tachyon_001.py: randomized SAT and Exact-One formulas; false future hints; complement inversion; local support soundness; empty clauses; duplicate and complementary literals; bounded input validation.
- experiments/direct/janus_tachyon_001_benchmark.py: the same six tiny formulas in three controlled configurations, using five sequential timings per case. Source SHA and independent UFR truth labels are recorded in machine-readable JSON.
- .github/workflows/validate-tachyon-001.yml: standalone falsification and unchanged C023 serialized verifier CI.
- All measurements are microbenchmarks: no statistical claims from tiny differences. Count search tree nodes as well as wall time. A zero-node speculative candidate is just an already-correct guess and its construction/verification cost is included.
- Do not compare a n<=10 prototype to MAJ3-K4 (n=18) without an adapted full-source test and pre-registered cross-runner benchmark.

### Success gate

A valid research PASS means no wrong SAT/UNSAT answers under all bounded tests, false echo cannot prune valid solutions, and independent certificate-verification regressions are absent. A production improvement requires independently measured end-to-end wins on the *same instances* against C023, proof and RSS gates, robust hostile hints, and two clean runners. Until then the experiment remains separate, with no merge or autotuning.


## 2026-11-01 retrospective Meta Registry audit and confound correction

The whole current Meta Registry checkout was scanned by a read-only GitHub Actions worker, yielding **190 direct-term JSON and one JSONL**, plus 256 further retrocausality-only context files among 6,397 JSON and three JSONL. This is a **complete current-tree** search, NOT a search of all historical Git revisions. A complete verified path index and sources are proposed through [Meta Registry draft PR #432](https://github.com/Hawkar-usls/janus-meta-registry/pull/432); the full scan with per-file SHA256 is in [GitHub Actions #41305794643](https://github.com/Hawkar-usls/janus-meta-registry/actions/runs/41305794643).

Previous JANUS evidence materially narrows admissible claims:

- `data/Retro-Tahyon.json` and `registry/uap/Retro-Tahyon.json`: the archive establishes research provenance, **NOT a detected physical tachyon or demonstrated time-reversed communication**.
- `EYE/r4_7_rt_1/retro_tahyon_prospective_outcome_contract.json`: preregister outcomes, retain invalid trials, block unsupported prior probabilities and claims based on post-hoc reclassification. Its validation receipt is a **deterministic routing** result, not physical evidence.
- `data/JANUS-TAHYON-TRAVELER-DISTRIBUTED-TIME-ARRIVAL-ORDER-INVERSION-v1.0.json`: timestamp/arrival inversion in a distributed workflow is not a physical time-travel observation.
- `data/Janus_Tachyon_Star_T1_Lookback_Result.json`: negative/incomplete replication; `data/Janus_Tachyon_Star_T2_External_Prepointed_Replication_Result.json`: qualified external trials produced zero isolated B candidates, with unresolved trials preserved.
- `data/JANUS-CAUSAL-DIFFERENCE-TEST-RUN-2026-09-01-v1.0.json`: the first clean preregistered external-future-randomness difference trial was **H0-compatible**, and a previous time-ordering mistake was explicitly retained.
- Physarum/reverse-search and Tranception analogies may motivate **conventional backcasting/constraint propagation**, but are not independent proof of exotic physics.

### Corrected equal-information ablation

The earlier tiny 3-SAT speed claim compared a plain forward DPLL against a retrograde algorithm permitted to test a complete heuristic model before any search. To isolate the effect, `search(..., strategy="candidate_first")` now **builds and verifies exactly the same input-derived model**, but retains conventional forward branch order. Both full costs are timed.

- Six original controls, last measured same 6-variable SAT: forward 1,191 μs, candidate_first **93 μs**, retrograde **87 μs**; both latter versions visit zero recursive nodes, because they verify the same already-correct input-derived assignment. The apparent ~14× improvement over forward is predominantly ordinary **candidate-first verification**.
- A frozen **60-case seeded SAT/Exact-One** suite (seed `20261101`, SHA256 `865af20c649740dc7847a7204d9cd0c36470ddb66777c4e92c26bde33c58c53b`) compared all three variants on identical inputs, verified every answer independently with `janus_ufr_001.verify_model` over all 2^n assignments, and ran three repetitions each. Retrograde was faster than equal-hint candidate_first in **48/60** tiny measurements and slower in **12/60**; the echo already proposed a correct model in **21/60** cases. This provides **no basis for claiming a general or stable advantage** without uncertainty intervals, nontrivial holdouts, and stronger solvers.
- Corrected CI: [Fundamentum #41306179442](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41306179442), all seven tests and C023 certificate-verifier PASS. Permanent evidence: `experiments/TACHYON_001_FAIR_REAUDIT_20261101.json`.
- The finite prototype still does a **full exhaustive UNSAT truth scan at n<=10** to verify its own negative result. That is an intentionally safe research bound and does not scale to MAJ3-K4 n=18 as a production certification algorithm.
- The two Boolean-domain modes of local support propagation are logically equivalent in the current implementation. **No novel GAC advantage is claimed.**

Research direction: preregistered and **externally hidden** larger SAT/Exact-One benchmarks against equal-hint, classic CDCL and C023, with wall-clock, nodes, peak RSS, proof replay and independent two-worker checks. Physical tachyons remain outside the algorithm's mechanism and cannot be inferred from it.

