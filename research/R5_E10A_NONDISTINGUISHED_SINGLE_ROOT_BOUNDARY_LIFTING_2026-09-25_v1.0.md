# R5 E10A — Nondistinguished Single-Root Boundary Lifting

Date: 2026-09-25

Authority:
`JANUS_DERIVED_EXACT_SINGLE_ROOT_BOUNDARY_LIFTING_AFTER_PA0009__NO_FULL_DECOMPOSITION_CLAIM`

Authorizing audit:
`PA-0009-CUBIC-ORIGIN-NONDISTINGUISHED-TORSO-VIRTUAL-INTERFACE-PROPAGATION`

Parent gate:
`R5_E10A_NONDISTINGUISHED_TORSO_BOUNDARY_LIFTING_GATE_V1`

Checker:
`experiments/r5_e10a_nondistinguished_single_root_boundary_lifting.py`

## 1. Input inherited from the cubic star

Let `P=M([I+P+Q|1])` be the exact cubic parent and let `A` be the real ground
set on one decomposition side with

```
f notin A.
```

NM-0010 gives a cocycle-star spanning family

```
D_i,
f in D_i,
|D_i|=4,
span(D_i)=C*(P).
```

Puncturing to `A` yields

```
X_i = D_i intersect A,
|X_i|<=3,
span{X_i}=C*(P)|A.
```

The task is to lift the real-side space through one rooted virtual separator.

## 2. Linear-algebra language

For a component `N` with real ground `A` and virtual separator `Z`, write

```
rho_A : C*(N) -> GF(2)^A
```

for coordinate restriction.

The desired statement has two parts:

1. identify `im(rho_A)` with the parent cocycle restriction `C*(P)|A`;
2. control `ker(rho_A)` and the support of a lift of each `X_i`.

The three sum types are different.

## 3. 2-sum boundary lifting

Let `Z={z}` be the virtual element of a binary 2-sum.

By the 2-sum hypotheses, `z` is neither a loop nor a coloop in either
component.  Therefore:

- the cycle trace onto `z` is surjective;
- the cocycle trace onto `z` is surjective;
- no nonzero cocycle is supported only on `z`.

Hence

```
ker(rho_A)=0.
```

The standard fiber-product description of a binary 2-sum shows

```
im(rho_A)=C*(P)|A.
```

Thus every real restriction `X_i` has a **unique** cocycle lift
```
X_i hat
```
to the component, and the only possible additional support is `z`.

Therefore

```
|X_i hat| <= |X_i|+1 <=4.
```

Since `rho_A` is injective and the `X_i` span its image, the lifts span
the full component cocycle space.

### 2-sum verdict

```
C*(N)
is spanned by cocycles of support <=4.
```

## 4. Ordinary Delta 3-sum

Let `Z={z1,z2,z3}` be the common triangle.

In each component:

- `Z` is a circuit;
- no nonzero cocycle is supported entirely in `Z`;
- the cycle trace onto `Z` is all `GF(2)^3`.

The last two statements are the standard equivalent 3-sum conditions in the
binary-code formulation.

### 4.1 Restriction map is injective

Because there is no nonzero cocycle supported entirely on `Z`,

```
ker(rho_A)=0.
```

### 4.2 Every component real restriction occurs in the parent

Take a component cocycle

```
(x,t) in C*(N),
x in GF(2)^A,
t in GF(2)^Z.
```

Since `Z` is a circuit, binary circuit-cocycle orthogonality gives

```
t dot 111 = 0.
```

Thus

```
t in {000,110,101,011}.
```

The restriction to `Z` of the cocycle space on the opposite component is
exactly this even-parity subspace.  Therefore an opposite-side cocycle with the
same trace `t` exists.  Pairing the two cocycles gives a parent cocycle whose
restriction to `A` is `x`.

Conversely, orthogonality to the parent cycle fiber product implies that every
parent cocycle restriction to `A` has a unique component cocycle lift.

Therefore

```
im(rho_A)=C*(P)|A.
```

### 4.3 Support bound

The unique virtual trace has weight `0` or `2`.

Hence each cubic-star puncture generator lifts with

```
|X_i hat|
<=
|X_i|+2
<=
5.
```

Because restriction is injective, these lifted generators span the entire
component cocycle space.

### Delta-3 verdict

```
C*(N)
is spanned by cocycles of support <=5.
```

This proves the proposed `3+2` bound exactly.

## 5. Dual Y 3-sum

This case is not obtained by copying the triangle argument.

A primal Y-sum is an ordinary Delta-sum after dualizing.  Therefore the
**component cocycle spaces themselves** satisfy the Delta-side trace conditions.

The virtual set

```
Z={z1,z2,z3}
```

is a cocircuit of the primal component.

### 5.1 Restriction kernel

The sum hypotheses exclude support-one and support-two cocycles on `Z`, while
`Z` itself is a cocycle.

Therefore

```
ker(rho_A)=span{111_Z}.
```

So restriction is deliberately **not injective**.

This is the exact firewall missing from a naive Delta/Y conflation.

### 5.2 Real-side image

Because the component cocycle trace onto `Z` is all `GF(2)^3`, any trace on
one side can be matched by a cocycle on the opposite side in the dual
Delta-sum.

Hence again

```
im(rho_A)=C*(P)|A.
```

### 5.3 Small representatives

Fix a real restriction `x` in the image.

It has exactly two component cocycle lifts, differing by the interface triad:

```
(x,t)
and
(x,t xor 111).
```

Their boundary weights sum to three.  Therefore one lift has

