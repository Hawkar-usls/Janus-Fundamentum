# R5 E10A — Boundary Metric Closure and Exact Delta/Y Compilation

Date: 2026-09-25

Authority:
`JANUS_DERIVED_EXACT_BOUNDARY_METRIC_CLOSURE_AFTER_PA0011__NO_END_TO_END_P_EQ_NP_CLAIM`

Authorizing audit:
`PA-0011-MIXED-DELTA-Y-CONDITIONED-COST-TABLE-TO-TWO-ROW-OBJECTIVE`

Parent gate:
`R5_E10A_BOUNDARY_METRIC_CLOSURE_GATE_V1`

Checker:
`experiments/r5_e10a_boundary_metric_closure.py`

## 1. Source correction frozen first

Kashyap Appendix B / Lemma B.1(b) is attached to the dual/bar-3 operation
used in Definition 6.1, i.e. the Y-sum branch, not ordinary Delta-3.

Therefore the two 3-interface compilers must be different:

```
Y/bar3:
primal traces are the even-parity subspace
{000,011,101,110}.

Delta3:
primal traces are all GF(2)^3,
but traces t and t+111 represent the same real behavior
after deletion of the shared triangle.
```

Copying the Y half-sum coefficients onto Delta is false in general.

## 2. Root boundary table of an absorbed subtree

Let `S` be any nondistinguished absorbed subtree whose internal real elements
have nonnegative rational weights.

Let the root interface state group be:

```
G = GF(2)                    for a 2-sum,
G ~= GF(2)^2                 for Delta3 or Y3.
```

For `g in G`, define

```
d_S(g)
=
minimum total weight of an internal binary cycle/codeword
having root boundary state g.
```

The root virtual coordinates themselves are not included in this internal
cost.

Because the zero codeword is feasible and all internal weights are
nonnegative,

```
d_S(0)=0,
d_S(g)>=0.
```

If `X` and `Y` are minimum witnesses for states `x` and `y`, their
binary symmetric difference is feasible for state `x+y`, and

```
w(X triangle Y) <= w(X)+w(Y).
```

Hence

```
d_S(x+y) <= d_S(x)+d_S(y).
```

Thus every absorbed subtree exports a normalized nonnegative subadditive
function on its root boundary group.

For the four-state cases this is exactly a three-point semimetric.

This argument is direct at the root of the entire subtree; no induction on the
internal mixture of 2/Delta3/Y3 nodes is required.

## 3. 2-sum compiler

The state group is `GF(2)`.

Write

```
a=d(1).
```

Replace the absorbed subtree by one virtual coordinate of weight

```
a>=0.
```

The two state costs are exactly

```
0 -> 0,
1 -> a.
```

## 4. Y/bar3 compiler — even trace space

In a Y/bar-3 component the interface triad `111` belongs to the dual code.
Therefore every primal codeword has even interface trace:

```
000,011,101,110.
```

Write

```
a=d(011),
b=d(101),
c=d(110).
```

Subadditivity gives the three triangle inequalities.

Define

```
w1=(b+c-a)/2,
w2=(a+c-b)/2,
w3=(a+b-c)/2.
```

All three weights are nonnegative and

```
011 -> w2+w3 = a,
101 -> w1+w3 = b,
110 -> w1+w2 = c.
```

This is exactly the nonnegative specialization of the half-sum transfer visible
in Kashyap Appendix B.

Thus the entire child table is replaced exactly by three ordinary nonnegative
virtual-coordinate weights.

## 5. Delta3 compiler — quotient by the interface triangle

For ordinary Delta-3 each component contains the interface-only codeword

```
111.
```

The three raw interface coordinates project onto all `GF(2)^3`.

After the common triangle is deleted, traces differing by `111` represent
the same real behavior.  Hence the state group is

```
GF(2)^3 / <111> ~= GF(2)^2.
```

Choose the three nonzero classes

```
g1=[100]=[011],
g2=[010]=[101],
g3=[001]=[110].
```

Write

```
a=d(g1),
b=d(g2),
c=d(g3).
```

Instead of the Y half-sums, assign the raw virtual coordinates the weights

```
beta1=a,
beta2=b,
beta3=c.
```

These are nonnegative.

For class `g1`, the two raw representatives have costs

```
100 : a,
011 : b+c.
```

Because `a<=b+c`, the minimum is exactly `a=d(g1)`.

Cyclically,

```
min(b,a+c)=b,
min(c,a+b)=c.
```

For the zero class, the representatives are `000` and `111`, whose costs
are `0` and `a+b+c`; the minimum is zero.

Therefore the induced quotient cost of the three nonnegative raw connector
weights is **exactly** the original Delta boundary table.

### Anti-loop falsifier

For the equilateral table

```
d=(0,2,2,2),
```

the Y half-sum compiler gives `(1,1,1)`.

If this were copied to Delta, the class `[100]=[011]` would have induced cost

```
min(1,2)=1,
```

not `2`.

So:

```
Y HALF-SUM COMPILER
-> DELTA QUOTIENT
=
FALSIFIED.

DELTA SINGLETON-DISTANCE COMPILER
=
EXACT.
```

## 6. Exact objective replacement

Consider a continuing component with an absorbed child at one interface.

### 2-sum / Y

