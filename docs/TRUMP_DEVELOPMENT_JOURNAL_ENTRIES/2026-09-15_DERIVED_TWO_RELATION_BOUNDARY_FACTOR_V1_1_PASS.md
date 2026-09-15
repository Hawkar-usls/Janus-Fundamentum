# 2026-09-15 — Derived two-relation boundary factor v1.1 PASS

Final scoped verdict:

`PASS_SCOPED_BICAMERAL_OVERWIDTH_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_V1_1`

The v2.9 open surface required a component boundary carrier without assuming a raw relation already covered the entire overwidth canonical cut. The first frozen successor was deliberately narrower than arbitrary elimination: every non-singleton cut component had exactly two relations, and their scope union had to cover the full cut.

For a two-relation component the candidate constructs exactly one natural join over explicit input rows, checks every shared variable, projects compatible row pairs to the full cut, and stores one original compatible row-pair witness per derived cut state. The derived support size is bounded by `|R1|*|R2|`, giving a fixed quadratic component-output envelope. A component of three or more relations returns OPEN before any join chain.

The immutable v1 run `34919089657` failed only in provenance serialization after a positive carrier had been built: tuple-valued cut states were Python dictionary keys and could not be directly JSON-serialized for hashing. That run is preserved as `FAIL_INFRASTRUCTURE_SERIALIZATION_BEFORE_RECEIPT`. v1.1 repaired JSON-safe provenance serialization only; frozen v1 candidate blob `1047351df47ed5f326eef2650da0c9f5ee0f2fda` remained unchanged.

GitHub Actions run `34919310274`, job `104223627451`, head `66e8055ad2d5aedf08379decc50e112779bee714` passed the independent checker, verdict assertion, canonical mincut regression, cut-support regression, component join-tree v1.3 regression, exact-interface-quotient regression and factorized-feedback regression.

Positive machine receipt:
- canonical cut `B = [0..19]`;
- predecessor parent `OPEN_MINCUT_BRANCH_BUDGET` with zero raw branches;
- predecessor full-anchor join-tree carrier `OPEN_NO_FULL_CUT_ANCHOR`;
- cut components `[[0],[1,2]]`;
- the two-relation component had no raw full-cut anchor but the relation-scope union covered all `B`;
- candidate performed 9 row-pair comparisons, exactly equal to the frozen row-product bound 9;
- independent hash-indexed join produced the same derived support;
- effective global support size was 1;
- original witness replay passed;
- raw `2^20` enumeration was 0;
- unbounded join chains were 0.

Negative controls behaved as preregistered: empty pair support gave exact UNSAT; three relations remained OPEN; incomplete pair cut cover remained OPEN at the unit gate; injected hint and tampered provenance were rejected.

This closes only the two-relation no-full-anchor bounded-output subproblem. It does not justify arbitrary-length elimination or general multi-relation compression.

Next local blocker: a canonical overwidth cut component containing three or more interacting relations and no raw full-cut anchor, where any admissible derived boundary message must carry a **uniform original-L polynomial envelope independent of relation count**. Candidate successor families remain raw-derived affine quotient with exact factor-through adequacy, factorized partial-boundary carrier, or another bounded-width/finite-congruence elimination theorem. Otherwise OPEN.

Scientific firewall unchanged: `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`.
