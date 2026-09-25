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

### S1 — Kashyap Appendix B already transfers arbitrary linear-cost tables for the dual Y 3-sum

Source correction: Definition 6.1 uses the dual/bar-3 operation, not ordinary Delta-3; the paper explicitly notes that ordinary 3-sum is absent from that definition. Accordingly Lemma B.1(b) applies to the bar-3 / Y-sum branch and computes four minima corresponding to the even-parity interface states

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

### S3 — Y3 nonnegative table lies in the three-point metric cone

For a Y-sum component, `111` lies in the dual code, hence every primal codeword has even interface trace. Write

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

This is exactly the nonnegative specialization of Kashyap Appendix B for the Y/even-trace branch, and the same three-point metric-cone mechanism already isolated in the earlier JANUS interface-cost artifact.

Classification:
`Y3_NONNEGATIVE_TABLE=SOURCE_BOUND_HALF_SUM_METRIC_COMPILER`.

### S4 — ordinary Delta3 has a quotient state, not the Y even-trace state

For ordinary Delta-3, `111` is a codeword of each component and the restriction onto the three interface coordinates is all of `GF(2)^3`. Two traces differing by `111` represent the same real behavior after the interface is deleted. Thus the natural boundary state group is

```
GF(2)^3 / <111> ~= GF(2)^2.
```

Each class has a unique even-parity representative, but this is only a chosen section. The raw continuation component still contains both representatives. Therefore the Y half-sum coefficients cannot simply be copied to Delta: a linear cost on the three raw bits need not be constant on a quotient class.

No source located in this audit states the exact nonnegative compiler for this quotient-state objective together with recursive witness reconstruction.

Classification:
`DELTA3_QUOTIENT_STATE=SOURCE_BOUND_LANGUAGE__EXACT_NONNEGATIVE_COMPILATION_GAP_SURVIVES`.

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
