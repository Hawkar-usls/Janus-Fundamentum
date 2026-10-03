# R5 E58 — Homogeneous Binary Kernel Maximum-Weight Cap

Date: 2026-10-03

Status:
`GLOBAL_EXACT_REFORMULATION__EXACT_ONE_IFF_BINARY_KERNEL_HITS_ABSOLUTE_2N_OVER_3_WEIGHT_CAP`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A POLYNOMIAL ALGORITHM.

IT SHARPENS E56 BY REMOVING THE AFFINE SYNDROME RIGHT-HAND SIDE ENTIRELY.

FOR EVERY BINARY SQUARE CUBIC CARRIER A,

    A 1 = 1  (mod 2),

SO

    {x : A x = 1} = 1 + ker_F2(A).

FOR EVERY k IN ker_F2(A), EACH INTEGER ROW SUM IS 0 OR 2.  IF t_2(k) IS
THE NUMBER OF ROWS OF SUM 2, THEN

    3 |k| = 2 t_2(k) <= 2n.

THEREFORE EVERY BINARY KERNEL CODEWORD SATISFIES THE ABSOLUTE CAP

    |k| <= 2n/3.

AND

    EXACT-ONE SAT(A)

IFF

    max{|k| : k in ker_F2(A)} = 2n/3.

THE UNIVERSAL PROBLEM CAN THUS BE STATED AS A HOMOGENEOUS MAXIMUM-WEIGHT
CODEWORD ENDPOINT PROBLEM FOR THE SPECIAL (3,3)-REGULAR I+P+Q LDPC FAMILY.

P_VS_NP = OPEN.
```

## 1. Canonical parity point

Let `A` be `n x n`, binary, with every row and column of weight 3.

Over `F_2`,

```text
A 1 = 3 * 1 = 1.
```

So the all-ones vector is always a solution of the E56 parity syndrome.

Therefore the affine parity coset is never empty and has the canonical form

```text
boxed:
C_1(A) = 1 + ker_F2(A).
```

If

```text
x = 1 + k
```

over `F_2`, then coordinatewise `x` is the Boolean complement of `k`, so

```text
boxed:
|x| = n - |k|.
```

Thus E56's minimum syndrome-weight problem is exactly dual to a homogeneous
maximum-weight problem in the binary kernel:

```text
boxed:
d_1(A) = n - w_max(ker_F2(A)).
```

## 2. Absolute kernel weight cap

Take any

```text
k in ker_F2(A).
```

Every row contains three Boolean coordinates, and the row parity is even.  Hence the
integer row sum can only be

```text
0 or 2.
```

Let

```text
t_2(k) = number of rows whose integer sum is 2.
```

Summing all row incidences in two ways gives

```text
3 |k| = 2 t_2(k).
```

Since

```text
t_2(k) <= n,
```

we obtain the universal cap

```text
boxed:
|k| <= 2n/3.
```

This is exact and uses only square cubic regularity.

A small arithmetic corollary is also automatic:

```text
3 |k| = 2 t_2(k)
```

forces

```text
|k| even,
t_2(k) divisible by 3.
```

So every binary kernel codeword has even Hamming weight.

## 3. Exact-One iff the cap is reached

Suppose first that `x` is an Exact-One solution:

```text
A x = 1
```

over the integers.

Set

```text
k = 1 + x
```

over `F_2`, i.e. the Boolean complement of `x`.

Each Exact-One row contains one `x=1` and therefore exactly two `k=1` coordinates.
Hence

```text
A k = 0 mod 2
```

and every row contributes `2`, so

```text
t_2(k)=n.
```

Therefore

```text
3 |k|=2n,
```

or

```text
|k|=2n/3.
```

Conversely, suppose a kernel codeword reaches the cap:

```text
|k|=2n/3.
```

Then

```text
3|k|=2 t_2(k)
```

forces

```text
t_2(k)=n.
```

So every row contains exactly two ones of `k`.

Its complement

```text
x=1+k
```

therefore has exactly one one in every row, i.e.

```text
A x=1
```

over the integers.

Thus

```text
boxed:
Exact-One SAT(A)
iff
max_{k in ker_F2(A)} |k| = 2n/3.
```

No approximation or one-way implication is involved.

## 4. Permutation form

For

```text
A=I+P+Q,
```

a kernel word satisfies

```text
k+Pk+Qk=0  (mod 2).
```

If `K=supp(k)`, every point belongs to an even number of the three support images

```text
K, P(K), Q(K).
```

With only three sets, every point therefore belongs either

```text
0 times
```

or

```text
2 times.
```

If `U_2(K)` is the set of points covered twice, then

```text
3 |K| = 2 |U_2(K)|.
```

So

```text
|K| <= 2n/3,
```

and equality holds iff

```text
U_2(K)=V,
```

i.e. every point belongs to exactly two of `K,P(K),Q(K)`.

Taking complements gives three pairwise-disjoint one-cover classes, exactly the E56
permutation tiling.

## 5. Linear-carrier graph meaning

Assume additionally that the square cubic carrier is linear, so

```text
G=A^T A-3I
```

is the simple 6-regular conflict graph.

For a kernel support `K`, each active row contains exactly two selected columns.
Therefore every selected column has exactly one selected mate in each of its three
incident rows.

Because linearity prevents the same mate from being repeated in two rows, the induced
selected conflict structure is cubic:

```text
boxed:
G[K] is 3-regular for every nonzero binary kernel codeword K.
```

At the maximum cap

```text
|K|=2n/3,
```

every one of the `n` rows is active, and the complement

```text
S=V\K
```

is the required independent Exact-One set of size `n/3`.

Thus the universal target can also be read as:

```text
find the largest kernel-induced cubic substructure;
SAT iff it reaches 2n/3 vertices.
```

This is a structural interpretation, not yet an algorithm.

## 6. Exact duality with E56

E56 defined

```text
d_1(A)=min{|x| : A x=1 mod 2}.
```

E58 defines

```text
w_max(A)=max{|k| : A k=0 mod 2}.
```

Since the syndrome coset is `1+ker(A)`, we have the exact identity

```text
boxed:
d_1(A)+w_max(A)=n.
```

Therefore the two endpoint criteria are the same theorem in dual coordinates:

```text
E56:
  SAT iff d_1(A)=n/3.

