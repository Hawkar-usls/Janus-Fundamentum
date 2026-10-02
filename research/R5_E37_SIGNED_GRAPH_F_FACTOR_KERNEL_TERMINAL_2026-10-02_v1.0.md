# R5 E37 — Signed-Graph / f-Factor Kernel Terminal

Date: 2026-10-02

Status:
`EXACT_SIGNED_GRAPH_KERNEL_POLYNOMIAL_TERMINAL__MIXED_ENDPOINT_SIGNS_REDUCE_TO_F_FACTOR`

Scientific ceiling:

```text
THIS NOTE EXTENDS R5 E36 FROM UNSIGNED GRAPH INCIDENCE MATRICES TO THE FULL
TWO-ENDPOINT SIGNED-GRAPH CLASS.

LET R BE AN INTEGER MATRIX IN WHICH EVERY COLUMN HAS EXACTLY TWO NONZERO
ENTRIES, EACH IN {+1,-1}.

IF
  ker_Q(R)=ker_Q(A),
THEN CENTERED EXACT-ONE
  R(3x-1)=0
REDUCES EXACTLY TO AN ORDINARY GRAPH f-FACTOR INSTANCE.

THIS INCLUDES
  ordinary flows/circulations,
  unsigned f-factor kernels,
  mixed directed/undirected signed edges,
  and complements of unsigned edges.

THEREFORE THE ENTIRE SIGNED-GRAPH TWO-NONZERO-PER-COLUMN KERNEL SECTOR IS
POLYNOMIAL.

P_VS_NP = OPEN.
```

## 1. Signed-graph representation

Let

```text
R in {-1,0,1}^{V x E}
```

have exactly two nonzero entries in every column.

Interpret a column `e` as an edge with endpoints `u,v` and endpoint signs

```text
(sigma_u(e), sigma_v(e)) in {+1,-1}^2.
```

Thus an edge may be of type

```text
(+,+),
(+,-),
(-,+),
(-,-).
```

Assume

```text
boxed:
ker_Q(R)=ker_Q(A).
```

Exact-One is equivalent to

```text
R(3x-1)=0,
x in {0,1}^E.
```

Equivalently,

```text
R x = (R1)/3.
```

## 2. Immediate modular gate

Because `R x` is integral for Boolean `x`, a necessary condition is

```text
R1 == 0 mod 3
```

rowwise.

If this fails, return UNSAT immediately.

Assume from now on that

```text
b=(R1)/3
```

is integral.

## 3. Negative-endpoint count

For every original vertex `v`, let

```text
d^-(v)
```

be the number of incident signed edges whose endpoint sign at `v` is `-1`.

For a Boolean edge variable `x_e`, a negative incidence contributes

```text
-x_e = (1-x_e)-1.
```

Therefore if we can represent

```text
x_e
```

at a positive endpoint and

```text
1-x_e
```

at a negative endpoint by ordinary selected graph edges, then the signed balance
at `v` becomes an ordinary degree condition shifted by `d^-(v)`.

The required ordinary factor degree will be

```text
boxed:
f(v)=b_v+d^-(v).
```

## 4. Edge gadgets

We now transform every signed edge independently.

### Type (+,+)

Use one ordinary graph edge between `u` and `v`.

Select it iff

```text
x_e=1.
```

Its selected incidence contributes `x_e` to both endpoints, exactly matching the
signed column.

### Type (-,-)

Again use one ordinary graph edge between `u` and `v`, but interpret its selection
bit as

```text
z_e=1-x_e.
```

At either endpoint

```text
-x_e=z_e-1.
```

The `z_e` part is the ordinary selected-edge contribution and the constant `-1` is
absorbed into `d^-(v)`.

### Type (+,-)

Introduce a new selector vertex

```text
s_e
```

with prescribed factor degree

```text
f(s_e)=1.
```

Connect `s_e` to the positive endpoint `u` and to the negative endpoint `v`.

Interpret

```text
s_e--u selected  <=> x_e=1,
s_e--v selected  <=> x_e=0.
```

Because `s_e` must have factor degree one, exactly one state is chosen.

At `u` the ordinary contribution is `x_e`.
At `v` it is `1-x_e`, which equals the desired negative contribution plus one:

```text
1-x_e = (-x_e)+1.
```

