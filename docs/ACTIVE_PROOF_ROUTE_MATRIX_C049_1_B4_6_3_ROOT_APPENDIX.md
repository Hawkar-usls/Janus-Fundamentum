# Active proof route matrix — C049.1 B4.6.3 root appendix

```text
PR #104 hardened Node-9 integration + root preflight
-> PR #105 root acceptance/reflection obstruction
-> correct join-path domain
-> replay all affected B3/B4 descendants
-> only then restart root structural compression
```

| Layer | Diagnostic contribution | Decisive correction | Strict next gate |
|---|---|---|---|
| Superseded PR #107 diagnostic | The diagonal-inclusive recurrence reproduces `4,954,128` path multiplicities, `7,825` apparent width-1 outputs and one false zero-root state | Join/interleaving paths may use only `(1,0)` and `(0,1)`; diagonal `(1,1)` belongs to the extension-preorder path domain, not B3 join | `C049.1_B4.6.3_JOIN_PATH_DOMAIN_CORRECTION` |

```text
ROOT_PARENT_REFINEMENT_COMPLETE = FALSE
ROOT_PARENT_UP_K_COMPLETE       = FALSE
ROOT_FULL_SET_COMPUTED          = FALSE
FOUND_LAYOUT                    = FORBIDDEN
NO_LAYOUT_AT_CAP                = FORBIDDEN
P_VS_NP                         = OPEN
```
