# C042 — Proof-Carrying Bounded Signed-Intersection Support

```text
P_VS_NP=OPEN
```

## Exact coordinate object

C041 parameterizes the affine side as

```text
x = p + B lambda
```

and translates every CNF clause `C` into its affine falsifying set

```text
U_C = { lambda : C(p+B lambda) is false }.
```

Thus

```text
F AND A is SAT  iff  GF(2)^d \\ UNION_C U_C is nonempty.
```

C041 solved laminar families. C042 permits genuine crossings.

## Signed-intersection representation

Process the nonempty forbidden subspaces in deterministic clause order and
maintain the exact indicator identity

```text
1_(UNION processed U) = SUM_S c_S 1_S,
```

where every `S` is a canonical nonempty affine intersection and every `c_S`
is an integer.

For a new factor `U`:

```text
1_(A UNION U) = 1_A + 1_U - 1_A 1_U
1_S 1_U       = 1_(S INTERSECT U).
```

Therefore one update needs only canonical affine intersection by Gaussian
elimination, integer coefficient addition, equality merging by canonical RREF,
and deletion of zero coefficients.

The algorithm does not require the full powerset of factors or all `2^d`
coordinate points. It retains only the current nonzero signed support.

## Constructive theorem

Let `K` be the largest number of nonzero signed terms present after any update.
If, under one fixed capability profile,

```text
K <= L^q,
```

and the charged work and certificate volumes remain within fixed polynomial
budgets, then C042 decides the affine-coordinate CNF in

```text
O(m K poly(d,L))
```

total work.

The exponents are fixed by the capability, never supplied by the instance.
Exceeding any bound returns an exact `OPEN_*` refusal.

Every coefficient is a signed sum of contributions from subsets of at most `m`
factors. Hence

```text
bit_length(c_S) <= m + 1.
```

C042 records the maximum and total coefficient bit lengths, the maximum support,
a transient-support bound, intersection calls and work units.

## Exact SAT and UNSAT handling

For an affine subspace `S` in `GF(2)^d`:

```text
|S| = 2^dim(S).
```

Therefore

```text
|UNION_C U_C| = SUM_S c_S 2^dim(S).
```

If the sum equals `2^d`, C042 emits an exact signed-intersection UNSAT cover.

Otherwise it recovers a SAT coordinate without enumeration. For each next bit
`lambda_i`, it tests the two prefix cells. The covered part of a cell `P` is

```text
|P INTERSECT UNION_C U_C|
  = SUM_S c_S |P INTERSECT S|.
```

At least one child has covered size strictly below its cell size. Repeating this
for all coordinates yields a point outside every forbidden subspace, which is
lifted through `x=p+B lambda` to a complete witness.

## Budget-bound verifier

The legacy arithmetic core is enclosed by a canonical C042 certificate envelope.
The envelope commits to and replays:

```text
closure exponent and absolute cap
work exponent and absolute cap
certificate exponent and absolute cap
all effective limits
coefficient-volume accounting
core result and schema
full integrity digest
```

This closes a verifier gap in the first experimental draft: an
`OPEN_WORK_BUDGET` or `OPEN_CERTIFICATE_VOLUME` result cannot be replayed under
a larger unrecorded budget.

## Strict extension of C041

Two crossing hyperplanes in dimension 64 have the exact support

```text
U, V, U INTERSECT V
```

and are solved with three terms, although they are non-laminar.

Four crossing codimension-two cells that cover all assignments of the first two
coordinates give a 64-dimensional UNSAT certificate without enumerating `2^64`
points.

Two hundred repeated crossing factors cancel back to at most three signed terms.
Thus input factor count and raw intersection multiplicity need not equal retained
semantic cover volume.

## Frozen acceptance audit

The deterministic audit includes:

```text
300 random coordinate CNFs on d <= 8
exact comparison with exhaustive truth tables
64-dimensional crossing SAT
64-dimensional crossing UNSAT cover
200 repeated crossing factors
24-variable NAND3+NEQ pressure
closure, work and certificate budget refusals
corrupt certificate rejection
corrupt budget rejection
```

Finite tests validate the implementation. The universal restricted theorem comes
from the signed-indicator identity, exact affine intersection, and the fixed
polynomial capability accounting.

## Hard-image boundary

The registered NAND3+NEQ pressure family exceeds the signed-support capability and
returns

```text
OPEN_INTERSECTION_CLOSURE.
```

This is a refusal of this representation, not a hardness theorem. It does not
show that every ordering, decomposition, vtree or richer cover has exponential
volume.

## Literature alignment

CNF satisfiability inside a prescribed affine subspace is equivalent to avoiding
a union of affine subspaces. Counting points on or off finite-field subspace
arrangements through intersection data and characteristic-polynomial methods is
classical. C042 is a charged algorithmic specialization that constructs one
exact signed support and accepts only while its complete discovery and proof
volume remain polynomial.

It is an alignment and restricted construction, not a new universal arrangement
width.

## Surviving gate

```text
POLYNOMIAL_DECOMPOSITION_BEYOND_BOUNDED_SIGNED_INTERSECTION_SUPPORT
```

The next route must discover a decomposition, vtree, local Möbius factorization,
or richer proof-carrying cover when the global signed support exceeds every fixed
polynomial budget.

C042 does not decide arbitrary 3-CNF, unrestricted Horn-affine composition, or P
versus NP.
