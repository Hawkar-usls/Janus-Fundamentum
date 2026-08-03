# C024 — GT Novelty Robustness under Policy-0A Local Resolution

**Status:** raw cardinality witness falsified / historical target frontier finitely preserved through `GT_8` / asymptotic transfer lemma open.

## Target

C023 left one precise transfer problem:

```text
historical graph-tautology lower bound for basic Formula Caching
+ Policy-0A exact residual cache
+ deterministic one-pass local Resolution
--------------------------------------------------------------
? lower bound for JANUS-FC_local
```

A polynomial local-inference budget cannot be declared harmless merely because
it is polynomial. One derived clause may remove an exponentially large search
frontier. C024 therefore reconstructs the historical proof object on the exact
Policy-0A execution and attacks every possible finite collapse mechanism.

## Candidate 1 — critical-order cardinality

Every permutation of the `n` vertices defines a total-order assignment that
satisfies all transitivity clauses and violates exactly the non-minimality clause
of its minimum vertex. Hence there are `n!` critical orders.

At the root this witness survived through `n=8`:

- for `n=5..8`, one accepted resolvent damages at most `(n-1)!/2` orders;
- the complete root pass damages only the minimum-`0` class;
- at `GT_8`, `36,120 / 40,320` critical orders survive.

The residual form nevertheless fails. The exact state audit finds local passes
that destroy every entry-assignment-compatible critical order at:

```text
GT_4: 0 of 3 states
GT_5: 3 of 12 states
GT_6: 4 of 40 states
GT_7: 4 of 140 states
```

Thus

```text
witness mass = number of entry-assignment-compatible total orders
```

is false. This rejects the naive reconstruction, not the historical Formula-
Caching theorem.

## Historical object — novel component joins

The historical lower-bound proof does not count permutations. A branch on the
comparison `x_(i,j)` is **novel** when `i` and `j` lie in different connected
components of the current partial-order Hasse diagram. After `n-2` novel joins,
the proof obtains `2^(n-2)` distinct restrictions.

C024 overlays this definition on the exact Policy-0A trace. Terminal conflict
assignments are recorded as conflicts rather than incorrectly required to remain
acyclic partial orders.

The exact finite target frontier is:

```text
n       target n-2       required 2^(n-2)       observed restrictions
4           2                    4                        4
5           3                    8                        8
6           4                   16                       16
7           5                   32                       32
8           6                   64                       98
```

No early contradiction or cache hit bypasses this first frontier in the verified
range.

## Resource decomposition

A Hasse-component reduction can be caused by four different resources:

```text
1. explicit novel branch;
2. unit propagation in the child residual before cache lookup;
3. units exposed after the one-pass local Resolution stage;
4. reuse of a completed exact residual through Formula Caching.
```

The finite accounting through `GT_8` finds:

```text
n       pre-unit merges       post-local-R unit merges       novel branches
4              4                         0                         3
5              3                         4                         7
6              1                         1                        33
7              2                         2                        90
8              2                         3                       303
```

Every legitimate unit merge reduces exactly two components to one. Every such
merge has an independently replayed source clause. Every post-local merge is
sourced by an explicit resolvent in the current one-pass trace. The maximum
number of unit-induced component merges on any root-to-leaf path is one.

## Timing result — no stolen novel join

The strongest finite result of C024 is:

```text
for every n in {4,5,6,7,8},
unit-induced component merges before novelty level n-2 = 0.
```

All observed unit merges happen exactly after the execution has already reached
the historical target level. They close the final `2 -> 1` component gap and do
not replace any of the first `n-2` required binary novel joins.

At `GT_8`, the three post-local events all derive the comparison unit `(27)` for
vertices `(5,7)` by resolving `(22,27)` with `(-22,27)` on pivot `22`. The two
pre-unit events are residual units `(-2)` and `(-1)`.

## Exact-cache frontier collision result

For every first call reaching novelty level `n-2`, C024 records:

1. the historical transitive-closure restriction signature;
2. the canonical residual CNF used as the exact cache key after pre-units;
3. or the terminal pre-cache outcome when no key exists.

Results:

```text
n    frontier calls    distinct restrictions    exact keys    terminals    cross-restriction key collisions
4          4                    4                   0             4                         0
5          8                    8                   5             3                         0
6         16                   16                  15             1                         0
7         32                   32                  30             2                         0
8         98                   98                  96             2                         0
```

There are no target-frontier cache hits and no repeated exact key groups. Hence,
within the verified range, simplification and pre-unit propagation do not map two
different historical target restrictions to the same memoized residual.

## Finite preservation statement

For `GT_n`, `4 <= n <= 8`, the exact Policy-0A execution satisfies all of the
following:

1. it reaches at least `2^(n-2)` distinct historical restrictions;
2. no unit-induced component merge occurs before level `n-2`;
3. each unit merge has a replayed clause source;
4. each post-local merge has an explicit Resolution derivation;
5. exact residual normalization creates no cross-restriction collision on the
   first target frontier;
6. no cache hit occurs on that frontier.

This is a verified finite preservation layer, not an asymptotic theorem.

## Exact missing theorem

The remaining transfer gate is now narrower:

### Early-merge exclusion

For every `n`, before a path accumulates `n-2` novel component joins, neither
residual unit propagation nor Policy-0A's bounded one-pass local Resolution may
derive a comparison unit joining two current Hasse components.

### Frontier separation

The first `2^(n-2)` historical restrictions must remain distinct under the exact
canonical residual map used by Formula Caching, or any collisions must be paid by
a lower-bound-preserving proof charge.

### Early-conflict charge

A local Resolution contradiction before the target must not remove the complete
historical frontier with polynomial charged work.

If these statements are proved, the historical graph-tautology Formula-Caching
count can be transferred to `JANUS-FC_local`. If any statement is falsified by a
polynomial execution family, the GT route must be rejected.

## Artifacts

```text
diagnostics/C024_NOVEL_BRANCH_REPORT.json
diagnostics/C024_FRONTIER_PRESERVATION.json
experiments/direct/janus_tear_gt_critical_order_damage.py
experiments/direct/janus_tear_gt_residual_critical_damage.py
experiments/direct/janus_tear_gt_novel_branch_audit_v2.py
experiments/direct/janus_tear_gt_component_merge_accounting.py
experiments/direct/janus_tear_gt_component_merge_sources.py
experiments/direct/janus_tear_gt_unit_merge_timing.py
experiments/direct/janus_tear_gt_target_frontier_collision.py
```

## Claim boundary

C024 has finitely preserved the historical target frontier through `GT_8` and
falsified one naive witness reconstruction. It has not proved the preservation
lemmas for all `n`, has not transferred an asymptotic graph-tautology lower bound
to Policy-0A, and does not resolve P versus NP.
