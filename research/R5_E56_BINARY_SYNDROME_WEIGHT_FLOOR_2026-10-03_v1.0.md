# R5 E56 — Binary Syndrome Weight Floor / Permutation Tiling Defect

Date: 2026-10-03

Status:
`GLOBAL_EXACT_REFORMULATION__SQUARE_CUBIC_EXACT_ONE_IS_THE_N_OVER_3_COSET_WEIGHT_FLOOR`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A POLYNOMIAL ALGORITHM.

IT REPLACES THE POST-E55 LOCAL SWITCH4/FREE8 VIEW BY A GLOBAL EXACT
OPTIMIZATION IDENTITY VALID FOR EVERY BINARY SQUARE CUBIC CARRIER.

LET A BE n x n WITH EVERY ROW AND COLUMN OF WEIGHT 3.  DEFINE THE BINARY
SYNDROME COSET

    C_1(A) = { x in F_2^n : A x = 1 }.

FOR EVERY BOOLEAN REPRESENTATIVE x IN C_1(A), IF t_3(x) IS THE NUMBER OF
ROWS WHOSE INTEGER SUM IS 3, THEN

    3 |x| = n + 2 t_3(x).

THEREFORE

    |x| >= n/3,

AND

    A x = 1 OVER THE INTEGERS

IFF

    x in C_1(A) AND |x| = n/3.

EQUIVALENTLY, IF

    d_1(A) = min{|x| : x in C_1(A)},

THEN EXACT-ONE SAT HOLDS IFF

    d_1(A) = n/3.

FOR A = I + P + Q, THE SAME STATEMENT IS A PERMUTATION-TILING DEFECT:
AMONG PARITY SOLUTIONS, EACH POINT IS COVERED EITHER ONCE OR THREE TIMES
BY THE THREE PERMUTED COPIES OF THE SUPPORT.  EXACT-ONE IS EXACTLY ZERO
TRIPLE OVERLAP.

P_VS_NP = OPEN.
```

## 1. Setup

Let

```text
A in {0,1}^{n x n}
```

be square cubic:

```text
every row has exactly 3 ones,
every column has exactly 3 ones.
```

For a Boolean vector

```text
x in {0,1}^n
```

write

```text
w(x)=|x|.
```

The original Exact-One target is

```text
A x = 1
```

over the integers.

Now forget the exact integer row sums and keep only parity:

```text
A x = 1  (mod 2).
```

This parity system is a linear system over `F_2` and can be solved / parameterized
by Gaussian elimination in polynomial time.

The remaining question is not feasibility of the parity system.  It is whether its
affine solution coset contains a representative at the exact global weight floor.

## 2. Exact weight-defect identity

Take any Boolean `x` satisfying

```text
A x = 1  (mod 2).
```

Each row of `A` contains exactly three Boolean variables.  Hence its integer row sum
is in

```text
{0,1,2,3}.
```

Odd parity forces that row sum to be either

```text
1 or 3.
```

Let

```text
t_3(x) = number of rows whose integer sum is 3.
```

Summing all integer row sums in two ways gives the theorem.

By rows,

```text
sum_i (A x)_i
  = (n-t_3(x))*1 + t_3(x)*3
  = n + 2 t_3(x).
```

By columns, every selected column occurs in exactly three rows, so

```text
sum_i (A x)_i = 3 |x|.
```

Therefore

```text
boxed:
3 |x| = n + 2 t_3(x).
```

Equivalently,

```text
boxed:
|x| = n/3 + (2/3) t_3(x).
```

This identity is exact, not a bound or relaxation.

## 3. Exact-One is exactly the parity-coset floor

Because

```text
t_3(x) >= 0,
```

we obtain the universal lower bound

```text
|x| >= n/3
```

for every Boolean parity solution.

Equality holds iff

```text
t_3(x)=0,
```

which means every row has integer sum exactly one.

Thus

```text
boxed:
A x = 1 over Z
iff
A x = 1 over F_2 and |x|=n/3.
```

Define

```text
d_1(A)=min{|x| : x in {0,1}^n, A x = 1 mod 2},
```

with `d_1(A)=+infinity` if the parity coset is empty.

Then

```text
boxed:
Exact-One SAT(A)
iff
n is divisible by 3 and d_1(A)=n/3.
```

Moreover, whenever the parity coset is nonempty, the minimum number of triple-covered
rows is recovered exactly from the minimum coset weight:

```text
boxed:
t_3,min = (3 d_1(A)-n)/2.
```

So the optimization gap above `n/3` is not merely correlated with Exact-One failure;
it measures the exact number of unavoidable `3` rows at an optimum parity solution.

## 4. Permutation form A = I + P + Q

For a square cubic carrier, 3-regular bipartite incidence gives a decomposition into
three perfect matchings.  Normalize one matching to obtain

```text
A = I + P + Q,
```

where `P,Q` are permutation matrices, with the usual simple-carrier condition that the
three 1-positions in each row are distinct.

Let

```text
S = supp(x).
```

Under matrix-action notation, the parity equation becomes

```text
1_S XOR 1_{P(S)} XOR 1_{Q(S)} = 1_V.
```

Equivalently,

```text
boxed:
S XOR P(S) XOR Q(S) = V.
```

Therefore every point belongs to an odd number of the three sets

```text
S, P(S), Q(S).
```

There are only three sets, so every point belongs either

```text
exactly once
```

or

```text
exactly three times.
```

Let the triple-overlap defect be

```text
T(S)=S intersect P(S) intersect Q(S).
```

Then `T(S)` is exactly the set of triple-covered points, and the same count gives

```text
boxed:
3 |S| = n + 2 |T(S)|.
```

Hence

```text
boxed:
Exact-One
iff
there exists a parity solution S with T(S)=empty
iff
there exists a parity solution S with |S|=n/3.
```

At zero defect the three sets are pairwise disjoint and cover `V`, so the original
problem can be written exactly as the permutation tiling condition

```text
boxed:
V = S disjoint_union P(S) disjoint_union Q(S).
```

No commutativity of `P,Q` is assumed.

## 5. Quadratic overlap form

Inside the parity coset, a point belongs to two of the three support images iff it
belongs to all three; a pure two-fold overlap would violate odd parity.

Therefore

```text
|S intersect P(S)|
+ |S intersect Q(S)|
+ |P(S) intersect Q(S)|
= 3 |T(S)|.
```

For indicator vectors this is

```text
boxed:
Phi(x)
 = <x,Px> + <x,Qx> + <Px,Qx>
 = 3 t_3(x),
