# C024 — Branch-frequency history score

Status: **FORMALIZING**  
Scope: the selected-branch half of the pre-frontier temporal handoff theorem for exact Policy-0A on `GT_n`.

## 1. Why a component-only selector theorem is false

Policy-0A selects the minimum-index variable among those with maximum absolute-literal occurrence frequency in the current post-result CNF.

A tempting quotient theorem was:

> all comparison variables joining the same unordered pair of current relation components have the same frequency.

The exact pre-frontier audit through `GT_8` falsifies this strongly:

```text
branch states                               604
component-pair groups                     1,851
uniform groups                              718
nonuniform groups                         1,133

selected component pair uniform             141
selected component pair nonuniform           463
```

Thus the selector does not factor through component sizes or through the unordered component pair. Clause history, polarity, and original vertex identity survive quotienting and materially affect the selected variable.

The earlier count `42` refers to dangerous lineage occurrences. Those occurrences occupy only `16` unique parent states. Conflating those populations was a finite self-test bug; it did not rescue component factorization.

```text
DANGEROUS_LINEAGE_OCCURRENCES = 42
DANGEROUS_UNIQUE_PARENT_STATES = 16
COMPONENT_PAIR_FREQUENCY_FACTORIZATION = FALSIFIED
```

## 2. Exact surviving selector behaviour

For all 42 immediate-local dangerous lineages that later reach a parent-eligible exact key:

```text
selected variable has global maximum frequency          42
selected variable is minimum-index maximum              42
selected branch complement occurs in source clause      42
selected branch touches dangerous tail                   0
selected branch joins dangerous head                    39
selected branch is disjoint after shield active          3
```

Tail exclusion splits into two mechanisms:

```text
strict selected-versus-tail frequency advantage         23
equal maximum frequency                                 19
minimum-index tie-break excludes tail                   19
```

A valid arbitrary-`n` proof must explain both the frequency advantage and the index ordering. A strict frequency-gap theorem is false.

## 3. Clause-level score decomposition

Fix one surviving dangerous lineage with singleton tail component `A`, source clause `C`, selected branch variable `s`, and strongest tail-touching competitor `t`.

For every parent post-result clause `D`, define

```text
contribution(D;s,t)
    =  1  if D contains s but not t,
    = -1  if D contains t but not s,
    =  0  otherwise.
```

Then exactly

```text
frequency(s) - frequency(t)
    = sum_D contribution(D;s,t).
```

The mechanical profile classifies each `D` by its immediate historical source:

```text
ROOT_NON_MINIMALITY
ROOT_TRANSITIVITY
LOCAL_RESOLVENT
INHERITED_DERIVED
OTHER_DERIVED
```

This is an accounting identity, not yet a theorem that any particular source class is nonnegative.

## 4. Correct next theorem target

### History-Sensitive Lexicographic Tail-Exclusion Lemma

For every pre-frontier immediate-local dangerous lineage that can survive toward a later exact key, let `s` be the Policy-0A selected variable and let `T` be the set of variables whose comparison edge touches the dangerous singleton tail. Prove

```text
for every t in T,
(-frequency(s), s) < (-frequency(t), t).
```

The proof must be allowed to use:

1. the exact source-clause polarity containing the complement of the selected branch;
2. direct residuals of root non-minimality and transitivity clauses;
3. inherited/local derived-clause contributions;
4. original comparison-variable indices;
5. the frozen one-pass restriction that prevents fresh recursive reuse.

It may not replace these data by component sizes alone.

## 5. Connection to cut-or-shield

If the lemma holds, the selected branch cannot merge the dangerous singleton tail. Therefore:

```text
singleton head -> selected branch merges the head -> canonical N_a shield activates;
merged head    -> disjoint branch may preserve the already active shield.
```

Combined with the proved branch-route classification, this blocks both:

```text
Route A: transmission of an inherited same-cut pair;
Route B: birth of two complementary same-cut bridge exposures.
```

That would close T2b and leave only the mechanical T3 exact-key induction.

## 6. Falsification conditions

The history-score route fails if any arbitrary-`n` reachable pre-frontier lineage has one of the following:

1. a tail-touching variable with strictly greater frequency than the selected candidate predicted by the lineage template;
2. an equal-frequency tail variable with smaller index than the selected variable;
3. a source clause whose selected-complement property does not survive the required transition;
4. a negative historical contribution not compensated by an identified positive source;
5. a selected branch that merges the dangerous tail before shielding or extinction.

The finite contribution profile searches directly for the first four conditions through `GT_8`; the existing handoff certificate searches for the fifth.

## Claim boundary

Quotient-component frequency factorization is mechanically falsified through `GT_8`. The exact history-sensitive score decomposition is constructive finite accounting. The arbitrary-`n` lexicographic tail-exclusion lemma, completed T2b/T3, global cache-frontier lower bound, and `P` versus `NP` remain open.
