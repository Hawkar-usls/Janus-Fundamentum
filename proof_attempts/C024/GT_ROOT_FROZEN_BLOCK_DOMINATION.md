# C024 — Root frozen-block domination

Status: **ASYMPTOTIC THEOREM PROVED / FINITE BASE GT_4..GT_47 PENDING CI ADMISSION**  
Scope: the exact canonical root `GT_n` CNF and the implemented frozen one-pass Resolution schedule of Policy-0A.

## 1. Root parent lists for one pivot

Fix a comparison variable

```text
p = x_{a,b}.
```

In the canonical root CNF, `p` occurs with each polarity in exactly:

```text
n-2 transitivity clauses;
1 non-minimality clause.
```

Thus the frozen positive and negative parent lists each have size `n-1`, and a complete pivot block makes exactly

```text
(n-1)^2
```

parent-pair attempts.

## 2. Accepted resolvents in a complete pivot block

### Transitivity/transitivity parents

Choose third vertices `c,d` outside `{a,b}`.

If `c=d`, the resolvent is tautological and is rejected. If `c!=d`, the resolvent is a fresh non-tautological width-four clause. Distinct ordered pairs `(c,d)` give distinct clauses.

Therefore:

```text
accepted T/T resolvents = (n-2)(n-3).
```

### Non-minimality/transitivity parents

The positive non-minimality parent resolves with one negative transitivity parent for every `c`, and symmetrically the negative non-minimality parent resolves with every positive transitivity parent. Each result is a fresh width-`n-1` subdivided-star clause.

Therefore:

```text
accepted N/T resolvents = 2(n-2).
```

### Non-minimality/non-minimality parents

The N/N resolvent is not accepted: it exceeds the root width limit or is otherwise rejected by the canonical clause checks. It contributes no fresh clause.

Hence a complete pivot block accepts exactly

```text
M(n)
  = (n-2)(n-3) + 2(n-2)
  = (n-1)(n-2)
```

fresh clauses.

```text
COMPLETE_ROOT_PIVOT_BLOCK_SIZE = (n-1)(n-2)
```

## 3. Variable-incidence theorem for one complete block

Every accepted parent and resolvent in the block mentions only comparison variables whose unordered edge is incident to `a` or `b`. No variable disjoint from `{a,b}` appears.

There are exactly

```text
2(n-2)
```

such nonpivot variables. Permutations fixing the unordered pivot endpoints act transitively on them and preserve the complete block. Hence every incident nonpivot variable has the same accepted-resolvent incidence.

The total literal incidence over the accepted block is

```text
4(n-2)(n-3) + (n-1) * 2(n-2)
  = 2(n-2)(3n-7).
```

Dividing by `2(n-2)` gives the exact per-variable fresh surplus

```text
S(n) = 3n-7.
```

### Complete Pivot-Block Incidence Theorem

For a fully processed root pivot `x_{a,b}`:

```text
fresh surplus of every nonpivot edge incident to a or b = 3n-7;
fresh surplus of every edge disjoint from {a,b}          = 0.
```

```text
COMPLETE_ROOT_PIVOT_BLOCK_INCIDENCE = PROVED
```

## 4. Number and shape of complete initial blocks

The root clause count is

```text
C(n) = n + 2*C(n,3).
```

For the asymptotic range, the exact addition budget is

```text
A(n) = floor(C(n)/4).
```

Since one complete block contributes `M(n)=(n-1)(n-2)` additions,

```text
floor(A(n)/M(n)) = floor(n/12).
```

Indeed,

```text
C(n) / (4M(n))
  = n/12 + n/[4(n-1)(n-2)],
```

and the correction is less than `1/12` for `n>=6`; the remaining small case is direct.

Let

```text
q = floor(n/12).
```

The first `q` comparison variables in the canonical pair numbering are

```text
(0,1), (0,2), ..., (0,q).
```

They form a star. Resolvents generated from distinct star pivots are distinct:

- T/T width-four clauses encode the pivot as one edge of the missing perfect matching; two star pivots share vertex `0` and cannot be the two disjoint missing edges of the same clause;
- N/T subdivided-star clauses retain a unique center/subdivision signature identifying their pivot block.

