# C049.1 B4.6.3 — root quotient reflection obstruction

This stacked draft starts from admitted exact head

```text
babdf21ba20c1d24ed97fff4bb14121d0dfc1287
```

and attacks the first proposed root structural-compression shortcut.

## Exact root boundary

```text
left boundary   [1]
right boundary  [1]
common boundary [1]
parent boundary []
k               1
```

The shrink is genuine. A quotient path that is successful on the retained lower envelopes is not automatically successful for every fine trajectory pair represented by the same child product language.

## Decisive counterexample

Use retained Node-9 class `N9-S02`, the canonical leaf-5 zero envelope, and quotient path

```text
(0,0) -> (1,0) -> (2,0) -> (2,1).
```

The lower-envelope replay yields

```text
raw root values     [0,1,1,0]
compact root values [0,1,0]
width               1
```

so the lower pair accepts at `k=1`.

Keep the same left trajectory and the same quotient path, but replace the right lower envelope by admitted leaf-5 fine entry index `30`:

```text
right fine trajectory values [1,0].
```

The exact B3 join and shrink replay yields

```text
raw root values     [1,2,2,0]
compact root values [1,2,0]
width               2
```

so this represented fine refinement fails.

Therefore

```text
successful lower envelope
DOES NOT IMPLY
universal success of the root quotient path.
```

The Node-9 universal lower-envelope failure argument cannot be reversed into a root success/reflection theorem. Any root compression must partition each quotient path into sound success and failure subclasses, or prove an equivalent reflection invariant over the complete typical-pattern product language.

## Proof-carrying package

```text
experiments/direct/janus_c049_1_b4_6_3_root_reflection_obstruction.py
experiments/direct/janus_c049_1_b4_6_3_root_reflection_obstruction_verifier.py
registry/c049-1-b4-6-3-root-reflection-obstruction.json
.github/workflows/validate-c049-1-b4-6-3-root-reflection-obstruction.yml
```

The independent verifier reimplements the dimension-one B3 join correction, genuine shrink to the empty boundary, scalar compactification, and both width computations. A digest-repaired semantic tamper is rejected.

## Strict boundary

This obstruction does not compute the root full set and does not prove that the root is empty or nonempty.

```text
ROOT_PARENT_REFINEMENT_COMPLETE = FALSE
ROOT_FULL_SET_COMPUTED          = FALSE
ROOT_EMPTY_PROVED               = FALSE
FOUND_LAYOUT                    = FORBIDDEN
NO_LAYOUT_AT_CAP                = FORBIDDEN
CURRENT_GLOBAL_TERMINAL         = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                         = OPEN
```

The corrected next gate is

```text
ROOT_QUOTIENT_REFINEMENT_WITH_SUCCESS_FAILURE_SUBCLASS_PARTITION_AND_REFLECTION_PROOF
```