E58:
  SAT iff w_max(A)=2n/3.
```

The E58 form is cleaner because it is homogeneous and requires no syndrome vector.

## 7. Complexity localization

The E12 reduction already proves NP-hardness for the frozen square+cubic+linear carrier
family.

Combined with E58, this means the hard core can be stated exactly as the endpoint
question

```text
DOES THE SPECIAL BINARY CODE

    C(A)=ker_F2(A)

CONTAIN A CODEWORD OF WEIGHT 2n/3?
```

where `A` is simultaneously

```text
square,
row weight 3,
column weight 3,
linear in the E12 family,
and normalizable to I+P+Q.
```

General maximum-weight codeword problems are known to be computationally hard; that
literature is useful as anti-loop, but the research target here is narrower and more
structured.

A relevant general reference is:

```text
Toshiya Itoh (2000), Approximating the Maximum Weight of Linear Codes is APX-Complete,
IEICE Transactions on Fundamentals E83-A(4), 606-613.
```

The E12 bridge is stronger for our purposes because it localizes the hardness inside
our exact carrier family rather than appealing only to a generic code.

## 8. New universal target after E58

The arbitrary noncommuting `(P,Q)` goal can now be frozen as:

```text
INPUT:
  A=I+P+Q from a simple square cubic carrier.

POLYNOMIAL LINEAR STEP:
  compute a basis of C=ker_F2(A).

UNRESOLVED UNIVERSAL STEP:
  determine in polynomial time whether C contains a word of weight 2n/3,
  and construct one when it exists.
```

A valid P=NP route must exploit structure beyond generic linear-code decoding.

High-value next attacks are therefore:

```text
1. derive additional identities satisfied by every codeword of C(A) from the
   permutation generators P,Q;

2. determine whether C(A) admits a canonical polynomial decomposition into blocks for
   which maximum weight is additive;

3. search for a polynomial certificate that the 2n/3 cap is unattainable without
   enumerating codewords;

4. combine the binary cap with the real two-level-kernel and ternary full-support views
   to force a common discrete extremizer.
```

Until such a mechanism exists:

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e58_kernel_max_weight_cap.py
```
