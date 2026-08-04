# C049.1 Phase B4.6.3 — negative root engine replay

## Target

Exercise the B4.5 full-set engine on a genuine width-`1` negative instance
without allowing an incomplete execution to collapse to `NO_LAYOUT_AT_CAP`.

## Fixture

The whole-factor arrangement consists of six one-dimensional subspaces of
`GF(2)^3` in the order

```text
[2], [4], [6], [3], [5], [1]
```

with `k=1`. The first five factors in the displayed order have exact width
vector

```text
[1,1,1,1]
```

so the iterative-compression precondition is satisfied. After adding the sixth
factor, all `720` whole-factor permutations are replayed independently:

```text
minimum width = 2
accepting width-1 layouts = 0
all-layout digest = 55134e134ca0a16f20779964ecf2461bd20e1bb5a5a6d26b3e8d4cff7c098003
```

The canonical B4.2 scaffold has width vector

```text
[1,2,2,2,1]
```

and therefore forces the engine through its first boundary-coordinate
dimension-two `up_k` computation.

## Frozen engine audit

The six leaf full sets each have boundary-coordinate dimension `1` and exactly
`36` entries. Before the first dimension-two B2 closure, the engine completed
and retained:

```text
child pairs                              1,296
Delannoy paths / refinements           163,824
successful refinements                  12,073
failed refinements                     151,751
unique successful generators               468
duplicate successful outputs deleted    11,605
provenance occurrences                  12,073
```

The independent verifier confirmed the exact equalities

```text
sum(pair path counts) = refinement records
refinements = successful + failed
successful attempt ids = disjoint generator provenance partition
noncanonical provenance ids = duplicate deletion records
```

Thus no trajectory was lost in the complete prefix before B2.

## Honest capability stop

The semantic B2 closure received `468` generators at boundary-coordinate
dimension `2`. It stopped exactly at:

```text
terminal    OPEN_WORK_BUDGET
counter     lattice_cells
cap         2,000,000
attempted   2,000,001
stop node   6
```

No root full-set receipt was emitted. The actual root node is `10`, so the
negative root was not reached and no statement about missing root entries is
permitted.

## Certificate accounting

```text
manifest digest
6df541b6aa441f218a54acf9232184d00cd319701156673e543fca651dec94ed

transcript root digest
eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8

outer semantic digest
baf49b77bba0bf7139c2117b25333e6e1ab382d9a10138983e0f14c794d22257

chunks                         61
uncompressed chunk bytes       979,191,854
compressed chunk bytes          21,842,373
workflow artifact SHA-256
b6133fd46473df3f1ddb975bc2736d6a4327b6bc6ff3e51e4bac60644f326fad
```

The hardened verifier authenticates the transcript in one streaming pass and
reuses the immutable checked prefix for digest-repaired outer tamper controls.
It does not materialize the near-gigabyte transcript in memory.

## Attack result

```text
NO_TRAJECTORY_LOSS
= CLOSED_FOR_COMPLETE_PREFIX_BEFORE_B2

NO_UNSOUND_DOMINANCE
= NO_DOMINANCE_CONCLUSION_ISSUED_AFTER_INCOMPLETE_B2

NO_MISSING_ROOT_ENTRIES
= OPEN_ROOT_NOT_REACHED

NEGATIVE_ROOT_REACHED
= FALSE
```

This is a proof-carrying obstruction, not a failed proof and not a negative
terminal. The next exact gate is

```text
C049.1_B4.6.3_DIMENSION_TWO_UP_K_CAPABILITY_HARDENING
```

## Strict boundary

```text
FOUND_LAYOUT = FORBIDDEN_YET
NO_LAYOUT_AT_CAP = FORBIDDEN_YET
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

H002 and SIM-3 remain untouched.
