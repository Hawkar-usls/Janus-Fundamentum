# C040.1 package manifest

Canonical logical cycle:

```text
C040.1 producer-lane affine/Horn module-forest implementation
```

Legacy `c040` paths are retained for deterministic replay.

The draft proof package consists of:

- `experiments/direct/janus_c040_portfolio_module_forest.py` — baseline native module-forest core;
- `experiments/direct/janus_c040_producer_lane_isolation.py` — canonical producer-lane implementation;
- `docs/C040_PORTFOLIO_GUIDED_MODULE_FOREST.md` — baseline core note retained for replay;
- `docs/C040_PRODUCER_LANE_STRENGTHENING.md` — canonical C040.1 theorem note;
- `proposals/C040-PORTFOLIO-GUIDED-MODULE-FOREST.json`;
- `registry/c040-source-map.json`;
- `schemas/c040-portfolio-module-forest-v1.schema.json`;
- `.github/workflows/validate-c040-portfolio-module-forest.yml`;
- `docs/ACTIVE_PROOF_ROUTE_MATRIX.md`.

The PR is pinned to the exact C039.2 snapshot `7954b91efe3062162887237e04ad866ea148f869a3a` and includes the later canonical C039.2 metadata updates in its head. It remains draft-only. No automatic merge or admission is requested.
