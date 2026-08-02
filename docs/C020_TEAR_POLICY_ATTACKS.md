# C020 addendum — attacks on concrete JANUS Tear policies

## Status

`EXPLORATORY / PRE-ADMISSION / TWO ADDITIONAL RESTRICTED POLICIES FALSIFIED`

The all-state continuation-complete Tear quotient is already false. This addendum
moves to narrower policies that might still look computationally useful.

The results below do not refute every possible policy-selected Tear algorithm.
They eliminate two explicit restricted mechanisms.

## Attack A — unit-propagation-enhanced marginal Tears

A natural candidate signature combines:

- exact unsigned clause-scope multiplicities;
- clause-width and clause-sign profiles;
- labelled positive/negative variable occurrence counts;
- the exact primal graph and component sizes;
- recognized binary equality/inequality gadgets;
- the result and residual size profile of exhaustive unit propagation.

C020 contains an exact collision on four variables. Both formulas contain ten
ternary clauses and no unit clause.

```text
UNSAT:
  (-2,-3,-4) (-2, 3,-4) (-1,-3,-4) (-1,-2, 4) (-1, 3,-4)
  ( 1,-2,-4) ( 1,-2, 4) ( 1, 2,-4) ( 2,-3, 4) ( 2, 3, 4)

SAT:
  (-2,-3,-4) (-2, 3, 4) (-1,-2,-4) (-1,-2, 4) (-1, 2,-4)
  ( 1,-2,-4) ( 1, 3,-4) ( 1, 3, 4) ( 2,-3,-4) ( 2,-3, 4)
```

The SAT formula has exactly two witnesses:

```text
(0,1,1,0)
(1,0,0,0)
```

The UNSAT formula has none. Exhaustive unit propagation returns the same result
on both:

```text
status:       OPEN
assignments:  none
residual:     ten width-three clauses
```

Every listed Tear field is equal.

```bash
python experiments/direct/janus_tear_unit_propagation_collision.py
```

### Result

Adding unit propagation to a rich finite marginal signature does not make the
signature SAT-complete. The attack does not exclude deeper lookahead, arbitrary
resolution, semantic canonicalization, or another explicitly defined policy.

## Attack B — bounded-width clause Tears

Suppose Tears are sound learned clauses and a policy saturates all resolution
consequences up to a fixed width. This is a precise and independently checkable
mechanism.

The executable audit builds the odd-charge Tseitin contradiction on `K4`:

```text
vertices:       4
edge variables: 6
axiom clauses:  16
axiom width:    3
```

Exact saturation gives:

```text
maximum width 3:
  closure clauses: 16
  empty clause:    absent

maximum width 4:
  closure clauses: 473
  empty clause:    present
```

Hence this instance has minimum resolution refutation width four. A policy that
stores every possible width-three clause still cannot reject it.

```bash
python experiments/direct/janus_tear_resolution_width_audit.py --self-test
```

### Result

A fixed small clause width is already incomplete on a tiny exact instance.
For asymptotic families, resolution width is a known proof-complexity resource;
the C020 code records only the finite `K4` theorem and does not claim a new
asymptotic lower bound.

Relevant primary references:

- E. Ben-Sasson and A. Wigderson, *Short Proofs Are Narrow—Resolution Made
  Simple*, JACM 48(2), 2001, DOI `10.1145/375827.375835`.
- A. Atserias and V. Dalmau, *A Combinatorial Characterization of Resolution
  Width*, JCSS 74(3), 2008, DOI `10.1016/j.jcss.2007.06.025`.

## Updated survivor

A surviving Tear policy must now avoid all of the following failures:

1. bounded locality;
2. finite structural marginals;
3. unit-propagation-enhanced marginals;
4. continuation-complete all-state quotienting;
5. fixed bounded-width resolution closure;
6. hiding the SAT decision problem inside Tear extraction or canonicalization.

The remaining target is therefore not merely a compact data format. It is one
fully explicit transition algorithm whose total extraction, proof, state,
verification, and witness-recovery cost is polynomial on every CNF.

Constructing and proving such an algorithm would itself establish `SAT in P`.
Failure to find a counterexample to an unspecified policy is not evidence of
that theorem.

## Next gate

The next experimentally meaningful step is to select one concrete stronger
policy, for example:

```text
unit propagation
+ bounded-width resolution
+ recognized affine/XOR elimination
+ deterministic branching rule
```

and then search automatically for the smallest formula on which its visited
state count exceeds a chosen polynomial envelope or its Tear signature collides
across opposite SAT labels.
