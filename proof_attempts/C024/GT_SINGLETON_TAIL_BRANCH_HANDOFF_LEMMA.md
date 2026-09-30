# C024 — Singleton-tail branch-handoff lemma

Status: **FORMALIZING**  
Scope: fresh local non-tail bridge lineages that survive into a later parent-eligible pre-frontier exact key of deterministic Policy-0A on `GT_n`.

## 1. Exact branch rule

After the local Resolution pass and post-unit propagation, Policy-0A chooses the branch variable by

```text
maximum number of literal occurrences in the residual CNF;
minimum variable index among variables tied for that maximum.
```

Equivalently, it minimizes the lexicographic key

```text
(-frequency(variable), variable_index).
```

Therefore a proof that the selected branch avoids a bad singleton tail must allow two mechanisms:

1. every tail-touching variable has strictly smaller frequency; or
2. a tail-touching variable ties for maximum but has larger variable index than the selected maximum-frequency variable.

A strict frequency inequality alone is false on the finite surviving family.

## 2. Finite exact certificate through GT_8

There are 42 immediate-local bad-resolvent lineages that survive into a later exact key.  In all 42, the selected variable is the first variable in the sorted maximum-frequency set.

```text
surviving lineages                          42
selected minimum-index maximum              42
selected complement occurs in source clause 42
```

Tail exclusion splits exactly as follows:

```text
strict frequency gap excludes tail          23
tail variable also reaches maximum           19
tail excluded by minimum-index tie-break     19
```

The observed tail-frequency gaps are:

```text
gap 0   1   2   3   7   8   15
     19  5   5   1   4   5    3
```

Thus every surviving tail is excluded by the exact lexicographic branch rule, but not always by frequency alone.

## 3. Relation of the selected comparison to the bad endpoints

```text
HEAD_TO_OTHER                               39
DISJOINT                                     3
TAIL_TO_OTHER                                0
TAIL_HEAD                                    0
```

In all 39 `HEAD_TO_OTHER` cases, a head-touching variable attains the global maximum.  The branch joins the current bad head component to another singleton component, increasing head size by one while leaving the singleton tail untouched.

In the three `DISJOINT` cases, no head-touching variable reaches the global maximum: the head gap is seven.  The head component is already non-singleton, so the canonical root shield is active before the branch; the disjoint branch preserves it.

The head-frequency gap histogram is:

```text
head gap 0: 39
head gap 7:  3
```

## 4. Maximum-frequency candidate structure

The maximum-frequency set sizes are:

```text
1 candidate: 15 lineages
2 candidates: 8
3 candidates: 12
4 candidates: 3
5 candidates: 4
```

The relation classes represented among maximum-frequency variables are:

```text
{HEAD_TO_OTHER}                         20
{HEAD_TO_OTHER, TAIL_HEAD}              18
{HEAD_TO_OTHER, TAIL_TO_OTHER}           1
{DISJOINT}                               3
```

Thus in the 19 tie cases the tail-touching competitor is present at maximum frequency, but the selected head-side variable has the smaller index.  The proof must preserve this polarity/index relationship; counting occurrences without variable labels is insufficient.

## 5. Open arbitrary-n lemma

### Lexicographic Tail-Exclusion Lemma

Let a fresh local non-tail bridge `l : a -> b` have singleton tail component `{a}` and survive toward a later exact key.  In the parent post-result CNF, let `T` be the set of variables whose comparison edge touches `{a}`.  Let `s` be the Policy-0A selected variable.

Prove:

```text
for every t in T,
(-freq(s), s) < (-freq(t), t),
```

and additionally:

```text
if component(b) is singleton,
s joins component(b) to another component;
otherwise s may be disjoint, but the root shield is already active.
```

The finite data show that the selected literal is always the complement of exactly one literal in the surviving source clause.  Any proof should exploit both:

- the GT root-clause frequency contribution around the untouched tail vertex;
- the local-resolvent/source-clause structure that raises a head-side variable to the maximum and gives it lower index in tie cases.

## 6. Consequence

The Lexicographic Tail-Exclusion Lemma proves the singleton-tail half of the Temporal Root-Shield Lemma:

```text
surviving singleton-tail bad resolvent
    -> branch cannot merge tail
    -> singleton head is merged, or head already merged
    -> untouched N_a supplies parallel complementary edge
    -> lineage is shielded before becoming parent-eligible.
```

It must be combined with the separate merged-tail unit-conflict lemma, which explains why fresh non-tail occurrences with non-singleton tails never reach a later exact key.

## Claim boundary

The exact lexicographic mechanism is exhaustively certified for all 42 surviving immediate-local lineages through `GT_8`.  The arbitrary-`n` frequency/index inequality, merged-tail conflict theorem, global Formula-Caching lower-bound transfer, and `P` versus `NP` remain open.
