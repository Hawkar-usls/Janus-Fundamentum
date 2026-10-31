# R5 E10A — Star-Support Active-Interface Tree Propagation

Date: 2026-09-25

Authority:
`JANUS_DERIVED_EXACT_ACTIVE_INTERFACE_BOUND_AFTER_PA0010__NO_FULL_DECOMPOSITION_SOLVER_CLAIM`

Authorizing audit:
`PA-0010-MULTI-INTERFACE-DECOMPOSITION-TREE-SUPPORT-ACCUMULATION`

Parent gate:
`R5_E10A_STAR_SUPPORT_ACTIVE_INTERFACE_TREE_PROPAGATION_GATE_V1`

Checker:
`experiments/r5_e10a_star_active_interface_tree_propagation.py`

## 1. Global star input

NM-0010 gives a spanning cocycle family of the exact cubic parent

```
D_1,...,D_n
```

with

```
f in D_i,
|D_i|=4.
```

Fix one star cocycle `D=D_i`.

Let `T` be a source-valid cycle-free 2/Delta3/Y3 decomposition tree for the
cocycle code, or equivalently the dualized tree realization appropriate to
cocycle propagation.

Each original real coordinate is assigned to exactly one node/piece of the
tree.

## 2. Source-bound tree-state fact

For an edge `e` of a minimal tree realization, let `J(e)` and
`Jbar(e)` be the original-coordinate sets on the two sides.

The minimal state space is the standard quotient whose dimension is

```
dim C - dim C_J(e) - dim C_Jbar(e).
```

Hence a codeword supported entirely on one side represents the zero state on
the separating tree edge.

Applied to the fixed global cocycle `D`:

```
D intersect J(e) = empty
    =>
canonical state of D on e = 0
```

when `J(e)` is taken to be the branch away from the current torso.

For an explicit Y-interface this canonical zero state corresponds to choosing
the `000` representative rather than the interface-only `111` kernel
representative.

This is a canonical state choice, not a claim that the raw Y-component
restriction map is injective.

## 3. Theorem — STAR_ACTIVE_INTERFACE_BOUND_FOUR

Fix a torso/tree node `v`.

Removing `v` from the tree partitions the remaining original real
coordinates among the incident branches.

Let

```
s_v = number of elements of supp(D) assigned locally to v.
```

An incident interface can carry a nonzero canonical state for `D` only if
its branch contains at least one element of

```
supp(D) - local(v).
```

Distinct incident branches are disjoint. Therefore

```
# active incident interfaces
<=
4 - s_v
<=
4.
```

Equivalently, the nonzero state edges of `D` lie in the minimal subtree of
`T` connecting the at most four nodes carrying its original support.

Freeze:

```
TORSO DEGREE
=
UNBOUNDED ALLOWED

ACTIVE INTERFACES
PER ORIGINAL CUBIC STAR COCYCLE
<=
4.
```

This is the exact PA-0010 killer.

## 4. Separate physical trace bounds

Use the exact single-root results of NM-0014 on each active incident edge.

### 2-sum

A nonzero state requires at most one virtual coordinate.

```
trace support <=1.
```

### ordinary Delta 3-sum

The separator is a circuit and every cocycle trace is even:

```
000, 110, 101, 011.
```

Hence

```
trace support <=2.
```

### dual Y 3-sum

Two raw lifts differ by the interface triad `111`.

Choose the representative of smaller support:

```
trace support <=1.
```

If the branch contains no support of `D`, choose the canonical `000`
representative.

## 5. Simultaneous Y-kernel choices commute

Different tree edges use disjoint virtual coordinate sets.

Toggling the Y-kernel representative on one interface adds only that
interface's `111` triad.

Therefore kernel toggles on distinct Y-interfaces commute and do not alter
traces on the other interfaces.

Consequently all empty Y-branches may be normalized to `000` simultaneously.

This proves the simultaneous-choice obligation left open by PA-0010.

## 6. Uniform local support bound

Let `a_v` be the number of active incident interfaces.

From Section 3:

```
a_v <= 4-s_v.
```

The worst physical trace is Delta, of support two. Therefore the canonical
local representative `L_v(D)` satisfies

```
|L_v(D)|
<=
s_v + 2 a_v
<=
s_v + 2(4-s_v)
=
8-s_v
<=8.
```

Thus every original support-four star cocycle has a local tree/torso
representative of support at most eight, independent of torso degree.

## 7. Spanning statement and Y kernels

The original star cocycles span the global cocycle code.

