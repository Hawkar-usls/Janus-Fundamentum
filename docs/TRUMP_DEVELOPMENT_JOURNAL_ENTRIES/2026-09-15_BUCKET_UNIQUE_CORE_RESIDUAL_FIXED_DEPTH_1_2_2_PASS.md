# 2026-09-15 — Bucket unique-core residual fixed-depth 1→2→2 PASS

The active v3.13 diagnostic licensed exactly one successor: a fixed-depth `1→2→2` residual separator portfolio. General recursion, arbitrary depth, separator sets of size three or more, general treewidth claims, and multi-relation join chains remained forbidden.

The frozen candidate reused only previously sealed lower layers. It scanned for one raw residual Boolean variable, then one raw pair in each nonempty branch, then at most one second pair on a unique three-relation GT2 remainder. Every terminal leaf had to be exact-empty or reduce to residual components of size at most two before the sealed v3.6 portfolio and guarded elimination were allowed.

An independent checker was added after the candidate freeze. It used BFS componentization, its own restriction implementation, and independent unordered-pair scans. It did not use candidate plan-discovery helpers.

GitHub Actions run `35010169968`, job `104519853649`, completed SUCCESS. Candidate and independent checker derived the same plan:

- single variable `92`;
- first pair `[93,94]` for both values of 92;
- second pair `[95,96]` in every first-pair branch;
- exactly 32 logical leaf equivalents covered.

The positive K4-style predecessor-open control was admitted with full original witness replay. The frozen structural K5 depth-cap unit control remained `OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND`. Injected plan/separator hints were rejected and a tampered plan receipt was rejected.

Resource receipt remained fixed: no unbounded recursion, no separator sets size >=3, no 3+ join chain, no global residual Cartesian product, no solver oracle, no budget raise. Conservative scoped envelope is `O(L^12)` with exponent independent of relation count because separator depth and branch count are fixed constants in this theorem.

Regressions were green for v3.13 forensic, v3.10 pair separator, v3.6 <=2 portfolio, guarded elimination, and the Schaefer mixed-carrier barrier.

Scoped verdict:

`PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_SEPARATOR_PORTFOLIO_V1`

Firewalls unchanged: `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, `CONNECTED_MIXED_CORE_SOLVED=NO`. No global APMA frontier advance.
