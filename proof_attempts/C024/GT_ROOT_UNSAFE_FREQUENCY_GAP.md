# C024 — Root unsafe-frequency gap

Status: **FINITE_CERTIFIED_THROUGH_GT_12 / ARBITRARY_N_OPEN**  
Scope: immediate-local root unshielded component-spanning non-tail bridge occurrences.

## 1. Unsafe-set formulation

For a fixed root occurrence `(C,l)`, call a branch variable `u` **unsafe** if at least one polarity, after exact child unit closure, admits a child exact key containing the same tracked lineage as an unshielded non-tail bridge.

Let `s` be the exact Policy-0A selected variable and let

```text
freq(v) = number of occurrences of variable v in the root post-result CNF.
```

The exact all-variable audit proves that unsafe variables exist abundantly, so selector independence is false. The correct selector theorem is to separate `s` from the unsafe set.

## 2. Exact finite result through GT_12

```text
root unshielded occurrences                   62
occurrences with unsafe variables             58
occurrences with no unsafe variable             4
unsafe variable-occurrence pairs            1,397
```

Every unsafe variable has the same structural form:

```text
geometry relative to bad bridge cut     INTERNAL_HEAD
occurrence in tracked clause            ABSENT
```

No unsafe variable belongs to `PIVOT`, `CROSS_CUT`, or the selected-literal endpoint templates.

The exact selector separation is stronger than lexicographic tie exclusion:

```text
unsafe excluded by strict frequency            58
unsafe excluded only by minimum index            0
unsafe variable at selected frequency            0
```

Therefore, for every tested occurrence and every unsafe variable `u`,

```text
freq(s) > freq(u).
```

The four `GT_4` occurrences have an empty unsafe set, so the statement is vacuous there.

## 3. Exact gap profile

Let

```text
gap(C,l) = freq(s) - max_{u unsafe for (C,l)} freq(u).
```

For the 58 nonvacuous occurrences:

```text
gap  6   7  10  14  18  21  26  31  32
count 2   2   3   5   6   7  13  18   2
```

Unsafe-set sizes:

```text
size  0  1  3  6  10  15  21  28  36
count 4  2  2  3   5   6   7  13  20
```

The large positive margins show that the finite mechanism is not a fragile index tie.

## 4. Selected safe-template cover

The selected variable always lies in one of four proved safe templates:

```text
CROSS_CUT       13
INTERNAL_HEAD   40  with selected literal present negative
INTERNAL_TAIL    3  with selected literal present positive
PIVOT            6
```

By contrast, every unsafe variable is `INTERNAL_HEAD` but absent from the tracked clause. Hence a sufficient arbitrary-`n` statement is:

### Root Unsafe-Frequency-Gap Theorem

For every root immediate-local unshielded occurrence `(C,l)`, every internal-head variable absent from `C` that would preserve `(C,l)` as an unsafe child lineage has strictly smaller post-result frequency than at least one safe-template variable.

Since Policy-0A selects a maximum-frequency variable, the selected variable is safe-template eligible.

## 5. Root baseline versus fresh surplus

The root GT CNF is permutation-symmetric before the deterministic frozen Resolution pass. This suggests decomposing

```text
freq(v) = root_base(v) + fresh_surplus(v),
```

where:

```text
root_base(v)    counts occurrences in the exact root key;
fresh_surplus(v) counts occurrences in newly added frozen-pass resolvents.
```

If `root_base(v)` is constant over all comparison variables, every unsafe frequency gap is entirely a fresh-resolvent surplus inequality:

```text
fresh_surplus(s) > fresh_surplus(u).
```

The next certificate checks this decomposition and records the deterministic resolution-event schedule responsible for the surplus.

## 6. Remaining proof target

A full proof may proceed in two steps:

1. **Uniform Root Baseline:** prove by GT symmetry/counting that every comparison variable has equal frequency in the root CNF.
2. **Frozen Surplus Separation:** prove from the exact lexicographic pivot/parent enumeration and finite attempt/addition budgets that every unsafe absent internal-head variable receives strictly less fresh-resolvent surplus than the selected safe-template maximum.

The first step is expected to be elementary. The second is solver-policy specific and must account for the exact frozen pass rather than an idealized saturation.

## 7. Falsification conditions

The theorem route is falsified by any arbitrary-`n` root execution containing:

1. an unsafe variable with frequency at least the selected frequency;
2. an unsafe variable outside the absent `INTERNAL_HEAD` class;
3. a nonuniform root baseline not captured by a corrected exact formula;
4. a fresh-resolvent surplus tie requiring index order against an unsafe variable;
5. a selected maximum variable outside the four proved safe templates.

## Claim boundary

Strict unsafe-frequency exclusion is mechanically certified for all 1,397 unsafe variable-occurrence pairs through `GT_12`. The arbitrary-`n` root baseline/surplus theorem, Non-Root Wing Reachability, T3, the global cache lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