```

subject to

```text
x + P x + Q x = 1  (mod 2).
```

So the universal arbitrary-`(P,Q)` target can equivalently be stated as

```text
find a point of the affine F_2 solution space with Phi(x)=0.
```

This is a global quadratic defect formulation.  It is not a local claw classification.

## 6. Relation to syndrome decoding

The problem

```text
minimize |x|
subject to A x = 1 (mod 2)
```

is a fixed-syndrome minimum-weight decoding / coset-leader problem.

General syndrome decoding is classically NP-complete, and modern coding literature
continues to treat minimum-weight syndrome representatives as the central hard object.
The special matrices here are much more structured: square, row-weight 3, column-weight
3, and after matching normalization exactly `I+P+Q`.

That structure is therefore where any universal polynomial closure would have to enter.
The present theorem does not import a generic decoding algorithm; it identifies the exact
quantity that such an algorithm must compute on the frozen carrier family.

Useful external anti-loop references:

```text
Berlekamp, McEliece, van Tilborg (1978), On the inherent intractability of certain
coding problems.

Zajac (2025), Polynomial reduction from syndrome decoding problem to regular decoding
problem, Designs, Codes and Cryptography 93, 1777-1793.
DOI: 10.1007/s10623-025-01567-2.
```

## 7. Why E56 changes the search target

R5 E55 says the frozen E12 hardness bridge needs only the local types

```text
SWITCH4 + FREE8.
```

E56 now gives a representation in which those local types disappear entirely from the
statement of the hard core.

The universal target is:

```text
INPUT:
  arbitrary simple permutation pair (P,Q).

LINEAR STAGE:
  compute the affine parity coset
      C = {x : x+Px+Qx=1 mod 2}.

NONLINEAR STAGE:
  determine whether
      min_{x in C} |x| = n/3,
  equivalently whether
      min_{x in C} Phi(x) = 0.
```

The linear stage is polynomial already.

The entire unresolved difficulty is now isolated in one global operation:

```text
POLYNOMIAL EXACT COSET-LEADER / ZERO-DEFECT EXTRACTION
FOR THE (3,3)-REGULAR I+P+Q FAMILY.
```

That is a cleaner universal research target than continuing to classify more local
neighborhood types.

## 8. Immediate next attacks

High-value directions after E56 are global, not subclass catalogues:

```text
A. Find a structural invariant of the affine parity kernel generated by I+P+Q that
   forces / forbids reaching the n/3 weight floor.

B. Determine whether the quadratic defect Phi becomes a tractable quadratic form after
   an exact polynomial change of coordinates on ker_F2(I+P+Q).

C. Search for a canonical decomposition of the parity coset under the noncommuting
   permutation action which makes minimum defect additive across polynomially many
   blocks.

D. Combine the binary weight-floor form with the independent ternary full-support form
      A r = 1, r_i != 0 over F_3,
   and look for a cross-field invariant that eliminates the Boolean search rather than
   merely restating it.
```

The forbidden move is to treat Gaussian elimination alone as a solution: it gives the
affine parity coset but not its minimum-weight representative.

Likewise, generic syndrome-decoding heuristics do not satisfy the required universal
polynomial proof burden.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e56_binary_syndrome_weight_floor.py
```