In a minimal observable tree realization, the global codeword-to-configuration
map is linear.  Hence the configurations of the star basis span the full
behavior, and their projections span every local constraint/state behavior.

If one materializes raw Y virtual coordinates instead of quotient states, the
only additional zero-real-support ambiguity at a Y-interface is the
interface-only triad from NM-0014.

Therefore the raw local cocycle behavior is spanned by:

```
{ local representatives L_v(D_i), each of support <=8 }
union
{ one interface-only triad of support 3 for each incident Y-kernel }
```

No generator in this spanning family has support greater than eight.

The number of kernel triads may grow with torso degree; their **count** is not
claimed bounded.  What is proved is a bounded-support generating family and a
bounded active-interface count for every original star generator.

## 8. Consequence for a two-row torso quotient

Suppose the materialized torso remains in the live two-row graph-lift class

```
[B_G;S]
```

so that

```
dim(C*(N)/cut(G)) <=2.
```

The quotient is spanned by the images of the bounded-support family in
Section 7.

Therefore a quotient basis can be selected from that family using at most two
members.

Each selected member has support at most eight.

After the same row/switching normalization used in NM-0013:

```
|supp(lambda)|
<=
8+8
=
16.
```

Freeze the conditional consequence:

```
MULTI-INTERFACE TWO-ROW TORSO
+
NM-0010 STAR PROPAGATION
+
MATERIALIZED TWO-ROW QUOTIENT RANK <=2
        =>
SWITCH-EQUIVALENT SIGNATURE SUPPORT <=16.
```

This removes unbounded torso degree as a source of unbounded signature support.

## 9. What is source-bound and what is derived

Source-bound:

- cycle-free / minimal tree realization language;
- exact sum-product / tree recursion;
- unary PAG decomposition as a sufficient known pattern;
- 2/Delta3/Y3 sum semantics;
- NM-0014 single-edge trace kernels and representatives.

JANUS-derived here:

- active incident interfaces per original cubic star cocycle <=4;
- simultaneous canonical zeroing of empty Y-branches across distinct
  interfaces;
- local star representative support <=8;
- bounded-support local spanning family;
- conditional two-row signature support <=16 independent of torso degree.

## 10. Why this is not yet the full decomposition solver

The support-accumulation question is closed at the **state/signature** level.

One further integration issue remains before promoting the result to the whole
decomposition algorithm:

the source conditioned-cost recursion must be matched exactly to the local
two-row/T-join objective when a torso has already absorbed several children,
especially across mixed Delta/Y interfaces.

For ordinary Delta 3-sums, source-conditioned scalar costs satisfy the metric
relations already audited earlier.

For arbitrary source recursion / dual Y states, one must not assume without
audit that every four-state conditioned table is representable by
nonnegative independent virtual-edge weights accepted unchanged by the
NM-0013 T-join relaxation.

This is a changed representation/objective scope.

## 11. Gate verdict

```
R5_E10A_STAR_SUPPORT_ACTIVE_INTERFACE_TREE_PROPAGATION_GATE_V1
=
PASS_ACTIVE_INTERFACE_AND_SUPPORT_ACCUMULATION_BOUND
```

with exact ceilings:

```
active incident interfaces per original star cocycle <=4

canonical local star representative support <=8

two-row signature support
if local quotient rank <=2
<=16.
```

## 12. Next mandatory audit

Freeze:

```
PA-0011
MIXED DELTA/Y CONDITIONED-COST
TABLE-TO-TWO-ROW-OBJECTIVE
SOURCE AUDIT
```

Question:

```
After child subtrees are replaced by their exact finite boundary-cost tables,
can every local source-valid 2/Delta3/Y3 torso objective be compiled into the
nonnegative weighted two-row/T-join form required by NM-0013/NM-0014,
without increasing interface state dimension or introducing an
input-dependent number of exceptional labels?
```

Do not start new mathematics in that changed scope before the audit.

## 13. Scientific ceiling

```
PA-0010
=
PASS

ACTIVE INTERFACES PER STAR
=
<=4

LOCAL STAR SUPPORT
=
<=8

MULTI-INTERFACE TWO-ROW SIGNATURE SUPPORT
=
<=16
conditional on quotient-rank-two materialization

UNARYIZATION
=
NOT NEEDED FOR THIS SUPPORT BOUND

MIXED CONDITIONED-COST COMPILATION
=
NOT YET AUDITED

FULL ORIGINAL CUBIC EXACT-ONE SOLVER
=
NOT YET PROVED

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
