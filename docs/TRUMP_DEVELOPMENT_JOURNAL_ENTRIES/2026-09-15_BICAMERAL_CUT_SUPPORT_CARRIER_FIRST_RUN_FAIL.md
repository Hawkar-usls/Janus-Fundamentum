# 2026-09-15 — Bicameral cut-support carrier first-run failure

Authority: `HISTORICAL_DIAGNOSTIC__NO_PROMOTION`

Run `34916573617` / job `104215376204` failed closed. The failure did **not** refute the core support-intersection carrier on the frozen positive overwidth instance.

The positive path remained exactly as intended: parent canonical mincut returned `OPEN_MINCUT_BRANCH_BUDGET`, `k=20`, raw branch budget `2^20=1048576`, and zero branch enumeration. The successor carrier projected the two explicit relation tables to the full cut, intersected the supports without enumerating the raw cube, obtained exactly one common cut state, reconstructed an original witness, and returned `ADMIT_EXACT_CUT_SUPPORT_INTERSECTION_CARRIER`.

Two checker/control assumptions failed instead. First, the checker asserted the ordered support-size vector `[3,4]`, while canonicalization presented the same two supports as `[4,3]`; this is order-only and has no semantic content. Second, the intended `PARTIAL_CUT_VISIBILITY` negative control used three overlapping relation scopes whose third relation created alternate incidence paths, so it did not isolate the intended reason class even though the candidate still failed closed as `OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER`.

The immutable first-run result is stored in `research/TRUMP_BICAMERAL_CUT_SUPPORT_CARRIER_FIRST_RUN_FAILURE_2026-09-15.json`.

Allowed successor repair is narrow: keep the preregistered theorem/candidate architecture unchanged; make the support-size checker order-invariant and replace only the malformed partial-visibility control with one that isolates the frozen obligation. No scientific PASS may be claimed from this run.

Firewalls remain `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, `CONNECTED_MIXED_CORE_SOLVED=NO`.
