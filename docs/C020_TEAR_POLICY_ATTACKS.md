# C020 addendum — attacks on concrete JANUS Tear policies

## Status

`EXPLORATORY / PRE-ADMISSION / RESTRICTED POLICIES FALSIFIED`

The all-state continuation-complete Tear quotient is already false. This addendum
moves to narrower policies that might still look computationally useful.

The results below do not refute every possible policy-selected Tear algorithm.
They eliminate explicit restricted mechanisms and feed the fully specified
Policy-0A experiment.

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

A fixed small clause width is already incomplete on a tiny exact instance. The
C020 code records only the finite `K4` theorem and does not claim a new
asymptotic lower bound.

## Attack C — one fully specified combined policy

Policy-0A combines:

```text
visible affine root extraction
+ unit propagation
+ polynomially budgeted local resolution
+ deterministic branching
+ exact residual memoization
```

The visible odd-charge `K4` instance is rejected with zero branch states. Under
the local nonlinear edge encoding

```text
x = b XOR (a AND c),
```

the same global contradiction requires 3,842 residual states on masked `K4`.
The masked `K3,3` instance exceeds the explicit state promise `B(v)=4v^2` at
state 2,917.

```bash
python experiments/direct/janus_tear_policy0a_masked_tseitin.py --self-test
```

Read `docs/C020_POLICY0A_MASKED_TSEITIN.md` for the exact budgets and claim
boundary.

## Updated survivor

A surviving Tear policy must now avoid all of the following failures:

1. bounded locality;
2. finite structural marginals;
3. unit-propagation-enhanced marginals;
4. continuation-complete all-state quotienting;
5. fixed bounded-width resolution closure;
6. visible affine extraction under nonlinear masking;
7. the exact Policy-0A quadratic state envelope;
8. hiding the SAT decision problem inside Tear extraction or canonicalization.

The remaining target is not merely a compact data format. It is one fully
explicit transition algorithm whose total extraction, proof, state,
verification, normalization, and witness-recovery cost is polynomial on every
CNF.

Constructing and proving such an algorithm would itself establish `SAT in P`.
Failure to find a counterexample to an unspecified policy is not evidence of
that theorem.

## Next gate

The next experimentally meaningful step is asymptotic:

```text
fixed bounded-degree expander family
+ constant-overhead nonlinear mask
+ fully specified policy
+ lower bound on one charged resource
```

A sequence of larger finite timeouts is not enough. The laboratory now needs a
proof connecting graph expansion, masked representation, and the exact policy's
residual or proof complexity.
