# R5 E65 — Transpose Asymmetry / Quantized Parity-Defect Firewall

Date: 2026-10-04

Status:
`POST_QUOTIENT_TRANSPOSE_CAN_FLIP_EXACT_ONE__PARITY_DEFECT_IS_QUANTIZED__FIRST_NONZERO_DEFECT_IS_TIGHT_AND_LOCALLY_CONCENTRATED`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

IT REFINES THE POST-QUOTIENT FRONTIER AFTER E64.

THE MAIN RESULT IS A PAIR OF EXACT FIREWALLS:

(1) THE SAME 63x63 TUTTE-12 INCIDENCE CARRIER CAN BE UNSAT IN ONE
    ORIENTATION AND SAT AFTER TRANSPOSITION.

    THEREFORE EVERY DATUM INVARIANT UNDER R -> R^T — INCLUDING RANK,
    NULLITY, SINGULAR VALUES, SMITH NORMAL FORM, DETERMINANT DATA, AND THE
    UNCOLOURED LEVI GRAPH — IS INSUFFICIENT BY ITSELF TO DECIDE EXACT-ONE.

(2) ON THE UNSAT ORIENTATION, THE BINARY PARITY RELAXATION REACHES THE
    FIRST THEORETICALLY POSSIBLE NONZERO DEFECT LEVEL:

        |x| = n/3 + 2,
        t3  = 3,
        energy = 12.

    EVEN MORE STRONGLY, THE THREE DEFECT ROWS ARE MAXIMALLY LOCALIZED:
    THEY ARE EXACTLY THE THREE ROWS IN THE SUPPORT OF ONE SELECTED COLUMN.

    SO 'ONLY THREE LOCAL DEFECTS REMAIN' DOES NOT IMPLY THAT A LOCAL OR
    AUGMENTING-PATH REPAIR TO EXACT-ONE EXISTS.