Again the constant is absorbed by `d^-(v)`.

### Type (-,+)

Use the same selector gadget with the endpoint roles reversed.

## 5. Exact degree identity

Let `F` be any selected edge set in the transformed ordinary graph corresponding to
an original Boolean assignment `x`.

At an original vertex `v`, the transformed degree is

```text
deg_F(v)
=
sum_{positive incidences} x_e
+
sum_{negative incidences} (1-x_e).
```

Therefore

```text
deg_F(v)
=
(Rx)_v + d^-(v).
```

Since `Rx=b`, this is exactly

```text
boxed:
deg_F(v)=b_v+d^-(v)=f(v).
```

Conversely, every `f`-factor of the transformed graph determines one state for every
selector and one bit for every direct edge, hence reconstructs a unique original
Boolean assignment satisfying `Rx=b`.

Thus the reduction is bijective at the witness level.

## 6. Theorem SIGNED-GRAPH-F-FACTOR

```text
boxed:
If ker_Q(A)=ker_Q(R) and every column of R has exactly two nonzero entries
from {+1,-1}, then Exact-One reduces exactly to an ordinary graph f-factor
problem of polynomial size.
```

The transformed graph has

```text
|V| + (# mixed-sign edges)
```

vertices and at most

```text
2|E|
```

edges.

The f-factor problem is polynomial, so the whole kernel language is polynomial.

## 7. Special cases

E37 contains several earlier global languages.

### Directed flow / circulation

If every edge has type

```text
(+,-)
```

or

```text
(-,+),
```

then `R` is an oriented graph incidence matrix.  The original system is a bounded
flow / circulation language.

### Unsigned graph factor

If every edge has type

```text
(+,+),
```

then the transformation is the identity and E37 reduces to R5 E36:

```text
f(v)=deg(v)/3.
```

### All-negative unsigned factor

If every edge has type

```text
(-,-),
```

then every original variable is complemented and the problem is again an ordinary
factor problem.

Thus E37 genuinely unifies the flow and f-factor branches in one signed-graphic
language.

## 8. Why this is beyond TU

Signed two-endpoint incidence matrices need not be totally unimodular.

The all-positive triangle is already a determinant-2 example.

Mixed sign patterns can also produce non-TU minors.

Nevertheless E37 remains polynomial because factor structure, not LP integrality,
is the controlling global language.

Therefore the post-E33 hard core cannot be characterized merely as

```text
non-TU.
```

It must avoid broader factorable signed-graphic representations.

## 9. Certificate form

A signed-graph kernel certificate consists of

```text
R,
the endpoint pair and signs for every column,
and an exact rank / kernel-equality certificate showing
ker_Q(R)=ker_Q(A).
```

A verifier checks:

```text
exactly two nonzeros per column,
each nonzero in {+1,-1},
ker_Q(R)=ker_Q(A).
```

It then constructs the ordinary factor instance deterministically.

SAT is certified by the returned f-factor / reconstructed Boolean witness.
UNSAT is certified by the standard factor obstruction returned by the polynomial
f-factor algorithm.

## 10. Updated global-language router

The exact kernel-language layer now contains:

```text
GL0  TU orthogonal representation               -> R5 E33
GL1  small distance-to-TU                        -> R5 E34
GL2  root/tension potential space                -> R5 E32
GL3  unsigned graph-incidence / f-factor         -> R5 E36
GL4  signed two-endpoint graph representation    -> R5 E37
```

These branches should run only after the earlier exact forcing / quotient / gauge
reductions.

## 11. New hard-core requirement

A genuine post-E37 survivor must have no exposed orthogonal representation with

```text
at most two signed endpoint incidences per coordinate column.
```

So its global kernel language must require genuinely higher-order coupling than a
graph edge.

This points to the next structural boundary:

```text
3-NONZERO-PER-COLUMN ORTHOGONAL REPRESENTATIONS.
```

That is exactly where graph-factor structure gives way to hypergraph-factor style
constraints, where NP-hardness can re-enter.

The next theorem target is therefore to determine which special three-endpoint
sign patterns still reduce to polynomial matching/flow structure and which already
contain the full R5 E12 hard carrier.

```text
P_VS_NP = OPEN.
```

Companion finite controls:

```text
experiments/r5_e37_signed_graph_f_factor_kernel.py
```
