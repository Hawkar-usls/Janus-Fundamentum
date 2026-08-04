# C049.1 Phase B4.6.3 — semantic `up_k` replay hardening

## Defect found by the negative-root attack

The first independent semantic replay was green on the positive B4.6.2 cycle,
but that cycle exercised only boundary coordinate dimensions `0` and `1`.
The verifier's local RREF routine omitted the final backward-elimination pass.
At dimension `2` this made the encoded basis depend on row insertion order:

```text
legacy rref((1,3), 2) = (3,1)
legacy rref((3,1), 2) = (2,1)
```

Those tuples represent the same full subspace of `GF(2)^2`. Treating them as
distinct would inflate the subspace inventory and invalidate a dimension-two
semantic `up_k` replay. The positive cycle did not expose the defect because
one-dimensional bases have no such collision.

## Hardened verifier

```text
experiments/direct/
  janus_c049_1_b4_6_3_semantic_up_k_root_replay_hardened.py
```

The hardened verifier patches only the independent verifier's basis primitive;
it imports neither the B4.5/B4.6 producer nor the B2 core. It adds the missing
backward-elimination pass, proves row-permutation confluence on a bounded
complete dimension-two control, and checks that `GF(2)^2` has exactly five
subspaces.

It then replays the complete positive B4.6.2 transcript again with the corrected
basis semantics.

## Coverage boundary

```text
positive-cycle semantic replay               = REPLAYED_HARDENED
dimension-two RREF permutation confluence     = CHECKED
dimension-two subspace inventory              = 5
dimension-two complete up_k closure            = NOT_REPLAYED_YET
negative root engine replay                    = OPEN
```

The previous green semantic result remains valid for the positive fixture, but
it is not promoted as evidence for a dimension-two negative root.

## Strict boundary

```text
FOUND_LAYOUT = FORBIDDEN_YET
NO_LAYOUT_AT_CAP = FORBIDDEN_YET
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

H002 and SIM-3 remain outside the proof perimeter.
