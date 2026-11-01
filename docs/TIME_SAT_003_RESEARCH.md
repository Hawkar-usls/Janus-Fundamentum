# JANUS TIME-SAT-003A/B/C — scientific report · 2026-11-01

Research-only experiment in draft PR #574. Production C023 and main untouched. No retrocausal physical inference or P=NP theorem.

## 003A: direct binary resolution
From (a OR b) AND (a OR NOT b), derive a by standard Boolean resolution, no separate speculative failed-literal search. Source-original two-clause witnesses are preserved and replayed. Repeated literals, tautological clauses and contradictory pairs are handled conservatively; original clauses are never deleted. Every added redundant unit is separately challenged against original CNF by CaDiCaL under the opposite assumption. All costs included in full time. This inference already falls within modern CDCL technology, not a novel breakthrough.

## 003B: forecast and stop
Before any expensive operation, estimate abstract work units using only CNF source features. Fixed rule:
estimated net = 16*(sum occurrences of unit-target variables) - 2*(total literal count) - 4*(number original clauses)*(number derived units) - 8*(number derived units).
Admit only if n>=64, clauses>=128, at least one resolution witness and positive predicted net; otherwise solve original source CNF. This is a frozen **uncalibrated proxy**, not a validated wall-time predictor. Full timing charges scanning even when all operations are skipped. Same solver, formula and options in all four arms: raw CDCL, direct resolutions, forecast-gated resolutions, and previous TIME-SAT-002 adaptive.

## 003C: fresh synthetic controls, independent proof replay and RSS
Original public development set: 60 frozen Exact-One/SAT + five larger research cases + three mechanism controls; seven additional **new public synthetic** n64/128/220/240 SAT and n128/220/240 UNSAT examples. Generator seed 20261101003, frozen input manifest SHA256 5c65a017c8dd732029030dbee64bd66a98ca9c98e9a29df1a58027733cca90aa.

Strong baselines CaDiCaL195 and Glucose4 from pinned python-sat 1.9.dev17. Every SAT model checked against original Boolean constraints. Three generated UNSAT instances produced full Glucose4 DRUP on **original unaugmented CNF**. Separate independent checker implementing unit propagation — no solver API in proof checker — replayed each addition to empty clause. Full source CNF + complete proof lines and process-isolated peak RSS measurements are in both CI JSON artifacts. Checker is maintained under same GitHub administration, therefore not independent third-party trust.

Two successful GitHub cloud workers: [CI #41315201470](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41315201470), tested PR head 9fec44ab9b5a876ef9a8b9b85d1bf0fbd42596c3. GitHub's GITHUB_SHA cac6ae986274ebe912bc70b0c594147fa29b7caa is pull-request merge test ref, not branch head. Ubuntu22 and Ubuntu24 each: 8/8 new test groups, 7/7 prior TIME-SAT-002 controls, original C023 serialized proof verifier PASS. All four SAT study arms agree on every instance.

Median ratio of whole-pipeline time to same raw CDCL on seven NEW controls (higher = slower):

| Runner | Solver | Direct | Forecast |
|---|---|---:|---:|
| Ubuntu 22.04 | CaDiCaL195 | 1.30x | 1.11x |
| Ubuntu 22.04 | Glucose4 | 1.30x | 1.12x |
| Ubuntu 24.04 | CaDiCaL195 | 1.31x | 1.12x |
| Ubuntu 24.04 | Glucose4 | 1.32x | 1.14x |

ALL 7/7 new cases slower than raw CDCL in both methods, on both machines and engines. Direct resolution derived sound redundant units in four new cases; forecast admitted no new operation. A skip-only gate incurs overhead and does not qualify as an accelerated solver.

On original known 60: direct yielded units in 22 cases, but full median 1.05–1.10x CaDiCaL and 1.16–1.19x Glucose. Forecast (0 admitted) 1.09–1.13x CaDiCaL and 1.21–1.27x Glucose. Few noisy repetitions and known public cases are **not evidence of population-level speed performance**.

New synthetic UNSAT proof replay:
- n128: eight DRUP lines, SHA256 2b503f4a2dddc95baed1a96fa31b2fc1a36206dd97ca56a892aefaef3e184a8c, PASS.
- n220: eight DRUP lines, SHA256 5e6713aa0b9026ef0947a165ddb7e387679202e82de2097a6dd3551b6c69359f, PASS.
- n240: twelve DRUP lines, SHA256 a9195bcaaa5eb8c4c407397a5d0a162c093416bb2396210159869d2dd865bca2, PASS.

These are intentionally simple four-variable blocking UNSAT cores embedded into larger formulas, NOT hard SAT Competition instances. Proof hashes bind original clauses and DRUP lines. Tests reject malformed, forged or nonterminating proof streams. Proof verification resource limit is fail-closed (NOT_VERIFIED), not a false UNSAT conclusion.

For each new case and arm an isolated Python process measured ru_maxrss, including interpreter and native solver libraries. Both child processing and process-startup latencies are recorded. This measures per-process peak memory, not pure solver RSS.

## Evidence and gates

Source: experiments/direct/janus_time_sat_003.py ; independent proof replay: experiments/direct/janus_time_sat_003_drup_witness.py ; workload: experiments/direct/janus_time_sat_003_benchmark.py ; process-isolated runner: experiments/direct/janus_time_sat_003_worker.py ; tests: tests/test_time_sat_003.py ; workflow: .github/workflows/validate-time-sat-003.yml.

Permanent combined verification: experiments/TIME_SAT_003_ABC_EVIDENCE_20261101.json.

Full per-case evidence and replayable proof CNF+DRUP in [Ubuntu22 artifact](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41315201470/artifacts/13087185767) and [Ubuntu24 artifact](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41315201470/artifacts/13087505475), 30-day retention.

**Scientific decision:** direct-unit correctness PASS, profit forecasting safety PASS but economic prediction NOT established, DRUP replay PASS on 3 synthetic cores, performance FAIL. The original proposal's truly external sealed complex CNF challenge and third-party-maintained Witness are **NOT DONE**. Both PRs stay DRAFT; production C023 unchanged. No P=NP claim, no physical reverse-time communication.
