# C020 addendum — strong 2-SAT backdoor Tears

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT CANONICAL`

This addendum tests one concrete surviving JANUS Tear policy on ordinary 3-CNF.

## Definition

A set of variables `B` is a **strong 2-SAT backdoor** when every assignment to
`B` simplifies the remaining formula to 2-CNF or to an immediate empty-clause
contradiction.

A complete solver can then:

1. enumerate the `2^|B|` assignments to `B`;
2. solve each residual by implication-graph SCC;
3. return a SAT witness when one branch succeeds;
4. otherwise retain one SCC contradiction Tear per branch.

For a supplied backdoor of size `k`, total work is

```text
O(2^k poly(L)).
```

Therefore an efficiently discovered `k=O(log L)` backdoor would yield a
polynomial-time algorithm for that input family.

## Positive non-XOR 3-CNF family

The audit builds arbitrarily large formulas from blocks

```text
(z ∨ a_i ∨ b_i)
(¬z ∨ c_i ∨ d_i)
```

plus binary equivalence-like constraints between the block variables.

The formula is genuine 3-CNF and is not treated as an XOR system. The single
selector variable `z` is a strong 2-SAT backdoor:

```text
z=0 -> every remaining clause has width at most 2
z=1 -> every remaining clause has width at most 2.
```

For every tested size, the exact minimum backdoor is one variable and the
solver needs at most two polynomial branches.

This is the first C020 positive compression experiment directly on 3-CNF
syntax outside the Tseitin/XOR and native 2-SAT families.

## Negative control — a large backdoor can occur on an easy formula

Consider `m` disjoint positive clauses:

```text
(a_i ∨ b_i ∨ c_i),  i=1,...,m.
```

The formula is trivially satisfiable by setting every variable true. However, a
strong 2-SAT backdoor must hit every disjoint 3-clause. Hence

```text
minimum backdoor size = m.
```

Choosing one variable from every clause is sufficient, so the lower bound is
exact.

Thus a fixed 2-SAT-backdoor policy may require `2^m` branches even on a formula
that another representation solves immediately.

## What this changes

The surviving route cannot be only

```text
find a logarithmic backdoor to 2-SAT.
```

It must instead be

```text
choose or synthesize the right tractable language
+ find a small backdoor or direct certificate to that language
+ verify the translation
+ charge language-selection and backdoor-search work
+ preserve SAT witness recovery.
```

This joins the three C020 sensitivity results:

```text
order sensitivity          equality family
module sensitivity         connected Tseitin lobes
language sensitivity       torus affine proof and disjoint positive 3-clauses
```

## Exact tests

The executable checks:

- guarded 3-CNF blocks `1..10`: exact minimum strong 2-SAT backdoor `1`;
- disjoint positive 3-clauses `1..5`: exact minimum backdoor equals clause count;
- SAT witness reconstruction through the selected branch;
- SCC contradiction Tears on rejected branches;
- 60 deterministic random CNFs with up to seven variables against exhaustive
  truth-table evaluation.

```text
random seed   9379992
agreement     60/60
```

## Reproduction

```bash
python experiments/direct/janus_tear_backdoor_policy.py --self-test
python experiments/direct/janus_tear_backdoor_policy.py --guarded-blocks 32
python experiments/direct/janus_tear_backdoor_policy.py --disjoint-blocks 5
python experiments/direct/janus_tear_backdoor_policy.py --json
```

## Claim boundary

This is an exact parameterized SAT algorithm for formulas with a supplied or
found strong 2-SAT backdoor. It does not establish that arbitrary CNF has a
small backdoor, that a useful target language can always be selected in
polynomial time, or that `P=NP`.
