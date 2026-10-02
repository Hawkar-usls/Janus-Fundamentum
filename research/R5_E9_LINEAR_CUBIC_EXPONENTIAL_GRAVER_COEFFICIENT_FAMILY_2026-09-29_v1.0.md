# R5 E9 — Linear-cubic exponential Graver-coefficient family

Date: 2026-09-29

Status: `JANUS_DERIVED_ARBITRARY_SIZE_CONNECTED_LINEAR_CUBIC_NULLITY1_EXPONENTIAL_GRAVER_BARRIER__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVIDE THE MISSING POLYNOMIAL SOURCE-TRADE ORACLE.
IT PROVES THAT CUBICITY + LINEARITY + NULLITY ONE DO NOT BOUND PRIMITIVE
INTEGER-KERNEL / GRAVER COEFFICIENTS BY ANY POLYNOMIAL IN THE MATRIX ORDER.

THE FAMILY ITSELF HAS SMALL INTERFACES AND IS NOT CLAIMED TO BE A
SEPARATOR-RESISTANT HARD FAMILY.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Amplifier gadget G

Use variables `x0,...,x8` and seven 3-rows

```text
(6,3,0)
(5,6,4)
(8,4,0)
(6,7,8)
(4,7,3)
(1,5,2)
(8,3,5)
```

The gadget is linear. Its column degrees are

```text
inputs  x1,x2 : degree 1,
outputs x7,x0 : degree 2,
all other columns : degree 3.
```

Let

```text
a=x1,
b=x2.
```

Solving the seven homogeneous row equations gives uniquely over `Q`

```text
s=(a+b)/2,

