# C049.1 B4.6.3 — Corrected Node-7 parent frontier compression

## Scope

This layer starts from the exact admitted head of PR #111:

```text
PARENT_PR   = 111
PARENT_HEAD = af0556d4ae05ea6dc343d120a34f67255890ba18
```

It consumes only the corrected Node-6 full set produced through the H/V join domain.

Historical Node-6 through root full sets, the legacy Node-7 frontier artifact, the legacy thirteen-class count, and the legacy Delannoy workload are forbidden as theorem inputs.

## Corrected child inventory

```text
left corrected Node-6 entries = 432
right whole-factor leaf entries = 36
child pairs = 15,552
ordinary H/V refinements = 1,531,584
```

The corrected left inventory has exactly two skeleton languages:

```text
LEFT_A = 216 entries
LEFT_B = 216 entries
```

The historical two-run `LEFT_C` language is absent.

## H/V quotient theorem

Ordinary join refinements use only:

```text
(1,0), (0,1)
```

The run-index projection of every fine H/V path, after deleting stutters, remains H/V-only. No diagonal quotient step is admitted.

For each `3 × 2` skeleton grid there are exactly three H/V quotient paths. With two corrected left skeletons:

```text
2 × 3 = 6 quotient classes
```

The proof replays all abstract run-length profiles with run lengths 1, 2, or 3:

```text
run-length profiles per left skeleton = 3^5 = 243
abstract fine H/V paths per left skeleton = 23,931
abstract fine H/V paths total = 47,862
diagonal quotient steps = 0
```

Every quotient path has a fine H/V lift.

## Geometry

```text
left boundary   = [4,2]
right boundary  = [6]
right transport = [3] in parent coordinates
common boundary = [4,2]
parent boundary = [4,2]
```

Left expansion and shrink are identities. The join lambda correction is zero on all twelve quotient cells, and the joined-symbol map is injective in each skeleton grid.

## Complete successful frontier

Each of the six quotient paths has a reachable zero envelope of length four. Every compact successful binary output in that class is directly covered by the zero envelope under the extension preorder.

```text
binary typical patterns per quotient cell = 6
direct assignments per class = 6^4 = 1,296
classes = 6
total direct assignments = 7,776
```

Extension-preorder witnesses retain H/V/diagonal steps. This does not reintroduce diagonals into ordinary joins.

The complete refinement space is partitioned by complete H/V quotient projection and the width dichotomy:

```text
compact width <= 1  -> successful output, directly covered
compact width > 1   -> failed refinement
```

No actual `1,531,584`-record refinement transcript is materialized.

## Candidate boundary before exact-head CI

```text
PR111_CORRECTED_NODE6_INTEGRATION = ADMITTED
PR112_CORRECTED_NODE7_FRONTIER_COMPRESSION = CI_PENDING
CORRECTED_NODE7_PARENT_GENERATOR_FRONTIER_COMPLETE = FALSE
CORRECTED_NODE7_PARENT_REFINEMENT_COMPLETE = FALSE
CORRECTED_NODE7_PARENT_UP_K_COMPLETE = FALSE
CORRECTED_BOTTOM_UP_REPLAY_COMPLETE = FALSE
ROOT_STRUCTURAL_COMPRESSION_ADMITTED = FALSE
ROOT_PARENT_REFINEMENT_COMPLETE = FALSE
ROOT_FULL_SET_COMPUTED = FALSE
ROOT_EMPTY_PROVED = FALSE
FOUND_LAYOUT = FORBIDDEN
NO_LAYOUT_AT_CAP = FORBIDDEN
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

Only after green exact-head CI may the frontier and parent-refinement flags be raised.

## Next gate after admission

```text
C049.1_B4.6.3_CORRECTED_NODE7_SIX_GENERATOR_UP_K_HARDENING
```
