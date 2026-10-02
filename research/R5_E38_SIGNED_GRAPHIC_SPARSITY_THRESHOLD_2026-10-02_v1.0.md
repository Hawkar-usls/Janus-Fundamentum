# R5 E38 — Sharp Signed-Graphic Sparsity Threshold

Date: 2026-10-02

Status:
`TWO_NONZERO_SIGNED_COLUMNS_POLYNOMIAL__THREE_POSITIVE_NONZEROS_ALREADY_NP_COMPLETE`

Scientific ceiling:

```text
R5 E37 proves that an orthogonal kernel representation with exactly two
nonzero entries from {+1,-1} in every column is polynomial via f-factor.

This note shows that the next sparsity level already contains the full
square+cubic+linear Exact-One hard carrier:

  three nonzero entries per column,
  all equal to +1,

is NP-complete.

Thus column sparsity two versus three is a sharp complexity boundary for the
unrestricted signed-incidence representation axis.

P_VS_NP = OPEN.
```

## 1. Polynomial side: sparsity two

R5 E37 proves the following exact theorem.

Let

```text
R in {-1,0,1}^{m x n}
```

have exactly two nonzero entries in each column, and assume

```text
ker_Q(R)=ker_Q(A).
```

Then Exact-One for `A` is equivalent to a polynomial-size ordinary graph
`f`-factor instance. Therefore this entire two-endpoint signed-graphic kernel
sector is decidable in deterministic polynomial time.

The proof allows all four endpoint-sign patterns

```text
(+,+), (+,-), (-,+), (-,-).
```

Hence the tractable class is not merely TU or ordinary flow structure; it includes
all signed two-endpoint incidence representations covered by E37.

## 2. Hard side: sparsity three

R5 E12 proves that the following problem is NP-complete.

Input:

```text
A in {0,1}^{n x n}
```

such that

```text
row sum = 3,
column sum = 3,
pairwise row overlap <= 1.
```

Decide whether

```text
A x = 1,
x in {0,1}^n.
```

Now take the orthogonal representation simply to be

```text
R=A.
```

Then trivially

```text
ker_Q(R)=ker_Q(A).
```

Because every column of the E12 carrier has column sum three and is 0/1, every
column of `R` has exactly three nonzero entries, all equal to `+1`.

Therefore the class

```text
R in {0,1}^{m x n},
exactly three +1 entries per column,
Exact-One asks for x in {0,1}^n with R(3x-1)=0
```

already contains the full R5 E12 NP-complete carrier.

Indeed, since `R=A` and `A1=3*1`,

```text
R(3x-1)=0
iff
3Ax-A1=0
iff
Ax=1.
```

Thus:

### Theorem SPARSITY-3-HARD

```text
Exact-One restricted to orthogonal representations with exactly three
nonzero entries per column is NP-hard, even when every nonzero is +1,
the matrix is square, every row also has weight three, and pairwise rows
overlap in at most one column.
```

Membership in NP is immediate, so the class is NP-complete.

## 3. Sharp threshold

Combining E37 and Section 2 gives the exact representation-sparsity boundary

```text
column support <= 2 with signed {+1,-1} endpoints
    -> polynomial via graph f-factor;

column support = 3, even all-positive
    -> NP-complete.
```

Equivalently:

```text
boxed:
2-ENDPOINT SIGNED GRAPH LANGUAGE IS TRACTABLE,
3-ENDPOINT UNRESTRICTED HYPERGRAPH LANGUAGE ALREADY CONTAINS THE HARD CORE.
```

So no theorem of the form

```text
"bounded column support in an orthogonal representation implies polynomial"
```

can extend from support two to support three without additional structure.

## 4. Why this boundary matters

The E32--E37 program progressively enlarged the known polynomial global-kernel
languages:

```text
root/tension potentials,
TU orthogonal spaces,
distance-to-TU backdoors,
unsigned graph f-factors,
signed graph f-factors.
```

E38 shows that this extension has now reached a genuine complexity wall. The next
step cannot be "allow one more endpoint in every column" in full generality.

Any tractable three-endpoint theorem must impose extra structure such as

```text
a small number of exceptional 3-endpoint columns,
a reducible sign pattern,
a bounded-width incidence interaction,
a decomposable hypergraph structure,
or another global normal form.
```

## 5. Router consequence

The global-language layer should now distinguish

```text
GL-S2:
  signed-graphic representation
  -> E37 polynomial;

GL-S3:
  unrestricted 3-endpoint representation
  -> cannot be promoted to polynomial unless P=NP.
```

The correct next parameter is therefore distance from the signed-graphic boundary,
not raw three-endpoint sparsity itself.

A natural exact target is:

```text
SIGNED-GRAPH BACKDOOR SIZE t
=
number of exceptional columns that must be fixed/removed so that the remaining
orthogonal representation has at most two signed endpoint incidences per column.
```

For small `t`, branching on only those exceptional Boolean coordinates should leave
an E37 f-factor instance on every branch.

That FPT theorem is the next R5 target.

```text
P_VS_NP = OPEN.
```