```
wt(trace) <=1.
```

Choose that lift for every punctured star generator `X_i`.

Then

```
|X_i hat|
<=
|X_i|+1
<=4.
```

The chosen lifts span the cocycle space modulo the one-dimensional interface
kernel.  Adding the interface cocycle `Z` itself completes the span.

### Y-3 verdict

```
C*(N)
=
span(
  cocycles of support <=4,
  plus the interface-only triad Z of support 3
).
```

Thus the dual case is not weaker than the Delta case; it has a different
kernel structure and a slightly better lift bound.

## 6. Exact single-root support table

Freeze:

```
2-SUM:
  restriction kernel = 0
  lifted generator support <=4

DELTA 3-SUM:
  restriction kernel = 0
  virtual trace weight in {0,2}
  lifted generator support <=5

Y 3-SUM:
  restriction kernel = span{virtual triad}
  choose lift trace weight <=1
  lifted generator support <=4
  plus interface-only triad support 3
```

This closes all five PA-0009 proof obligations:

1. restriction-map injectivity/kernel;
2. boundary-trace realizability;
3. ordinary Delta 3-sum;
4. dual Y 3-sum separately;
5. explicit lift/interface witness reconstruction.

## 7. Consequence for two-row torsos

Suppose the resulting component is in the live two-row graph-lift class

```
[B_G;S]
```

so that

```
dim(C*(N)/cut(G)) <=2.
```

Choose at most two quotient-independent cocycle generators from the bounded
family above and use them as the two signature rows, exactly as in NM-0013.

No common-f overlap is assumed here.

Therefore a row-equivalent / switching-equivalent representation exists with
nonzero signature support bounded by:

```
2-sum:      <= 8
Delta3:     <=10
Y3:         <= 8
```

For a conservative uniform ceiling across all three single-root cases:

```
|supp(lambda)| <=10.
```

## 8. Conditioned separator costs

For source-standard 2/3-sum shortest-circuit composition, the component must
supply only finitely many connector-conditioned values, such as:

```
minimum circuit containing z
and no other connector.
```

To compute these values, enlarge the exceptional set by the virtual separator:

```
F' = supp(lambda) union Z.
```

Hence

```
|F'| <= 9   for 2-sum,
|F'| <=13   for Delta3,
|F'| <=11   for Y3.
```

For each prescribed connector state and each subset

```
R subseteq F'
```

consistent with that state and with zero total group label, the remaining
zero-label real edges must form an ordinary `T`-join with

```
T=partial_G(R).
```

Thus every required single-root connector-conditioned cost is computable by a
constant enumeration of ordinary deterministic minimum `T`-joins.

For the worst Delta case:

```
2^13 = 8192
```

exceptional subsets.

This is a constant, not an input-dependent exponential.

For the standard condition "contains connector z and excludes the other
connectors", replacing a feasible binary cycle by its circuit component
containing `z` preserves the condition and cannot increase weight.  Hence the
cycle relaxation is exact for the source-required scalar connector costs.

## 9. What is source-bound and what is derived

Source-bound:

- 2/Delta3/Y3 sum definitions and duality;
- circuit-cocircuit even intersection in binary matroids;
- minimum `T`-join;
- vertex switching / row-equivalent signature normalization.

JANUS-derived here:

- exact real-restriction image statement tied to the punctured NM-0010 star;
- separate kernel formulas for 2 / Delta3 / Y3;
- support bounds `4 / 5 / (4+triad)`;
- uniform two-row signature-support bound `<=10`;
- constant-enumeration conditioned-cost reduction with `|F'|<=13`.

## 10. Gate verdict

```
R5_E10A_NONDISTINGUISHED_TORSO_BOUNDARY_LIFTING_GATE_V1
=
PASS_SINGLE_ROOT_BOUNDARY_LIFTING_AND_CONDITIONED_COST_SOLVER
```

This theorem handles **one rooted decomposition interface**.

## 11. Remaining firewall: multi-interface accumulation

Do not promote this to a full cubic decomposition algorithm yet.

A final torso in a decomposition tree can carry virtual elements for more than
one incident separator.  The theorem above gives a constant bound relative to
one rooted 2/3-sum interface; it does not prove that repeated child-interface
absorption preserves a uniform global constant independent of decomposition
degree.

The next changed scope is therefore:

```
PA-0010
MULTI-INTERFACE / DECOMPOSITION-TREE
SUPPORT-ACCUMULATION SOURCE AUDIT
```

The exact next question is:

```
Can a source-valid decomposition be rooted/processed so that
only one live interface is exposed at each two-row solve,
with already absorbed children represented solely by
scalar conditioned weights,

or can multiple virtual interfaces accumulate in one
two-row torso in a way that destroys the constant-support
normal form?
```

No new mathematics in this changed scope before the audit.

## 12. Scientific ceiling

```
PA-0009
=
PASS

2-SUM BOUNDARY LIFT
=
PASS <=4

DELTA3 BOUNDARY LIFT
=
PASS <=5

Y3 BOUNDARY LIFT
=
PASS <=4 + INTERFACE TRIAD

SINGLE-ROOT TWO-ROW SIGNATURE SUPPORT
=
PASS <=10

SINGLE-ROOT CONDITIONED COSTS
=
DETERMINISTIC POLYNOMIAL VIA <=8192 T-JOIN CASES

MULTI-INTERFACE DECOMPOSITION TREE
=
NOT YET CLOSED

FULL ORIGINAL CUBIC EXACT-ONE SOLVER
=
NOT YET PROVED

P_VS_NP
=
OPEN
```
