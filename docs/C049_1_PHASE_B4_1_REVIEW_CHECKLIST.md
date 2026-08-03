# C049.1 Phase B4.1 review checklist

Reviewers should independently confirm:

- every insertion candidate appears in the frozen round manifest;
- candidate cut-width vectors are recomputed from grouped factor blocks;
- failed candidates remain in the transcript;
- per-round cumulative work is strictly increasing;
- global cumulative work equals the sum of complete round costs;
- `OPEN_WORK_BUDGET` preserves the exact tested manifest prefix;
- every selected order belongs to the independently enumerated width-`k` oracle;
- the six-block insertion obstruction has zero successful insertions and exactly 72 exhaustive width-1 layouts;
- grouped factor partition loss is rejected;
- repaired-digest changes to order, width vector, and global cumulative work are rejected;
- `OPEN_TRAJECTORY_ENGINE_INCOMPLETE` is never promoted to `NO_LAYOUT_AT_CAP`.

B4.1 does not claim the complete branch-decomposition/full-set refinement engine.