The continuing component's allowed root state is directly the same state on
which the compiled linear virtual cost was defined.  Therefore replacing the
child by the compiled virtual weights changes no feasible real continuation
and preserves its exact added cost.

### Delta

For a fixed real continuation behavior, the two raw traces `t` and
`t+111` differ only by the interface-only triangle codeword.  Hence both are
available and give the same real continuation coordinates.

The compiled raw virtual weights induce

```
min {
  beta dot t,
  beta dot (t+111)
}
=
d([t]).
```

Thus minimizing over the continuing component after replacement gives exactly
the original child boundary cost for every real behavior.

No signed virtual weight is used.

## 7. Recursive witness reconstruction

For every subtree and every boundary state, store:

- its minimum cost;
- a pointer to the minimum-achieving child/local choice;
- a representative boundary trace.

### 2-sum / Y

The chosen continuation trace directly identifies the stored child state.

### Delta

The continuation solver returns some raw trace `t`.
Look up the stored child witness for its quotient class `[t]`.

If the stored child representative is `t+111` rather than `t`, toggle the
child's interface-only `111` codeword.  This changes only deleted virtual
coordinates, leaves all real child coordinates and internal cost unchanged,
and makes the raw traces agree for gluing.

Following the stored pointers recursively reconstructs an exact global witness.

## 8. Mixed Delta/Y closure

There is no separate mixed-type algebraic obstruction.

An absorbed subtree may contain any source-valid mixture of

```
2 / Delta3 / Y3.
```

Its entire internal structure is summarized by the definition of its root
table `d_S`.

Since `d_S` is itself a normalized nonnegative quotient/coset semimetric, the
compiler used at the root depends **only** on the root interface type:

```
root 2      -> scalar compiler,
root Y      -> half-sum compiler,
root Delta  -> singleton-distance quotient compiler.
```

Therefore the table class is closed under arbitrary source-valid mixed
subtrees.

Min-plus convolution is an optional equivalent view: infimal convolution of
normalized subadditive functions on the same finite binary group is again
normalized and subadditive.

## 9. Rational arithmetic

If the input weights have polynomial bit length, the 2-sum and Delta compilers
use only minima and additions.

The Y compiler additionally divides by two.

Along a decomposition tree of polynomial size, at most one factor of two is
introduced per Y compilation level.  Therefore denominator bit length grows
at most linearly with tree depth, and all exact rational arithmetic remains
polynomial-bit.

The T-join / shortest-path routines may therefore operate on exact rational
nonnegative weights without pseudopolynomial expansion.

## 10. Consequence for NM-0013 / NM-0015

NM-0015 gives a degree-independent switching-equivalent two-row signature
support bound at a materialized torso.

The present theorem shows that already-absorbed children can be represented by
ordinary **nonnegative** virtual weights without adding new group-label support
or increasing the boundary state dimension.

Therefore the local NM-0013 binary-cycle -> constant exceptional subset ->
ordinary T-join reduction remains valid after arbitrary mixed child
absorption, provided the torso satisfies the already-frozen two-row/signature
hypotheses.

## 11. Gate verdict

```
R5_E10A_BOUNDARY_METRIC_CLOSURE_GATE_V1
=
PASS_EXACT_NONNEGATIVE_COMPILATION_AND_WITNESS_RECONSTRUCTION
```

with:

```
2:
GF(2) scalar message

Y/bar3:
even-trace GF(2)^2 message
-> nonnegative half-sum weights

Delta3:
GF(2)^3/<111> message
-> nonnegative singleton-distance raw weights

mixed subtree:
root table remains a normalized quotient semimetric

witness:
exact recursive reconstruction
```

## 12. Remaining scientific firewall

This theorem removes the **conditioned-table representation** obstruction.

It does not by itself certify that every object needed by the original
lower-bound-tight cubic problem has now been covered exactly once by the chain

```
source decomposition
-> no-S8 absorption
-> distinguished/nondistinguished two-row torsos
-> virtual interface propagation
-> final shortest-f threshold.
```

Before any global polynomial-algorithm or P=NP promotion, perform a fresh
end-to-end composition audit over the entire E10 chain.

Freeze next required audit:

```
PA-0012
E10 END-TO-END DECOMPOSITION SOLVER
COMPOSITION / COVERAGE AUDIT
```

Required questions:

1. Are all decomposition component classes either source-bound polynomial or
   covered by NM-0013/NM-0014/NM-0015/NM-0016?
2. Is every virtual interface represented exactly once with compatible
   Delta/Y orientation?
3. Is the distinguished `f` root objective reconstructed exactly?
4. Does the final threshold remain the original `n/3+1` query with no
   hidden input-dependent exponential state?
5. Is total construction + solve + witness reconstruction polynomial in the
   original input size?

No end-to-end solver claim before that audit.

## 13. Scientific ceiling

```
PA-0011
=
PASS

BOUNDARY TABLE SEMIMETRIC
=
SOURCE-BOUND / DIRECT

Y HALF-SUM COMPILER
=
SOURCE-BOUND SPECIALIZATION

DELTA QUOTIENT COMPILER
=
PROVED

MIXED BOUNDARY METRIC CLOSURE
=
PROVED

NONNEGATIVE VIRTUAL WEIGHTS
=
PROVED

RECURSIVE WITNESS RECONSTRUCTION
=
PROVED

FULL E10 END-TO-END SOLVER
=
NOT YET AUDITED

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
