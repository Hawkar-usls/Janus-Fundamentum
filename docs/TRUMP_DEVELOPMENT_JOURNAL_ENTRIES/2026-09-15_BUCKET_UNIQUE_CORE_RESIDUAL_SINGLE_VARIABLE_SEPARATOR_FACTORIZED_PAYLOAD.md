# TRUMP development journal — unique-core residual single-variable separator

Date: 2026-09-15

## Context

The v3.7 forensic profile isolated the first residual component of size >2 after exact unique-common-core conditioning. Its three factors (`orig:4`, `orig:5`, `orig:6`) form a relation-overlap K3, but all three pairwise overlaps are exactly the same Boolean residual variable `47`. Pairwise semijoin did not reduce the rows, while removing variable `47` disconnects the relation dependency.

Captain Obvious therefore selected the nearest missing exact obligation: condition on the raw-derived single Boolean articulation variable before any 3plus join, then reuse only the sealed residual component size <=2 carriers.

## Frozen experiment

Preregistration was frozen before implementation at commit `913cbe32145df5931f282fdd7403adc620f0e5d2`.

Candidate commit: `86678c8d725d9355fe6638c8e02d88791a302baa`.
Candidate blob: `cd17292b7451b03b966dbcf62d1b6e4c767f7ac0`.
Independent checker commit: `deabafaf0861f796d19dc0ecf8a2ccaae42ddeb1`.
Workflow head: `11a3adaf62e365949302e2164327ce8285f6f168`.
Actions: run `34993184716`, job `104462750297`.

## Result

Scoped verdict:

`PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_V1`

The candidate and independent checker both derive separator variable `47` without a trusted hint. Exactly two branches are evaluated: `47=0` and `47=1`. Each branch recomputes the residual dependency graph after exact row restriction. The positive control has both branches admitted as exact SAT branches with original witness replay.

Control outcomes:

- positive: `ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD`;
- positive branches: SAT / SAT;
- one-branch control: exact empty-restriction UNSAT / exact SAT;
- both-branch control: exact UNSAT / exact UNSAT, yielding `EXACT_UNSAT_BY_BOTH_SEPARATOR_BRANCHES`;
- no-single-variable-articulation control: `OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR`;
- branch-still->2 control: `OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR`;
- injected separator hint: `REJECT_RAW_INPUT`;
- tampered proposal: `REJECT_TAMPERED_PROVENANCE`.

No three-plus natural join chain was materialized, no global residual Cartesian product was materialized, the L2 budget was not raised, and no alternative elimination order search was used.

Regressions remained green for v3.6 residual <=2, v3.5 conditioned payload, factorized feedback, guarded elimination, and the Schaefer mixed-carrier barrier.

## Scientific meaning

This closes only the scoped surface in which the already unique common-core state is followed by a raw-derived single Boolean residual articulation variable whose two exact conditioned branches reduce to residual components of size at most two (or exact branch UNSAT). It does not establish general residual separator tractability, general connected mixed-core tractability, or general SAT in P.

Firewalls remain:

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
