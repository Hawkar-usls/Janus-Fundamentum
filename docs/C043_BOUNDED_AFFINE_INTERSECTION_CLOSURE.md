# C043 — Bounded Affine Intersection-Support Compiler

```text
P_VS_NP=OPEN
```

## Exact coordinate object

After an affine parameterization

```text
x_i = p_i XOR <b_i, lambda>,
```

the simultaneous falsification of one CNF clause is an affine subspace
`U_C` of `GF(2)^d`, or the empty set. The coordinate formula is satisfiable
exactly when

```text
GF(2)^d \ union_C U_C
```

is nonempty.

C042 solved the laminar case, where every two nonempty `U_C` are disjoint
or nested. C043 permits arbitrary crossings, provided the exact signed
intersection support generated below remains polynomially bounded.

## Constructive theorem

Process the forbidden subspaces in a deterministic order. Maintain a signed
indicator representation

```text
1_(union processed factors) = sum_S c_S 1_S,
```

where every `S` is a nonempty affine intersection of processed factors.

When a new factor `U` arrives, use

```text
1_(A union U) = 1_A + 1_U - 1_A 1_U
```

and

```text
1_S 1_U = 1_(S intersect U).
```

Therefore the updated coefficients are obtained only by affine intersection,
integer addition and cancellation. Equal intersections are merged by canonical
RREF.

If at every step the number of nonzero coefficient terms is at most `K`, then
the complete construction costs

```text
O(m K poly(d,L))
```

arithmetic and Gaussian-elimination work. Coefficient bit lengths are at most
linear in the number of processed factors.

For a fixed capability exponent `q`, C043 admits only instances satisfying

```text
K <= L^q,
```

with an additional absolute safety cap. Exceeding the cap returns
`OPEN_INTERSECTION_CLOSURE`; the exponent is not supplied by the input.

## Exact counting and certificates

The union cardinality is

```text
|union_C U_C| = sum_S c_S 2^dim(S).
```

- Equality with `2^d` gives an exact signed-intersection UNSAT cover.
- Otherwise C043 constructs a SAT coordinate bit by bit. For each candidate
  prefix cell `P`, it computes

```text
|P intersect union_C U_C|
  = sum_S c_S |P intersect S|
```

by affine intersection and rank. It chooses a child whose covered count is
strictly smaller than the child-cell size.

The final coordinate is outside every forbidden subspace and therefore lifts
to a satisfying assignment.

The verifier reruns the deterministic construction, all intersections,
coefficient cancellations, counts and witness choices. A digest alone is not
accepted as proof.

## Strict extension beyond C042

Two crossing coordinate hyperplanes in dimension 64 are non-laminar, but their
signed support contains only

```text
U
V
U intersect V
```

and C043 solves them without enumerating `2^64` coordinates.

Four crossing codimension-two cells covering all assignments of the first two
coordinates yield a 64-dimensional UNSAT certificate through the same signed
intersection calculation.

Thus:

```text
laminar arrangements  subset  bounded signed-intersection-support arrangements.
```

The inclusion is strict.

## Frozen audit

```bash
python experiments/direct/janus_c043_bounded_affine_intersection_closure.py --self-test
```

The deterministic audit includes:

```text
300 random coordinate CNFs on d <= 8
0 SAT/UNSAT mismatches
0 replay-verification failures
64-dimensional crossing SAT control with 3 coefficient terms
64-dimensional crossing UNSAT cover with 4 input factors
200 repeated crossing factors compressed to 3 terms
24-variable NAND3+NEQ pressure -> OPEN_INTERSECTION_CLOSURE
explicit closure-budget exhaustion
corrupt certificate -> rejected
```

Finite exhaustive checks validate the implementation. The universal theorem
follows from the signed indicator identity and exact affine-intersection
arithmetic.

## Literature alignment

Intersection-poset and characteristic-polynomial methods for counting points on
or off finite-field subspace arrangements are classical. C043 is a
proof-carrying algorithmic specialization: it charges deterministic construction
of the nonzero signed intersection support and accepts only when that support
remains within one fixed polynomial capability. It is not named as a new
general arrangement invariant.

## Decisive boundary

The C023/C041 hard image exceeds the fixed polynomial support budget on the
registered pressure family and returns:

```text
OPEN_INTERSECTION_CLOSURE
```

C043 does not claim that every arrangement has polynomial intersection support.
It does not solve arbitrary 3-CNF, unrestricted Horn-affine composition, or
P versus NP.

The surviving gate is:

```text
POLYNOMIAL_DECOMPOSITION_BEYOND_BOUNDED_INTERSECTION_SUPPORT
```

A next route must discover a decomposition, vtree, bounded Möbius-support
factorization, or richer symbolic cover whose construction, joins, projections,
witness recovery and UNSAT evidence remain polynomial even when global
intersection support is exponential.
