# 2026-09-15 — Bucket unique-core residual no-pair structure forensic

Authority: `DIAGNOSTIC_ONLY`

Verdict: `PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_PAIR_SEPARATOR_STRUCTURE_FORENSIC`

The frozen v3.10 K4 control remained `OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR`. Under the preregistered fixed diagnostic cap 3, both profiler and an independent BFS/Prim/hash-signature checker found minimum raw residual variable-cut size exactly 3.

Residual scopes were:

- `{92,93,94}`
- `{92,95,96}`
- `{93,95,97}`
- `{94,96,97}`

Minimum cuts were exactly the four incident-edge triples `[92,93,94]`, `[92,95,96]`, `[93,95,97]`, `[94,96,97]`. A deterministic spanning-tree check failed running intersection on variables `95,96,97`.

The decisive Captain diagnostic is narrower: for every residual variable 92..97 and for each Boolean value 0/1, exact row restriction remained nonempty and the recomputed minimum raw variable-cut size dropped from 3 to 2. This establishes only that a pair cut appears structurally after one condition. It does **not** establish that such a pair is admissible under the sealed v3.10 requirement that every exact pair branch reduce to residual components of size at most two or exact UNSAT.

Therefore the next obligation is not a triple-separator theorem. It is a diagnostic of `single condition -> pair admissibility / branch component sizes`. In particular, a pair cut may merely isolate one K4 relation while leaving a residual K3 component.

Actions: `35003910809 / 104498782752` — full SUCCESS, including v3.10 regression.

Resource receipt: zero SAT separator assignments, zero separator sets size >=4, zero 3+ join chains, zero global residual Cartesian products, no budget raise.

Firewalls remain: `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, no global APMA frontier advance.
