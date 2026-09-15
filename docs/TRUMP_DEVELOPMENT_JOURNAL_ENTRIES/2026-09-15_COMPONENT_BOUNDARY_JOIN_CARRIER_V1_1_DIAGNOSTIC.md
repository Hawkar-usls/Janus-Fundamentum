# 2026-09-15 — component-boundary join carrier v1.1 diagnostic

Authority: `DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION`.

GitHub Actions run `34917919531`, job `104219470394`, executed the original v1 candidate blob `89f5d591d4d553bb26489908a79f2c739f62b756` unchanged under a stage-by-stage exception surface.

The source guard completed. The first scientific-control stage, `POSITIVE_OVERWIDTH_COMPONENT_JOIN`, raised `KeyError: 'tree_sha256'` in `component_boundary_support` while building the receipt for a singleton relation component.

Root cause: `deterministic_join_tree()` correctly treats one relation as a trivial valid tree, but that early return did not attach the same canonical `tree_sha256` field that the multi-relation path attaches. Receipt construction therefore crashed before semijoin/exactness obligations were evaluated.

Classification: `PROVENANCE_RECEIPT_IMPLEMENTATION_BUG__NOT_SEMANTIC_JOIN_TREE_FALSIFIER`.

Allowed successor repair is restricted to providing a canonical hash/receipt for the singleton tree case. The frozen v1 candidate remains immutable in its original commit. No changes to anchor-state discovery, multi-relation tree construction, running-intersection verification, semijoin logic, controls, or theorem scope are authorized by this diagnostic.

Firewalls remain unchanged: `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, `CONNECTED_MIXED_CORE_SOLVED=NO`.
