# R5 E10A — Mixed Delta/Y Conditioned-Cost Table to Two-Row Objective Source Audit

Date: 2026-09-25

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__GENERIC_TRANSFER_AND_QUOTIENT_METRIC_SOURCE_BOUND__EXACT_DELTA_Y_COMPILATION_GAP_SURVIVES`

Immediate predecessor:
`NM-0015-STAR-SUPPORT-ACTIVE-INTERFACE-TREE-PROPAGATION`

## G0 — exact changed scope

NM-0015 removes unbounded decomposition degree as a source of unbounded
signature support.

The remaining changed-scope question is objective propagation:

```
absorbed child subtree
  -> exact finite boundary cost table
  -> local two-row torso objective
  -> NM-0013/NM-0014 T-join solver.
```

The audit must distinguish:

1. arbitrary four-state linear-cost tables;
2. nonnegative binary-cycle / coset-leader tables actually produced by the
   cubic lineage;
3. ordinary Delta 3-sum boundary coordinates;
4. dual Y 3-sum quotient coordinates.

## G1 — internal anti-duplication

Already source-bound or internally sealed:

- Appendix-B 2/3-sum conditioned-cost recursion;
- positive-integer scalar 3-sum interface metric cone;
- exact single-root Delta/Y trace semantics from NM-0014;
- support accumulation from NM-0015;
- ordinary nonnegative T-join optimization.

No previous Fundamentum artifact was found that proves the exact conjunction:

```
mixed Delta/Y subtree
+
normalized nonnegative four-state boundary table
+
exact nonnegative three-coordinate realization
+
recursive witness reconstruction.
```

## G2 — source collisions

### S1 — Kashyap Appendix B already transfers arbitrary linear-cost tables

For an ordinary 3-sum, Kashyap Lemma B.1 computes four minima corresponding
to the interface states

```
000, 011, 101, 110.
```

For general real linear costs the three transferred coefficients are

```
beta_1 - M = (-mu_0-mu_1+mu_2+mu_3)/2,
beta_2 - M = (-mu_0+mu_1-mu_2+mu_3)/2,
beta_3 - M = (-mu_0+mu_1+mu_2-mu_3)/2.
```

Thus generic four-state linear-cost transfer is source-bound.

The coefficients need not be nonnegative for an arbitrary table.  Hence:

```
ARBITRARY FOUR-STATE TABLE
-> THREE NONNEGATIVE PHYSICAL EDGE COSTS
```

is not a source theorem.

Classification:
`GENERIC_SIGNED_TRANSFER_SOURCE_BOUND__NONNEGATIVE_SPECIALIZATION_NOT_AUTOMATIC`.

### S2 — normalized nonnegative lineage tables are quotient/coset weights

For a linear subspace/code, the minimum nonnegative weight in each coset is
the standard coset-leader weight.  Equivalently, a quotient of a weighted
Hamming space inherits a translation-invariant quotient pseudometric.

Therefore, for a boundary group `G` and normalized table

```
d(g)=minimum internal nonnegative cost among feasible objects of boundary state g,
```

we have source-standard metric behavior:

```
d(0)=0,
d(g)>=0,
d(x+y)<=d(x)+d(y).
```

The triangle inequality also follows directly by symmetric-differencing two
minimum witnesses.

Classification:
`QUOTIENT_COSET_WEIGHT_SEMIMETRIC=SOURCE_BOUND_LANGUAGE`.

### S3 — ordinary Delta3 nonnegative table lies in the three-point metric cone

Write

```
a=d(011), b=d(101), c=d(110).
```

Then

```
a<=b+c,
b<=a+c,
c<=a+b.
```

With `d(000)=0`, Kashyap's Appendix-B coefficients reduce exactly to

```
w1=(b+c-a)/2,
w2=(a+c-b)/2,
w3=(a+b-c)/2.
```

Hence all three are nonnegative and

```
d(011)=w2+w3,
d(101)=w1+w3,
d(110)=w1+w2.
```

This is the same three-point metric-cone mechanism already isolated in the
earlier JANUS 3-sum interface-cost artifact.

Classification:
`DELTA3_NONNEGATIVE_TABLE=KNOWN_METRIC_CONE_MECHANISM`.

### S4 — dual Y3 must be normalized through the quotient

Kashyap's dual 3-sum is defined separately and ordinary 3-sum is not closed
under duality.

For a Y interface the raw three-coordinate state has the interface-only
`111` kernel, so the correct boundary state space is

```
GF(2)^3 / <111> ~= GF(2)^2.
```

Each class has a unique even-parity representative:

```
[000] -> 000,
[100] -> 011,
[010] -> 101,
[001] -> 110.
```

Kashyap's definition of dual 3-sum passes through the corresponding enlarged
codes so that ordinary 3-sum is applied after the `111` quotient/coset
identification.

No source located in this audit states the full JANUS objective theorem:

```
Y3 nonnegative child table
-> normalize to the even-parity transversal
-> obtain a nonnegative three-edge realization
-> reconstruct the original-side witness recursively.
```

Classification:
`Y3_QUOTIENT_LANGUAGE_SOURCE_BOUND__EXACT_NONNEGATIVE_COMPILATION_GAP_SURVIVES`.

### S5 — min-plus / infimal convolution preserves subadditive boundary costs

For functions `f,g:G->R_{ge0}` with `f(0)=g(0)=0` and subadditivity, the
infimal convolution

```
h(s)=min_t [f(t)+g(s+t)]
```

is again nonnegative, normalized and subadditive.

This is a standard infimal-convolution phenomenon and also has an immediate
finite-group proof by combining minimizers.

However the full mixed decomposition theorem does not need to rely on
pairwise convolution alone: any absorbed subtree with nonnegative internal
weights directly defines a quotient/coset-weight table at its root boundary,
which is already subadditive.

Classification:
`SEMIMETRIC_CLOSURE_MECHANISM_STANDARD__LINEAGE_STATE_BINDING_STILL_TO_VERIFY`.

## G3 — exact remaining gap

Known / source-bound:

```
generic signed four-state transfer
quotient/coset-leader metric language
Delta3 metric-cone realization
tree conditioned-cost recursion
```

No exact source closure located for the conjunction:

```
MIXED 2/Delta3/Y3 CUBIC-LINEAGE SUBTREE
+
ROOT BOUNDARY NORMALIZATION
+
NONNEGATIVE SEMIMETRIC EXPORT
+
EXACT THREE-COORDINATE REALIZATION
+
WITNESS POINTERS THROUGH Delta<->Y BASIS CHANGES.
```

Therefore:

```
PA-0011-MIXED-DELTA-Y-CONDITIONED-COST-TABLE-TO-TWO-ROW-OBJECTIVE
=
PASS_SCOPED_GAP_CONFIRMED
```

New mathematics is authorized only inside:

```
R5_E10A_BOUNDARY_METRIC_CLOSURE_GATE_V1
```

## First authorized theorem target

Prove that every absorbed cubic-lineage subtree with root interface of type

```
2-sum / Delta3 / Y3
```

exports a normalized nonnegative subadditive cost function on

```
GF(2) or GF(2)^2,
```

and that for the four-state case the table has an exact nonnegative
three-coordinate realization after the source-valid Delta/Y state
identification.

Required:

1. exact state group and zero-state normalization;
2. Delta even-parity coordinates;
3. Y quotient by `111` and fixed even-parity transversal;
4. nonnegative rational transferred weights of polynomial bit complexity;
5. exact objective equality after replacement;
6. recursive witness reconstruction from stored state minimizers;
7. no hidden signed edge required by the lineage specialization.

## Mandatory anti-loop controls

Do not:

- claim Appendix-B signed transfer as new;
- claim quotient/coset metric triangle inequality as new;
- assume an arbitrary four-state table is nonnegative-realizable;
- identify raw Y states with Delta states without quotienting by `111`;
- lose constant offsets when normalizing `mu_0`;
- infer the full decomposition solver before witness/state reconstruction is bound;
- reopen Bentert/PIT.

## Scientific ceiling

```
GENERIC FOUR-STATE SIGNED TRANSFER
=
SOURCE-BOUND

NONNEGATIVE LINEAGE TABLE IS A QUOTIENT SEMIMETRIC
=
SOURCE-BOUND / DIRECT

DELTA3 THREE-EDGE METRIC REALIZATION
=
KNOWN MECHANISM

Y3 QUOTIENT NORMALIZATION
=
SOURCE-BOUND LANGUAGE

MIXED LINEAGE NONNEGATIVE COMPILATION + WITNESS
=
NO EXACT CLOSURE LOCATED

PA-0011
=
PASS_SCOPED_GAP_CONFIRMED

P_VS_NP
=
OPEN
```
