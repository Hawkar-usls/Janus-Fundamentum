# C040.1 — Proof-Carrying Horn Producer-Lane Module Forests

**Status:** `CONSTRUCTIVE_RESTRICTED_THEOREM / P_VS_NP=OPEN`

## Canonical identity

```text
C040   portfolio-guided semantic-vtree discovery contract
C040.1 producer-lane affine/Horn module-forest implementation
```

The branch, executable, proposal and schema paths retain the legacy `c040` spelling because the package was assembled before the canonical C040 allocation was reconciled.

## Why the baseline refusal was too early

The first module-forest core formed maximal Horn components before checking the single-head condition. A component containing

```text
a -> q
b -> q
```

therefore returned `OPEN_HEAD_CONFLICT` immediately.

That refusal was sound but did not test the decomposition route proposed by C039.2: place conflicting producers in different single-head regions and charge the resulting interfaces.

C040.1 performs that test.

## Deterministic producer-lane discovery

For every positive Horn head `h`:

1. collect all rules headed by `h`;
2. sort them by factor identifier;
3. assign the rule of producer rank `k` to lane `k`.

Negative Horn constraints are assigned to lane zero. Inside every lane, C040.1 takes connected components of the Horn factor-variable incidence graph.

For a fixed head, one lane contains at most one producer. Every discovered Horn module is therefore single-head by construction.

The lane map is included in the certificate and independently recomputed by the verifier. It is not a supplied partition.

## Constructive consequence

The pair

```text
a -> q
b -> q
```

is no longer an automatic refusal. The two rules become two single-head modules sharing the one-variable separator `{q}`.

The exact module-forest dynamic program then decides and certifies the composition. The frozen 64-pair control is accepted with maximum module boundary one.

Thus duplicate heads can sometimes be removed by decomposition without changing the native Horn message language.

## Where the C039.2 obstruction moves

Apply producer lanes to the C039.2 family

```text
a_i -> q_i
b_i -> q_i
q_1 AND ... AND q_n -> z.
```

For every `q_i`:

- `a_i -> q_i` is in producer lane zero;
- `b_i -> q_i` is in producer lane one.

The lane-zero rules are connected through the final rule and form one central single-head module. Every lane-one producer forms a leaf module. Discovery therefore constructs a star rather than returning a head collision.

But the central module is incident to all separators

```text
q_1,...,q_n.
```

Its boundary has size `n`. Under the admitted exact table algebra, the dynamic program must charge `2^n` central boundary assignments. At `n=64`, C040.1 therefore returns

```text
OPEN_INTERFACE_WIDTH
```

before materializing the table.

This is the desired localization:

```text
duplicate producer heads can be isolated
but producer isolation does not automatically create a small interface
```

The result is consistent with the C039.2 boundary-CNF lower bound. The exponential cost has moved from an immediate language collision to the exact shared interface induced by the decomposition.

## Three producers

For

```text
a -> q
b -> q
c -> q
```

producer lanes create three single-head modules containing `q`. The current binary module-interaction contract permits each shared variable in at most two modules. The instance therefore returns

```text
OPEN_INTERFACE_HYPEREDGE
```

This is not an intrinsic hardness claim. It identifies the next missing composition object: proof-carrying hyperedge messages or a richer Horn module able to absorb several producers.

## Exact module-forest theorem

Let the raw factor encoding size be `L`. If producer-lane discovery yields:

```text
module language in {AFFINE_GF2, SINGLE_HEAD_HORN}
module interaction graph is a forest
every shared variable belongs to at most two modules
for every module M: |B_M| <= floor(log2 L)
```

then exact discovery, native solving, bottom-up interface composition, SAT recovery and UNSAT replay require

```text
sum_M 2^|B_M| poly(L_M)
```

work and certificate volume, hence polynomial total work.

Pure affine modules retain the C039.1 Gaussian/RREF engine. Pure lane modules retain the C039.2 least-model/single-head engine. Only cross-module interfaces are enumerated.

The derived binary variable vtree is checked as an embedding witness. The load-bearing tractability proof is the module-forest dynamic program; no polynomial standard factor-width claim is made.

## Proof package

The executable pair is:

```bash
python experiments/direct/janus_c040_portfolio_module_forest.py --self-test
python experiments/direct/janus_c040_producer_lane_isolation.py --self-test
```

The second executable imports the audited native solvers and dynamic-programming verifier, replaces only deterministic module discovery, and adds the lane map to the certificate.

The combined audit requires:

```text
350 baseline random module forests
350 producer-lane random module forests with exhaustive bounded validation
64 duplicate-producer pairs -> SAT_AFTER_LANE_ISOLATION
maximum duplicate-pair module boundary = 1
C039.2 blow-up family n=64 -> OPEN_INTERFACE_WIDTH
three producers of one head -> OPEN_INTERFACE_HYPEREDGE
alternating module cycle -> OPEN_MODULE_CYCLE
wide affine/Horn star -> OPEN_INTERFACE_WIDTH
180-module accepted chain
work exhaustion -> OPEN_WORK_BUDGET
unsupported language -> OPEN_LANGUAGE
corrupt producer-lane certificate -> REJECTED
```

Exhaustive enumeration remains confined to bounded test validation. It is not used by discovery, native solving, dynamic programming, witness recovery, or verification.

## Stack and reproducibility

C040.1 draft PR #60 is pinned to the exact C039.2 snapshot

```text
7954b91efe3062162887237c9a17cf1754aa6de3
```

because the active C039.2 branch advanced concurrently during package construction. Later canonical C039.2 workflow, proposal and source-map metadata are copied into the C040.1 head. No active sibling PR is rewritten or merged.

## Updated theorem boundary

C040.1 proves polynomial discovery and compilation when deterministic producer-lane modules form a forest and every complete module boundary is logarithmic.

It does not prove that every multi-producer Horn instance admits a small producer-lane interface, that hyperedge interactions are polynomial under the current algebra, that every C040 portfolio contains this candidate, or that arbitrary CNF admits this structure.

## Surviving gate

```text
RICHER_MESSAGES_OR_DISCOVERY_BEYOND_FOREST_LOG_BOUNDARIES
```

The next advance must compactly handle wide producer-lane stars, shared-variable hyperedges, or cyclic module interactions, while retaining proof-carrying join, projection, decision, witness recovery and strict polynomial accounting.

```text
P_VS_NP=OPEN
```
