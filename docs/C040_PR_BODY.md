## Purpose

Advance C039/C039.1 from native symbolic factor algebras to the first charged portfolio-guided decomposition discovery theorem.

C040 receives raw tagged factors, not a supplied module partition or vtree. It deterministically constructs maximal pure affine and pure Horn connected components, rejects Horn components with duplicate positive heads, builds the exact module interaction graph, and admits only acyclic networks with logarithmic per-module shared-variable interfaces.

## Constructive theorem

Let the raw factor encoding size be `L`. Suppose discovery produces modules satisfying:

```text
module language in {AFFINE_GF2, SINGLE_HEAD_HORN}
module interaction graph is a forest
every shared variable belongs to at most two modules
for every module M: |B_M| <= floor(log2 L)
```

Then C040 constructs and verifies in

```text
sum_M 2^|B_M| poly(L_M)
```

work and certificate volume:

- the canonical native-module partition;
- the module interaction forest;
- a verified derived binary variable vtree;
- exact bottom-up separator messages;
- a complete SAT witness, or
- a recursively replayable UNSAT certificate.

Pure affine modules use Gaussian elimination with XOR provenance. Pure single-head Horn modules use least-model closure with derivation/conflict traces. Only cross-language module interfaces are enumerated.

## Proof-carrying composition

For a rooted module `M`, enumerate assignments to its complete incident boundary `B_M`. Under each assignment:

1. run the native module solver;
2. replay every child separator message;
3. accept exactly when the native module and all child subtrees accept.

Project the accepted rows to the parent separator. Every false row records one blocker for every full-boundary extension:

```text
NATIVE_UNSAT
CHILD_FALSE
```

SAT recovery follows deterministic chosen extensions from roots to leaves and checks the final assignment against every original factor.

## Discovery and vtree boundary

The module partition is discovered by same-language factor-variable connectivity. A binary variable tree is then derived deterministically and checked to contain every input variable exactly once.

The vtree is an embedding witness, not a claim of polynomial standard TDD/SDD factor width. The load-bearing tractability proof is the module-forest dynamic program.

## Exact OPEN terminals

```text
OPEN_LANGUAGE
OPEN_HEAD_CONFLICT
OPEN_INTERFACE_HYPEREDGE
OPEN_MODULE_CYCLE
OPEN_INTERFACE_WIDTH
OPEN_NONPOLYNOMIAL_INTERFACE_LIMIT
OPEN_WORK_BUDGET
OPEN_TABLE_BUDGET
OPEN_CERTIFICATE_VOLUME
```

A cycle or head conflict is not promoted to intrinsic hardness. It is outside this theorem.

## Frozen audit

```bash
python experiments/direct/janus_c040_portfolio_module_forest.py --self-test
```

Required controls:

```text
350 random admitted module forests on at most 9 variables
exact SAT/UNSAT agreement with bounded exhaustive validation
independent certificate replay
180-module alternating affine/Horn chain
64-variable affine core
64-variable single-head Horn core
64 duplicate-producer pairs -> OPEN_HEAD_CONFLICT
alternating four-module ring -> OPEN_MODULE_CYCLE
24-leaf interface star -> OPEN_INTERFACE_WIDTH
work exhaustion -> OPEN_WORK_BUDGET
unsupported beta-acyclic tag -> OPEN_LANGUAGE
corrupt message certificate -> REJECTED
```

Finite exhaustive checks validate implementation only.

## Located gate

```text
RICHER_MESSAGES_OR_POLYNOMIAL_DISCOVERY_BEYOND_ACYCLIC_LOG_INTERFACES
```

A next route must absorb multi-producer Horn components, extend certified composition to a rigorously larger cyclic class, or discover non-enumerative polynomial interfaces. A supplied partition, heuristic score improvement, or small final representation without charged construction does not pass the gate.

## Lineage and claim boundary

This draft is stacked directly on PR #55 / C039.1 and inherits C039 affine symbolic factors. It does not modify older sibling numbering drift and requests no automatic merge.

C040 is complete only for the discovered acyclic portfolio class with logarithmic module boundaries. It does not solve unrestricted Horn-affine mixtures, arbitrary CNF, or P versus NP.

```text
P_VS_NP=OPEN
```
