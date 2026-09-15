# C024 — Root selector necessity

Status: **FINITE_FALSIFICATION_OF_SELECTOR_INDEPENDENCE / SELECTED_TEMPLATE_REACHABILITY_OPEN**  
Scope: immediate-local root post-result clauses containing an unshielded component-spanning non-tail bridge.

## 1. Question attacked

The exact Policy-0A selected branch is safe for every root unshielded occurrence through `GT_12`. A stronger possibility was:

> perhaps every available root branch variable is safe, so the maximum-frequency/minimum-index selector is irrelevant.

The all-variable root audit falsifies this decisively.

For every root unshielded occurrence, the audit assigns every variable present in the root post-CNF in both polarities, replays full child unit closure, and independently classifies the tracked clause/literal lineage as:

```text
terminal or extinct;
component-spanning non-bridge;
tail-singleton safe;
canonically N_a-shielded;
unsafe unshielded survivor.
```

Nonselected branches are hypothetical counterfactuals; they are not claimed to be Policy-0A executions.

## 2. Exact result through GT_12

```text
root unshielded occurrences                 62
all-variable polarity trials             6,960
unsafe unshielded trials                  3,404
unsafe trials using selected variable         0
unsafe trials using nonselected variable  3,404
```

The actual selected-variable outcomes are all safe:

```text
CANONICALLY_SHIELDED   40
CLAUSE_EXTINCT         55
SPANNING_NONBRIDGE     26
TAIL_SINGLETON_SAFE     3
UNSAFE_UNSHIELDED       0
```

The counts exceed twice the number of occurrences because a single occurrence may be represented by multiple local source antecedents in the counterfactual audit; the safety claim is per tracked occurrence and branch polarity.

Unsafe hypothetical trials by order:

```text
GT_4      12 /    48
GT_5      14 /    40
GT_6      22 /    60
GT_7      54 /   126
GT_8     130 /   280
GT_9     210 /   432
GT_10    322 /   630
GT_11    718 / 1,430
GT_12  1,410 / 2,640
```

Thus unsafe counterfactual choices persist and grow throughout the extended root frontier.

```text
ROOT_SELECTOR_INDEPENDENCE = FALSIFIED
```

## 3. What this proves and does not prove

It proves that the deterministic selector is mathematically essential to the observed root safety. The local theorem cannot be replaced by a selector-free statement saying arbitrary branch contraction preserves or creates a shield.

It does **not** yet prove why the selected variable is safe for arbitrary `n`. The finite audit only establishes:

```text
selected variable unsafe count = 0 through GT_12;
many nonselected variables are unsafe.
```

## 4. Exact safe-template cover of selected choices

A separate root-template audit proves that all 62 selected root occurrences through `GT_12` instantiate exactly one of four already proved graph implications:

```text
CROSS_CUT       13  -> SPANNING_NONBRIDGE / SPANNING_NONBRIDGE
INTERNAL_HEAD   40  -> CANONICALLY_SHIELDED / CLAUSE_EXTINCT
INTERNAL_TAIL    3  -> TAIL_SINGLETON_SAFE / CLAUSE_EXTINCT
PIVOT            6  -> CLAUSE_EXTINCT / CLAUSE_EXTINCT
```

There is no fifth selected route.

The source-side pattern is also exact:

```text
CROSS_CUT       selected literal absent
INTERNAL_HEAD   selected literal present negative
INTERNAL_TAIL   selected literal present positive
PIVOT            selected literal present negative
```

Therefore the remaining root theorem is not to prove these implications again. It is to prove that the exact selector lands inside their union.

## 5. Correct theorem target

### Selected Safe-Template Reachability

For every arbitrary-`n` root immediate-local unshielded occurrence, let `s` be the minimum-index maximum-frequency Policy-0A branch variable. Prove that `s` satisfies at least one of:

```text
R1  s is the bad pivot;
R2  the s-edge crosses the bad bridge cut;
R3  the s-literal is present and merges the singleton head inside the head side;
R4  the s-literal is the unique internal edge of a two-node tail wing.
```

All four implications are already proved safe. Only selected-template reachability remains.

## 6. Lexicographic unsafe-set formulation

For a fixed root occurrence, let `U` be the set of branch variables for which at least one polarity produces an unsafe unshielded child. Let

```text
score(v) = (-frequency(v), v).
```

Because Policy-0A selects the minimum score, the exact equivalent target is:

```text
for every u in U,
score(selected) < score(u).
```

The next mechanical gate measures whether unsafe variables are excluded by:

```text
strictly lower frequency;
or equal maximum frequency but larger variable index.
```

It also records whether every maximum-frequency variable is safe or whether the minimum-index tie-break is genuinely needed against unsafe maxima.

## 7. Falsification conditions

Selected Safe-Template Reachability is falsified by any reachable root occurrence where:

1. the selected variable is unsafe under either polarity;
2. the selected variable lies outside R1–R4;
3. an unsafe variable has strictly greater frequency than the selected variable;
4. an unsafe variable ties the selected frequency and has smaller index;
5. a claimed safe template fails its proof-carrying fate replay.

The current finite gates search directly for conditions 1, 2, and 5 through `GT_12`. The unsafe-set selector-margin gate attacks conditions 3 and 4.

## Claim boundary

Selector independence is mechanically falsified by 3,404 unsafe counterfactual trials through `GT_12`, while the actual selected variable is safe in every tested occurrence and always lies in one of four proved templates. Selected Safe-Template Reachability for arbitrary `n`, Non-Root Wing Reachability for arbitrary `n`, T3, the global cache lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
