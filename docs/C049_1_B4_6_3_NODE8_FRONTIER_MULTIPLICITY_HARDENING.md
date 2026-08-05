# C049.1 B4.6.3 Node-8 Frontier Multiplicity Hardening

## Position in the stacked route

This layer is based exactly on PR #93 head:

```text
research/c049-1-b4-6-3-node8-frontier-structural-compression
54f15535647406bad3f6b4f02ed2b5e97efa52da
```

It does not replace the node-8 structural-compression theorem. It hardens the proof-carrying accounting that must be complete before PR #94 and later descendants may be treated as admitted.

## Binding source theorem

The hardening producer and independent verifier require the exact PR #93 artifact:

```text
bytes           204,739
file sha256     93dcd5610eb9df079823b172a4f824ce1c09859e759c6b771dc95b99af394d34
semantic digest 209f5a013ec492b67066abc3dcf08af183d2ec5ec0000f3d8d03a033cb32f9db
```

CI regenerates the complete negative prefix, admitted node-6 layer, node-7 frontier, node-7 `up_k`, node-7 integration, node-8 preflight, and the exact PR #93 artifact. The original independent verifier is rerun before this hardening layer is allowed to consume the artifact.

## New closed accounting obligations

The ten original `N8-INV-01..10` invariants remain byte-bound and independently replayed. Six additional invariants close the missing multiplicity obligations:

```text
N8-INV-11 exact quotient-path key domain and uniqueness
N8-INV-12 per-class and global source-path multiplicity conservation
N8-INV-13 collision conservation: sum(multiplicity-1) = 75-61 = 14
N8-INV-14 per-class and global direct-assignment work conservation
N8-INV-15 shrink-correction cell conservation: 220 zero + 88 one = 308
N8-INV-16 fixed certificate bytes, verifier operation charge, tamper contract,
          and strict terminal boundary
```

The exact source quotient domain is frozen for all thirteen retained left classes. Every `(left_class_id, local_path_index)` occurs exactly once.

## Frozen ledger

```text
source quotient classes       13
pre-shrink quotient paths     75
post-shrink classes           61
multiplicity sum              75
multiplicity histogram        47 classes x 1, 14 classes x 2
collision count               14
direct assignment work        31,500
shrink correction 0 cells     220
shrink correction 1 cells      88
correction cells total        308
```

The class ledger stores every source path key, each class multiplicity, collision contribution, direct-assignment work, and deterministic digest.

## Determinism

`ORIGINAL`, `REVERSED`, and `SEEDED_SHUFFLE` record orders produce byte-identical hardening artifacts.

Frozen hardening artifact:

```text
bytes           31,836
file sha256     e5cca8a4c873f23d53011daa6921008d6577300e22199c869832c2bfe467d5fd
semantic digest 75e1dd666de9596aba28eac51a7f88f29b74a5f6caae4d13f9488211f267ca71
source-domain digest
32a407b45d96c1a8b7823ce9d9d79969a2dbe61946f0cc53ee35b009a35ab605
class-ledger digest
36051983fbed5275c139c4f80f408a386a19e2bb7a7b9bc17a875109eb9318cb
```

The certificate byte field is solved to a fixed point and equals the final serialized artifact length.

## Charged replay work

```text
verifier operation charge 205,587
source bytes hashed        204,739
class records read              61
path records read               75
path-key tests                  75
correction cells read          308
assignment factor cells        220
class multiplicity checks       61
summary equalities              12
invariant slots                 16
```

No work counter is inferred from the compact final class count alone.

## Digest-repaired tamper contract

The independent verifier reconstructs the expected hardening artifact without importing the producer. It rejects twenty semantic attacks after the outer semantic digest and fixed-point byte field are repaired. The attacks cover source bindings, source-domain loss, class deletion/collision, path-key deletion/substitution, multiplicity and collision corruption, assignment-work corruption, correction-cell corruption, operation-charge corruption, invariant falsification, false root reachability, and false `NO_LAYOUT_AT_CAP` enablement.

```text
INVARIANTS = 16/16
DIGEST_REPAIRED_TAMPER_ATTACKS_REJECTED = 20/20
```

## Strict boundary

This hardening does not admit node-8 `up_k`, executor integration, node-9 refinement, root refinement, a discovered layout, or a complete negative root transcript.

```text
NODE8_FRONTIER_ORIGINAL_THEOREM_BOUND = TRUE
NODE8_FRONTIER_MULTIPLICITY_HARDENED  = TRUE
NODE8_PARENT_UP_K_COMPLETE            = FALSE
NODE8_INTEGRATED_INTO_EXECUTOR        = FALSE
NODE9_PARENT_REFINEMENT_STARTED       = FALSE
NEGATIVE_ROOT_REACHED                 = FALSE
FOUND_LAYOUT                          = FORBIDDEN
NO_LAYOUT_AT_CAP                      = FORBIDDEN
CURRENT_GLOBAL_TERMINAL               = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                               = OPEN
```

The next permitted action is:

```text
REPLAY_AND_REBIND_PR94_TO_NODE8_MULTIPLICITY_HARDENED_HEAD
```

Draft only. No automatic merge.
