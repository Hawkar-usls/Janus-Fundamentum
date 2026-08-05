# C049.1 B4.6.3 — root acceptance-reflection obstruction

```text
BASE = PR #104 / babdf21ba20c1d24ed97fff4bb14121d0dfc1287
STATUS = DRAFT_EXACT_HEAD_CI_REQUIRED
ROOT_STRUCTURAL_COMPRESSION = BLOCKED_PENDING_REFLECTION_CORRECTION
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

## Purpose

PR #104 reaches Node 10 on the fully hardened ancestry and freezes the exact root preflight:

```text
left Node-9 entries = 252
right leaf-5 entries = 36
child pairs = 9,072
fine Delannoy refinements = 4,954,128
common boundary = [1]
parent boundary = []
shrink identity = false
```

The next proposed step was structural compression of this root frontier. Before admitting such a compression, this draft attacks the necessary reflection statement:

```text
an accepting root trajectory under the current B3/full-set semantics
must reflect an actual grouped width-k layout.
```

## Decisive mismatch

The frozen six-factor fixture is

```text
d = 3
k = 1
whole factor blocks = [[2],[4],[6],[3],[5],[1]]
affine offsets = [0,0,0,0,0,0]
```

An independent exhaustive oracle replays all `6! = 720` whole-factor orders and all five cuts of each order:

```text
minimum grouped linear-layout width = 2
width-1 layouts = 0
width-2 layouts = 288
width-3 layouts = 432
```

The current B3 join/shrink semantics are then applied exactly to the full admitted root child languages, without using the retained-generator shortcut. The verifier evaluates all `207,360` root lattice cells and uses exact Delannoy dynamic programming rather than materializing the `4,954,128` paths:

```text
child pairs with at least one width-1 refinement = 764
width-1 fine refinements = 7,825
```

Their compact scalar root outputs are:

```text
0    ->    1
01   -> 1,898
010  -> 1,351
1    ->   221
10   -> 1,898
101  -> 2,456
```

In particular, one exact child pair has cell table

```text
[[0,1],
 [1,0]]
```

and its diagonal Delannoy path produces the compact zero-root trajectory `0`.

Therefore the current local acceptance language contains an accepting root state although the independent grouped-layout oracle contains no width-1 order.

## Shortcut attack

Using only the two retained Node-9 lower-envelope generators does not repair the issue. That tempting quotient has:

```text
8 quotient paths
26 visited quotient cells
join corrections:   26 x 0
shrink corrections: 16 x 0, 10 x 1
compact outputs:     7 x 010, 1 x 0
```

Without a reflection theorem, this shortcut would promote the same false accepting zero state. It is therefore explicitly forbidden as a root structural-compression proof.

## What is proved — and what is not

This obstruction proves a semantic inconsistency between:

1. the current B3/root full-set acceptance calculation; and
2. exhaustive grouped-layout existence on the frozen fixture.

It does **not** yet localize the defect. At least one of the following must be corrected or supplied:

```text
upstream structural frontier realizability
up_k closure interpretation at the root
join/shrink implementation or coordinate convention
root acceptance/reflection theorem
```

No upstream PR is silently revoked by this draft. Their local transcript theorems remain frozen, but they may not be composed into a root acceptance claim until the reflection gap is resolved.

## Independent replay

The producer and verifier independently:

- bind the exact PR #104 manifest, summary, Node-9 `up_k` artifact and child receipts;
- recompute all 720 grouped layouts;
- recompute root length histograms, 9,072 pairs and 4,954,128 Delannoy refinements;
- evaluate every root cell using the committed B3 join and true `[1] -> []` shrink equations;
- count every width-1 path with exact dynamic programming;
- recover all six compact scalar output patterns and the unique zero witness;
- attack the retained-envelope-only quotient;
- reject twelve semantic modifications after digest repair.

## Strict boundary

```text
PR104_NODE9_INTEGRATION_REBOUND = ADMITTED
ROOT_REACHED_ON_REBOUND_CHAIN = TRUE
ROOT_PARENT_REFINEMENT_STARTED = TRUE

ROOT_PARENT_REFINEMENT_COMPLETE = FALSE
ROOT_PARENT_UP_K_COMPLETE = FALSE
ROOT_FULL_SET_COMPUTED = FALSE
ROOT_EMPTY_PROVED = FALSE
TERMINAL_COMPLETENESS_PROVED = FALSE
FOUND_LAYOUT = FORBIDDEN
NO_LAYOUT_AT_CAP = FORBIDDEN
P_VS_NP = OPEN
```

The surviving gate is no longer immediate frontier compression:

```text
C049.1_B4.6.3_ROOT_ACCEPTANCE_REFLECTION_CORRECTION
```

Only after that correction proves that the root language is sound and complete may `ROOT_PARENT_FRONTIER_STRUCTURAL_COMPRESSION` resume.
