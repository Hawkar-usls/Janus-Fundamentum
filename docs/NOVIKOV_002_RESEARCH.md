# JANUS-NOVIKOV-002 — partial-state consistency before complete SAT candidates

**Result (2026-11-01):** correctness PASS, bounded probing engineering PASS, general speedup **NOT ESTABLISHED**. Research only in draft PR #574. No changes to production C023, independent UFR certificate promotion, or the PENROSE-003 proof trust DAG.

## Scientific meaning

The Novikov self-consistency analogy is used only as: a partial hypothesis cannot eliminate a branch without a **logically derived conflict** with the original constraints. This is conventional Boolean constraint propagation and *failed-literal probing*. There is no physical tachyon, future information, time loop, quantum oracle, or proof of P=NP.

The previous NOVIKOV-001 applied greedy single-bit repair to *complete* models and was slower (1.35–4.93x on the 60-case controlled sample). NOVIKOV-002 instead works on a partial list of values -1/0/1 and investigates whether an early contradiction can justify committing a forced value.

## Exact algorithm, soundness and important limits

- For SAT: classical unit propagation with distinct-variable tracking, plus tautology, duplicate literal and empty-clause handling.
- For native Exact-One: support-preserving bitset dynamic programming for the cardinality target exactly 1; respects repeated positive literals and complementary literals for a single variable. A local value is removed only if the original row has **no supporting assignment** for that value under current partial assignments.
- Two variants share **the identical** source, literal-vote preference, branching order and core propagation:
  - `unit`: propagate, then branch on most frequent unset variable, prefer the same input-only literal vote.
  - `lookahead`: at each partial state, tentatively set each value of the next two variables and propagate. If one branch proves inconsistent, the opposite value is forced. If neither is refuted, ordinary branching continues. All probe visits are charged.
  - `selective`: the same partial-state failed-literal reasoning, but globally reserves only 5% of available clause visits to speculative probing. If this local quota runs out, abandon the **unfinished probe** and continue the sound baseline search; never misinterpret the interrupted probe as an actual conflict. Every attempted work unit remains charged.
- Exact SAT models are independently checked using `janus_ufr_001.verify_model`.
- Search caps variables at 240, rows at 4,096, clause width at 24, and explicitly limits recursive nodes, clause visits, and wall time. Exhaustion returns `UNKNOWN`, **not** `UNSAT`.
- For n<=12, a returned UNSAT is additionally independently checked across all 2^n assignments; for n>12, a completed DPLL UNSAT is labeled **DPLL_UNSAT_NO_PORTABLE_PROOF** until an independent C023/UFR certificate is available.
- All experiments run forward in time. The PENROSE-003 strict event graph still bans `FINAL_GATE -> UFR_PRODUCE`; no speculative hint can create a producer dependency on its later reviewer.

## Correctness validation

[Independent GitHub Actions #41308187788](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41308187788) at source SHA `da00bdde288cbae64f429c6e8db69918515e373b`, all steps PASS: **8/8** NOVIKOV-002 test groups, **9/9** previous NOVIKOV-001 groups and the original C023 serialized replay verifier PASS.

The tests include random SAT/Exact-One formulas against independent full truth sets; every 2–4 variable partial assignment including contradictory rows, repeated or complementary Exact-One literals, deliberate false initial hypotheses, forced literals detected before any complete candidate is built, n240 deterministic UNKNOWN limits, and a real MAJ3-K4 n18 / 1024-clause bounded control. No unit's locally plausible state is assumed globally solvable.

## Fair n<=10 repeat benchmark

Uses the **same 60 fixed earlier cases**, suite SHA256 `865af20c649740dc7847a7204d9cd0c36470ddb66777c4e92c26bde33c58c53b`, 3 repeats per variant. All 60 outcomes agreed with independent UFR exact truth.

| Comparison vs identical `unit` search | Faster cases | Slower cases | Median whole-call runtime ratio |
| --- | ---: | ---: | ---: |
| Unrestricted two-variable failed-literal lookahead | 15 | 45 | **1.31x slower** |
| 5%-capped selective lookahead | 11 | 49 | **1.33x slower** |

The limited policy is not a time speedup; it makes computational costs predictable.

## Actual n18–n240 results with exact equal resource ceilings

One repetition each, **max 140 recursive nodes, 140,000 clause visits and 4 seconds per variant**. A result of UNKNOWN means no proof was completed inside the budget and is NOT a statement about SAT truth.

| Formula | Unit | Unrestricted lookahead | 5%-capped selective | Clause visits: unit / unrestricted / selective |
| --- | --- | --- | --- | --- |
| MAJ3-K4 n18, 1024 clauses | UNKNOWN | UNKNOWN | UNKNOWN | 93,279 / 140,001 / 100,280 |
| Planted random 3SAT n220 | **SAT verified** | UNKNOWN | **SAT verified** | 89,100 / 140,001 / 96,101 |
| Planted random 3SAT n240 | UNKNOWN | UNKNOWN | UNKNOWN | 140,001 / 140,001 / 140,001 |
| Embedded 4-variable UNSAT core in n220 | UNSAT search-only | UNSAT search-only | UNSAT search-only | 7,520 / 15,632 / 13,103 |
| Embedded 4-variable UNSAT core in n240 | UNSAT search-only | UNSAT search-only | UNSAT search-only | 8,068 / 16,900 / 14,353 |

The two synthetic n220/n240 UNSAT controls are generator-known UNSAT by a simple 16-clause four-variable blocking core, but this experiment does not produce an independently replayable UNSAT certificate. MAJ3-K4's earlier C023 proof establishes UNSAT separately; **no** NOVIKOV-002 strategy completed that instance under these budgets.

The constructed n220 and n240 inputs are not the user's historical March 2026 220–240-variable solver experiments or an external SAT competition benchmark. They are synthetic, deterministic and **not blinded**.

## Files and reproducibility

- `experiments/direct/janus_novikov_002.py`: native partial-state propagation, three explicitly controlled budgets/policies, independently checked complete SAT candidates.
- `tests/test_novikov_002.py`: 8 adversarial test groups and random finite truth controls.
- `experiments/direct/janus_novikov_002_benchmark.py`: the 60-case same-input control plus five large cases, with every UNKNOWN preserved in the JSON.
- `.github/workflows/validate-novikov-002.yml`: bounded read-only CI and artifact upload.
- `experiments/NOVIKOV_002_CLOUD_EVIDENCE_20261101.json`: durable source/provenance/metrics; full per-case evidence is downloadable in the [GitHub Actions artifact](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41308187788/artifacts/13084296108) (30-day retention).

**Promotion gate NOT_READY.** The only measured gain is that bounded lookahead can return to an otherwise successful baseline under a fixed resource budget, while unconstrained lookahead can exhaust it. No evidence that selective consistency outperforms well-engineered CDCL, C023, or ordinary unit propagation on these benchmarks. Next valid experiment requires independent larger challenge inputs and a genuinely information-efficient trigger for failed-literal probes.