x3=x4=x6=x8=s,
x0=x5=x7=-2s=-(a+b).
```

Therefore the exact boundary transfer is

\[
\boxed{
(a,b)\longmapsto (-(a+b),-(a+b)).
}
\]

For integer solutions the only extra condition is `a+b` even. In particular on the equal line `a=b` the transfer is

\[
\boxed{(a,a)\longmapsto(-2a,-2a).}
\]

There is no hidden homogeneous mode once the two input values are fixed.

## 2. Closing-cap gadget C

Use a second 9-variable, 7-row linear gadget

```text
(8,4,7)
(6,3,4)
(2,6,8)
(0,3,7)
(4,5,2)
(8,5,3)
(1,7,2)
```

Its degree-one boundary columns are

```text
inputs: x1,x0,
```

and its degree-two boundary columns are

```text
outputs: x5,x6.
```

All other columns have degree three.

Solving its homogeneous equations gives

```text
x0=x1=x6+3x8,
x5=x6,
x2=x3=-x6-x8,
x4=x8,
x7=-2x8.
```

Thus the boundary relation is

\[
\boxed{
\text{input pair }(\alpha,\alpha),
\qquad
\text{output pair }(\beta,\beta),
}
\]

with integer extension iff

\[
\boxed{\alpha\equiv\beta\pmod 3.}
\]

Over `Q`, the two equal-pair values are independent and determine all internal variables uniquely.

## 3. Chain construction

For `k>=1`, take `k` copies

```text
G_0,...,G_{k-1}
```

of the amplifier and one copy of `C`.

For each `t<k-1`, identify the two degree-two outputs of `G_t` pairwise with the two degree-one inputs of `G_{t+1}`.

At the right end, identify the two degree-two outputs of `G_{k-1}` pairwise with the two degree-one inputs of `C`.

At the left end, identify the two degree-two outputs of `C` pairwise with the two degree-one inputs of `G_0`.

Call the resulting incidence matrix `A_k`.

Each identification joins one degree-two boundary column to one degree-one boundary column. Hence every resulting column has degree three.

There are `k+1` seven-row gadgets and, after the `2(k+1)` pairwise identifications,

\[
\boxed{n_k=7(k+1)}
\]

rows and the same number of columns.

## 4. Linearity and connectedness

Each constituent gadget is linear.

The two amplifier output columns never occur together in one amplifier row. The two cap input columns also never occur together in one cap row, and the two cap output columns never occur together in one cap row. Although the two amplifier input columns occur together in one row, they are glued to the cap output pair, which does not co-occur in any cap row.

Consequently, across every interface, no row from one side and row from the other side can acquire two common columns. No identification is made between two columns of the same gadget. Therefore no row develops a repeated column and no pair of distinct rows meets twice.

Hence `A_k` is linear.

Every local gadget incidence structure is connected to its boundary, and the gadgets form a cyclic chain through the stated interfaces. Thus `A_k` is connected.

### Theorem EGC-1

For every `k>=1`, `A_k` is a connected square linear-cubic `0/1` matrix of order `7(k+1)`.

## 5. Exact global rational kernel

Let the first amplifier inputs be `(a,b)`.

After the first amplifier the output pair is equal. Therefore every later amplifier input/output pair is equal.

The cap output relation forces the first amplifier input pair itself to be equal:

\[
a=b.
\]

Write the common value as `t`. Repeated amplifier transfer gives the final pair

\[
\boxed{((-2)^k t,(-2)^k t).}
\]

The cap therefore has

```text
alpha=(-2)^k t,
beta=t.
```

Over `Q` this always extends uniquely. Thus the global rational kernel has exactly one free scalar `t`.

So

\[
\boxed{
\operatorname{rank}_{\mathbb Q}(A_k)=n_k-1,
\qquad
\nu_{\mathbb Q}(A_k)=1.
}
\]

## 6. Integer kernel and primitive coefficient growth

For `t=1`, every amplifier is integral because each equal input pair has even sum.

The cap congruence is also automatic:

\[
(-2)^k\equiv1\pmod3,
\]

so

\[
\alpha-\beta=((-2)^k-1)t
\]

is divisible by three.

Therefore `t=1` gives an integer kernel vector `h_k`.

It is primitive because the first amplifier input coordinates equal one. Since the global rational kernel is one-dimensional,

\[
\ker_{\mathbb Z}(A_k)=\mathbb Z h_k.
\]

The final amplifier output coordinates have magnitude exactly `2^k`, so

\[
\boxed{
\|h_k\|_\infty\ge2^k.
}
\]

All amplifier coordinates at stage `j` have magnitude at most `2^j`, and the cap's extra coordinate

\[
x_8=\frac{(-2)^k-1}{3}
\]

has magnitude strictly less than `2^k` for `k>=1`. Hence in fact

\[
\boxed{
\|h_k\|_\infty=2^k.
}
\]

Since `n_k=7(k+1)`, this is

\[
\boxed{
\|h_k\|_\infty
=2^{n_k/7-1}.
}
\]

## 7. Graver consequence

For a rank-`n-1` integer matrix whose integer kernel is generated by one primitive vector `h`, the Graver basis is exactly

\[
\{h,-h\}.
\]

Therefore

\[
\boxed{
\max_{g\in\mathcal G(A_k)}\|g\|_\infty
=2^{n_k/7-1}.
}
\]

### Theorem EGC-2

Primitive integer-kernel / Graver coefficients can grow exponentially with the order even on connected square linear-cubic incidence matrices of rational nullity one.

## 8. Algorithmic meaning

This kills the shortcut

```text
row degree = column degree = 3
+ linearity
=> every primitive trade has polynomially bounded coefficients
=> enumerate coefficient range / use a polynomial proximity radius.
```

The implication is false.

It does **not** imply that source-trade augmentation itself requires exponential time. The family has constant-size interfaces and can be represented symbolically by the 2x2 transfer law above; existing small-separator machinery may exploit that structure.

Thus the correct conclusion is narrower and more useful:

```text
A universal polynomial source-trade algorithm must tolerate exponentially large
primitive coefficients in binary encoding and cannot be justified by a polynomial
coefficient bound that follows merely from cubicity and linearity.
```

This points toward symbolic/decomposition-based augmentation rather than explicit coefficient enumeration.

## 9. Relation to prior art

General hypergraph toric ideals are known to admit complicated primitive/Graver elements; see Petrović, Thoma and Vladoiu, *Hypergraph encodings of arbitrary toric ideals*, JCTA 166 (2019), 11–41, DOI `10.1016/j.jcta.2019.02.017`.

That general theorem is not imported as an exact result for the present regular linear class. The exponential family above is an explicit JANUS construction inside the exact connected square linear-cubic carrier.

No novelty/priority claim beyond this scoped construction is made here.

## 10. Ceiling

```text
CONNECTED + SQUARE + LINEAR + CUBIC
= PROVED FOR ALL k>=1

ORDER
= 7(k+1)

RATIONAL NULLITY
= 1

INTEGER KERNEL
= Z h_k

||h_k||_infinity
= 2^k = 2^(n/7-1)

GRAVER BASIS
= {+h_k,-h_k}

POLYNOMIAL PRIMITIVE-COEFFICIENT BOUND FROM CUBICITY/LINEARITY
= FALSE

SOURCE_TRADE_AUGMENTATION
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