P_VS_NP = OPEN.
```

## 1. Carrier and orientation

R5 E64 reconstructed the Tutte 12-cage from the standard LCF notation

```text
[17,27,-13,-59,-35,35,-11,13,-53,53,-27,21,57,11,-21,-57,59,-17]^7.
```

Its bipartition has 63 vertices on each side.  Choosing one side as rows and the
other as columns gives a square binary incidence matrix

```text
R in {0,1}^{63 x 63}
```

with

```text
row weight    = 3,
column weight = 3,
linearity     = true,
Levi girth    = 12,
rank_Q(R)     = 49,
nullity_Q(R)  = 14.
```

The companion E64 checker proved for this orientation

```text
ker_Q(R) intersect {-1,2}^63 = empty,
```

hence Exact-One is UNSAT.

The key E65 move is to keep the same carrier and reverse the incidence
orientation:

```text
R -> R^T.
```

## 2. Exact transpose asymmetry

The E65 checker computes the complete two-level kernel search on both matrices.
It obtains

```text
R   : nullity = 14, two-level kernel vectors = 0,
R^T : nullity = 14, two-level kernel vectors = 36.
```

By the E61 equivalence

```text
A x = 1, x in {0,1}^n
iff
exists y in ker_Q(A) intersect {-1,2}^n,
```

we therefore have the exact post-quotient pair

```text
boxed:
R   is Exact-One UNSAT,
R^T is Exact-One SAT.
```

This is not a gadget-inflation phenomenon.  Both are genuine connected
square-cubic-linear quotient carriers on the same 126-vertex Levi graph.

## 3. What transposition preserves

For every square matrix R, transposition preserves or canonically identifies:

```text
rank,
nullity,
determinant,
Smith normal form,
nonzero singular values,
characteristic data of R^T R versus R R^T,
uncoloured bipartite incidence graph,
girth and ordinary graph distance data.
```

In our Tutte-12 pair, even the zero singular multiplicity is identical because
R is square and rank(R)=rank(R^T).

Therefore no decision rule depending only on such transpose-invariant data can
separate the two instances.

This is a stronger post-E64 firewall than merely saying that large nullity does
not imply SAT.

It says:

```text
boxed:
orientation of the two incidence parts contains essential Boolean information.
```

A successful invariant must see which side is the selectable-variable side and
which side is the Exact-One-constraint side.

## 4. External geometric sanity check

The Tutte 12-cage is the point-line incidence graph of the generalized hexagon
of order (2,2).  The two bipartite orientations correspond to the split Cayley
hexagon H(2) and its point-line dual.

The finite-geometry literature independently reports the same asymmetry at the
relevant partition level: a partition of the point set into lines (called a
`distance-2 spread` in that literature) exists in the dual of H(2), while H(2)
itself does not admit such a distance-2 spread.

This is an independent conceptual anchor for the computational transpose split.
The checker does not rely on the external classification.

## 5. Quantized parity defect: universal identity

Let A be any square cubic binary matrix of order n with n divisible by 3, and
let

```text
x in {0,1}^n
```

satisfy the binary syndrome

```text
A x = 1 mod 2.
```

Every row contains either one or three selected columns.  Let t3 be the number
of rows containing three selected columns.

Double-count selected incidences.  Every selected column occurs in exactly
three rows, hence

```text
3 |x| = (n - t3) + 3 t3 = n + 2 t3.
```

Because n is divisible by 3,

```text
2 t3 = 0 mod 3,
```

so

```text
t3 = 3m
```

for an integer m >= 0.  Substituting back gives

```text
boxed:
|x| = n/3 + 2m.
```

Thus parity-coset weights above the Exact-One floor occur in steps of two.

Now define the integer residual energy

```text
E(x) = ||A x - 1||_2^2.
```

For a parity solution, each normal row contributes zero and each 3-row has
residual 2 and contributes 4.  Therefore

```text
E(x) = 4 t3 = 12m.
```

Hence

```text
boxed:
parity defect levels are quantized as
(m, |x|, t3, E) = (m, n/3+2m, 3m, 12m).
```

The Exact-One condition is exactly m=0.

## 6. The first nonzero level is actually attainable

A possible hope after deriving the quantization is that the first positive
level m=1 might be forbidden by connectivity, high girth, linearity, or the
post-quotient geometry.

The Tutte-12 UNSAT orientation kills that hope exactly.

The complete F_2 parity coset has dimension 14, hence 2^14 = 16384 solutions.
The checker enumerates all of them and finds

```text
minimum parity weight = 23,
63/3                  = 21,
weight gap            = 2,
m                     = 1,
t3                    = 3,
energy                = 12.
```

Therefore the universal lower positive gap is tight on a genuine connected
high-girth quotient carrier.

## 7. Exact classification of nearest parity solutions

The same enumeration finds exactly

```text
252
```

minimum-weight parity solutions.

For each such solution x:

```text
* exactly three rows have selected count 3;
* the other 60 rows have selected count 1;
* those three defect rows are exactly the support of one column c;
* column c itself is selected in x.
```

Across all 252 minimizers:

```text
* every one of the 63 columns occurs as the unique defect-star centre;
* each column occurs for exactly four minimum parity solutions.
```

Equivalently, there are exactly

```text
63 distinct localized defect stars,
4 nearest parity solutions per star.
```

This is much stronger than merely saying that the nearest parity solution has
three bad rows.

The three bad rows are as locally concentrated as possible in a linear
3-uniform incidence system: they are all incident with one common selected
column.

## 8. Local-repair firewall

This gives a direct anti-loop theorem.

The following proposed shortcut is false:

```text
If a parity solution differs from Exact-One on only O(1) rows, and those rows
are localized around one hyperedge, then a bounded/local augmenting repair must
exist.
```

The Tutte-12 orientation supplies a counterexample with the smallest possible
nonzero defect:

```text
three bad rows,
one defect star,
energy 12,
no Exact-One solution anywhere in the instance.
```

Thus a repair algorithm cannot be justified from defect count or defect radius
alone.  Any successful repair invariant must also encode the global response of
the rest of the incidence system.

## 9. Transpose SAT control

For R^T, the same parity-coset enumeration reaches

```text
minimum weight = 21 = 63/3,
```

and finds exactly

```text
36
```

Exact-One / two-level-kernel solutions.

So the transpose pair has the same nullity and the same quantized parity
framework, but opposite value of the zero-defect question:

```text
R   : min m = 1,
R^T : min m = 0.
```

This identifies the real decision boundary more sharply than E64:

```text
not nullity,
not singular spectrum,
not high girth,
not a small local parity defect,
but whether the oriented incidence kernel actually hits the two-level cube.
```

## 10. Coding-theory interpretation

R5 E56/E58 already identify the binary syndrome relaxation as a minimum-weight
coset problem:

```text
A Exact-One SAT
iff
min{|x| : A x = 1 mod 2} = n/3.
```

E65 sharpens this for n divisible by 3:

```text
all feasible parity weights are n/3 mod 2,
and the normalized defect is
m = (|x|-n/3)/2 = t3/3 = E/12.
```

This is a highly structured nearest-codeword / syndrome-decoding formulation.
General nearest-codeword and exact decoding problems are known to be NP-hard;
that literature is an anti-loop anchor only.  Our frozen E12 bridge is stronger
for the present family because it already gives the self-contained hardness
route inside the square-cubic-linear Exact-One setting.

## 11. E65 surviving frontier

E65 kills two tempting universal shortcuts:

```text
A. transpose-invariant spectral / rank data decide SAT;
B. a constant, highly localized parity defect is always locally repairable.
```

Both are false on the same 63x63 post-quotient carrier.

The next useful object therefore has to be orientation-sensitive and globally
responsive while remaining compressible enough for a polynomial algorithm.

Concrete E66 candidates:

```text
1. oriented kernel-coordinate sign geometry rather than kernel dimension;
2. a certificate derived from how local defect stars propagate under kernel
   moves;
3. an oriented matroid invariant of the row-vs-column incidence realization;
4. a polynomially computable obstruction separating min-defect m=0 from m=1
   without solving the whole nearest-codeword problem;
5. exact exchange structure among minimum parity representatives.
```

Any E66 candidate must be tested immediately on the transpose pair R,R^T,
because that pair has become a canonical firewall for post-quotient proposals.

## 12. Replay

Companion checker:

```text
experiments/r5_e65_transpose_asymmetry_quantized_defect.py
```

It verifies:

```text
* Tutte-12 R and R^T are square cubic linear, connected, girth 12;
* rational nullity 14 on both orientations;
* R has 0 two-level kernel vectors;
* R^T has 36 two-level kernel vectors;
* complete 2^14 F_2 parity-coset enumeration on R;
* universal quantization identities on every enumerated parity solution;
* min_R |x| = 23, t3=3, energy=12;
* exactly 252 minimum R parity solutions;
* 63 distinct column-support defect stars;
* exactly 4 minimizers per defect-star centre;
* min_{R^T} |x| = 21 and exactly 36 Exact-One solutions.
```

Scientific status remains:

```text
P_VS_NP = OPEN.
```