Therefore the first `q` blocks are fully accepted before the addition budget enters the partial block for pivot `(0,q+1)`.

The attempt budget cannot stop this prefix: processing `q+1` complete parent-pair blocks needs at most

```text
(q+1)(n-1)^2
```

attempts, while the implemented root attempt budget is

```text
4n(n-1)^2.
```

Thus the addition budget is the active stopping mechanism.

```text
INITIAL_COMPLETE_ROOT_BLOCKS = floor(n/12)
```

## 5. Root unsafe class

Every root component-spanning fresh non-tail bridge occurrence for `n>=6` comes from an accepted N/T subdivided-star clause: a width-four T/T clause cannot span `n` quotient vertices.

Its bad bridge cuts the tree into

```text
2 | (n-2)
```

quotient vertices. The exact unsafe set consists of clause-absent comparisons internal to the large side and disjoint from its distinguished bad head. In particular, every unsafe edge is disjoint from vertex `0` and from the two-node wing endpoint supplied by the producing star pivot.

This semantic characterization is proved conditionally by the root unsafe-set graph lemma and mechanically certified through `GT_12`.

## 6. Asymptotic domination for n>=48

Assume `n>=48`. Then

```text
q = floor(n/12) >= 4.
```

Let `S=3n-7`.

Choose an unprocessed star edge

```text
e = (0,k)
```

whose leaf `k` is outside the finitely many producing-wing and partial-pivot labels. Such a choice exists because `q<n-1` with large slack.

The edge `e` is incident to every one of the `q` complete star pivots and is not itself a processed pivot. By the complete block incidence theorem,

```text
fresh_surplus(e) >= qS.
```

Now let `u` be any unsafe edge. Because `u` is disjoint from vertex `0`, it is incident to at most two of the `q` complete star pivot leaves. Hence complete blocks contribute at most

```text
2S
```

to `u`.

The final partial pivot block is a prefix of one complete block. No variable can occur in that prefix more often than in the complete block, so it contributes at most another `S` to `u`.

Therefore

```text
fresh_surplus(u) <= 3S.
```

Since `q>=4`,

```text
fresh_surplus(e) >= qS > 3S >= fresh_surplus(u).
```

The Policy-0A selected variable has maximum post-result frequency, and the uniform root baseline is common to every variable. Thus

```text
fresh_surplus(selected)
  >= fresh_surplus(e)
  > fresh_surplus(u)
```

for every unsafe `u`.

### Asymptotic Root Unsafe-Surplus Separation

For every `n>=48`, the exact selected root variable has strictly greater fresh frozen-pass surplus than every geometric unsafe alternative.

```text
ROOT_UNSAFE_SURPLUS_SEPARATION_N_GE_48 = PROVED
```

Minimum-index tie-breaking is irrelevant to this exclusion.

## 7. Finite base

The remaining orders are exactly

```text
GT_4, GT_5, ..., GT_47.
```

The optimized finite-base checker:

```text
experiments/direct/janus_tear_gt_root_surplus_gap_finite_base.py
```

replays the exact root pass, reconstructs every fresh component-spanning non-tail bridge, builds its geometric unsafe class, and requires a strict selected fresh-surplus advantage.

The checker is designed to certify:

```text
FINITE_ROOT_SURPLUS_GAP_GT_4_TO_GT_47 = PASS.
```

Independent GitHub Actions admission is pending. Until that gate is green, the combined arbitrary-`n` root theorem is not promoted from candidate to admitted.

## 8. Consequence after finite admission

Once the finite base passes independently, the finite gate plus the `n>=48` proof yield

```text
FROZEN_UNSAFE_SURPLUS_SEPARATION = PROVED_ARBITRARY_N.
```

Combined with the unsafe-set characterization and the four root graph implications, this closes the root half of T2b.

The only remaining local reachability theorem would then be Non-Root Wing Reachability.

## Claim boundary

The complete pivot-block size/incidence theorem, exact initial-block count, and `n>=48` unsafe-surplus domination are proved. The `GT_4..GT_47` finite base is implemented but awaits independent CI admission. Non-Root Wing Reachability, T3, the global cache lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
