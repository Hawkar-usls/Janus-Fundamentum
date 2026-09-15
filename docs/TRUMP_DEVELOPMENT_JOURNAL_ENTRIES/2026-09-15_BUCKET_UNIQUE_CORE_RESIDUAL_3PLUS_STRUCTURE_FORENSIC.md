# TRUMP — unique-core residual 3+ structure forensic — 2026-09-15

Status: `PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_3PLUS_STRUCTURE_FORENSIC`.

Authority: diagnostic only. No theorem promotion and no global APMA frontier advance.

## Why this run existed

The v3.6 successor closed unique-core-conditioned residual components of size 1 and 2, while returning `OPEN_RESIDUAL_COMPONENT_GT2` before any unbounded join chain. Captain Obvious required a read-only forensic of the first real 3+ residual component before any new carrier was proposed.

## Frozen target

The target was exactly `residual_component_gt2_control()` from the sealed v3.6 candidate. No solver semantics were changed and no 3-way join was materialized.

## Result

The target component consists of `orig:4`, `orig:5`, `orig:6`. Its relation-overlap graph is a triangle. Every edge overlap is the same single Boolean residual variable `47`.

- relation articulation vertices: none;
- variable articulation points: `[47]`;
- deterministic max-overlap join tree satisfies running intersection;
- every pair has 4 x 4 explicit rows, 16 comparisons, 8 compatible pairs;
- every row has pairwise support;
- pairwise semijoin closure is immediately `[4,4,4]` and therefore does not solve the component;
- 3+ join chains materialized: 0;
- global residual Cartesian products materialized: 0.

Candidate and independent checker agreed using different methods: profiler Kruskal + nested pair loops versus checker Prim + hash-indexed compatibility. Parent v3.6 regression also remained PASS.

Actions: `34982303998 / 104425422440`.

## Captain Obvious readout

The nearest missing exact obligation is not a general 3+ join theorem. The whole triangle is coupled through a single raw-derived Boolean variable articulation point. Therefore the next falsifier should condition only on variable `47` with exactly two branches. Each branch must recompute the residual graph and must fall entirely into already sealed residual components of size <=2 before any carrier is admitted. If either branch still contains a 3+ residual component, the successor remains OPEN.

This is a scoped successor of the existing separator and residual-portfolio machinery, not evidence that arbitrary partial-overlap components are tractable.

## Firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `GENERAL_PARTIAL_OVERLAP_FACTORIZATION = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
