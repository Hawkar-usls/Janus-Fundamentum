# R5 E69 — Large-Nullity Torus / Algebraic-Compression Firewall

Date: 2026-10-04

Status:
`LARGE_BINARY_NULLITY_DOES_NOT_FORCE_BOUNDED_OR_LOG_GRAPH_WIDTH__TORUS_FAMILY_HAS_D_EQ_SQRT_N_MINUS_1__ALGEBRAIC_COMPRESSION_NOT_SEPARATOR_DP`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

THE TARGET REMAINS A UNIVERSAL, PROVABLE POLYNOMIAL-TIME ALGORITHM FOR THE
SQUARE-CUBIC-LINEAR EXACT-ONE HARD CORE.  P_VS_NP REMAINS OPEN.

E69 TESTS THE POST-E68 DICHOTOMY HOPE

    SMALL BINARY NULLITY -> E61 ENUMERATION,
    LARGE BINARY NULLITY -> FORCED POLYNOMIAL STRUCTURAL DECOMPOSITION.

THE SIMPLE SEPARATOR/WIDTH VERSION OF THE SECOND IMPLICATION IS FALSE.
A CONNECTED INFINITE TORUS FAMILY HAS

    dim_F2 ker(A) = Theta(sqrt(n))

AND LEVI TREEWIDTH Omega(sqrt(n)).

HOWEVER THE SAME FAMILY IS EXACTLY SOLVABLE BY A GLOBAL ALGEBRAIC/SYMMETRY
COMPRESSION.  THIS SHOWS WHAT A LARGE-NULLITY BRANCH WOULD HAVE TO LOOK LIKE:
NOT GENERIC SMALL-SEPARATOR DP, BUT A STRONGER ALGEBRAIC OR QUOTIENT STRUCTURE.
```

## 1. Anti-loop from Fundamentum

The following earlier results are binding.

* E58:

  ```text
  Exact-One SAT
  iff max_{k in ker_F2(A)} |k| = 2n/3.
  ```

* E61:

  ```text
  d = dim ker_F2(A) = O(log n)
  -> exact 2^d poly(n) enumeration is polynomial.
  ```

* E63:

  Raw gadget nullity is not a reliable hardness parameter because bounded gadget
  substitutions can inflate it linearly and exact quotienting can remove the
  inflation.

* E64-E68:

  Connected post-quotient carriers can have nontrivial nullity; low-order spectral,
  exchange, moment and degree-2 SDP information does not universally decide the
  hard core.

Therefore E69 works directly with a genuine connected post-quotient family.

## 2. Open-literature anti-loop

Two external bodies of work are relevant.

### 2.1 Bounded branch-width is algorithmically useful, but no converse from nullity is known

For finite-field represented matroids, bounded branch-width/decomposition width
supports polynomial/FPT dynamic programming and MSO model checking.  See, e.g.

* P. Hlineny, "A Parametrized Algorithm for Matroid Branch-Width",
  SIAM J. Comput. 35 (2006), and subsequent finite-field branch-width work;
* D. Kral, "Decomposition width of matroids", Discrete Applied Mathematics 160
  (2012), 913-923;
* J. Jeong, E. J. Kim, S. Oum, "Finding Branch-Decompositions of Matroids,
  Hypergraphs, and More", SIAM J. Discrete Math. 35 (2021).

These results justify testing width as an algorithmic route.  They do **not** say
that a large nullspace forces small branch-width/treewidth.  E69 supplies an
explicit counterexample to the analogous graph-width hope inside our exact
square-cubic-linear carrier class.

### 2.2 The polynomial `1+X+Y` is a known algebraic-dynamics object

The binary algebraic subshift annihilated by

```text
1 + X + Y
```

is the Ledrappier/3-dot system.  The object itself is classical; E69 is not
claiming invention of that polynomial dynamical system.  A modern reference is
J. Kari and E. Moutot, "Nivat's conjecture and pattern complexity in algebraic
subshifts", Theoretical Computer Science 777 (2019), which explicitly defines
the Ledrappier subshift by the annihilator `1+X+Y` over F2.

E69 uses a finite torus specialization of that known algebraic object as a
firewall for our rank/nullity dichotomy.

## 3. The torus carrier

Fix

```text
m >= 3
```

and index both rows and columns by

```text
G_m = Z_m x Z_m.
```

Define the binary matrix `A_m` by

```text
row(i,j) = {(i,j), (i+1,j), (i,j+1)}
```

with coordinates modulo `m`.

Equivalently, on functions on `G_m`,

```text
A_m = I + P_x + P_y.
```

Every row has weight three.  Translation invariance gives column weight three.
The six nonzero ordered differences of the local support

```text
{(0,0),(1,0),(0,1)}
```

are distinct for `m>=3`, so two distinct row supports meet in at most one column;
by duality the same holds for columns.  Thus `A_m` is square-cubic-linear.

The Levi graph is connected because the two translation directions generate
`Z_m x Z_m`.

## 4. Exact binary nullity on `m=2^r-1`

Take

```text
m = 2^r - 1.
```

Then `m` is odd, so `X^m-1` and `Y^m-1` are separable over the splitting field
`F_{2^r}`.  Extend scalars from `F2` to `F_{2^r}`.  Rank and nullity do not change
under field extension.

The group algebra diagonalizes in the character basis.  A character indexed by

```text
(alpha,beta) in (F_{2^r}^*)^2
```

has eigenvalue

```text
1 + alpha + beta.
```

Because `F_{2^r}^*` has order `m`, every nonzero field element is an `m`th root
of unity.  Therefore

```text
1+alpha+beta=0
```

with `alpha,beta` both nonzero is equivalent to

```text
beta = 1+alpha,
alpha in F_{2^r} \ {0,1}.
```

There are exactly

```text
2^r - 2 = m-1
```

such characters.  Hence

```text
boxed:
dim_F2 ker(A_m) = m-1.
```

Since

```text
n=m^2,
```

we obtain

```text
boxed:
d = sqrt(n)-1.
```

This is already far above the E61 logarithmic-enumeration regime.

## 5. Large nullity does not force bounded/log graph width

In the Levi graph, contract every natural identity-matching edge

```text
row(i,j) -- column(i,j).
```

The two remaining incidences from that row become exactly

```text
(i,j)--(i+1,j),
(i,j)--(i,j+1).
```

Thus the contraction minor is

```text
C_m square C_m.
```

The toroidal grid contains an ordinary `m x m` grid after deleting wrap edges,
and the `m x m` grid has treewidth `m` (up to the standard endpoint convention).
Treewidth is minor-monotone, so in particular

```text
boxed:
tw(Levi(A_m)) = Omega(m) = Omega(sqrt(n)).
```

Therefore the naive implication

```text
large nullity -> bounded/logarithmic Levi-treewidth -> polynomial separator DP
```

is false even on connected square-cubic-linear post-quotient carriers.

This does not rule out every possible matroidal or algebraic decomposition.
It specifically kills the simple graph-separator version of the E69 dichotomy.

## 6. Exact kernel words are cubic even-sections

Let `H_A` be the 3-uniform hypergraph whose vertices are columns of `A` and whose
hyperedges are row supports.

For a binary word `k` and

```text
U = supp(k),
```

we have

```text
A k = 0 mod 2
```

if and only if every row-hyperedge meets `U` in an even number of points.  Since
row size is three, the only possibilities are

```text
0 or 2.
```

Now keep the hyperedges meeting `U` in two points and replace each by the pair of
selected points it contains.  Every selected point belongs to exactly three
row-hyperedges, and each such hyperedge must contain exactly one other selected
point.  Therefore the resulting ordinary graph on `U` is cubic.  Linearity of
`A` makes it simple.

Hence

```text
boxed:
k in ker_F2(A)
iff supp(k) is a cubic even-section of H_A.
```

Let `D(k)` be the number of row-hyperedges disjoint from `U`.  The other `n-D`
hyperedges become edges of the cubic section.  Double counting incidences gives

```text
3|U| = 2(n-D).
```

Therefore

```text
D = 0 mod 3,
|k| = 2n/3 - 2D/3.
```

Combining with E58:

```text
boxed:
Exact-One SAT
iff there exists a kernel cubic even-section with D=0,
i.e. one that uses every row-hyperedge.
```

The E65 quantized defect has the exact combinatorial interpretation

```text
m_defect = D/3.
```

This is a new structural normalization of the top-shell problem; it does not by
itself give an algorithm.

## 7. The torus family is nevertheless algebraically compressible

The family above has large nullity and large Levi treewidth, but Exact-One is
still trivial to decide from `m`.

Every Exact-One solution selects exactly

```text
n/3 = m^2/3
```

columns.  Hence `3|m` is necessary.

If `3|m`, define

```text
x_(i,j) = 1 iff i-j = 0 mod 3.
```

Because the three columns in row `(i,j)` have residues

```text
(i-j), (i-j)+1, (i-j)-1 mod 3,
```

exactly one is selected.  Thus the condition is sufficient.

So

```text
boxed:
A_m is Exact-One SAT iff 3 divides m.
```

For the frozen family `m=2^r-1`,

```text
3 | (2^r-1) iff r is even,
```

hence

```text
boxed:
SAT iff r is even.
```

This is the positive lesson of E69: a large-nullity/high-width branch can still
collapse polynomially by **global algebraic structure**.  Separator width is not
the only possible compression mechanism.

## 8. Hardness-bridge control

The companion checker also replays the frozen E17/E12 `q=6` RXC3 source.  Its
binary nullity is zero, so E58 immediately certifies UNSAT.  E69 does not replace
or weaken the E12/RXC3 hardness bridge.

More importantly, the torus family is highly translation-structured and is not
claimed to be a hard family.  It must not be used as evidence that arbitrary
large-nullity quotients admit the same Fourier/group-algebra compression.

## 9. Consequence for the universal dichotomy

The post-E68 program must now be sharpened from

```text
large nullity -> small separator
```

to something like

```text
small nullity
    -> E61 enumeration,

large nullity + compressible dependency algebra
    -> polynomial quotient/Fourier/recurrence solver,

large nullity without such compression
    -> THIS is the unresolved universal frontier.
```

A real P=NP route must prove that the third case is empty, or provide a separate
polynomial algorithm for it.

The next useful target is therefore to study the **dependency algebra of the
left/right kernel**, not only its dimension.  Natural quantities to test include

```text
* support growth of kernel generators;
* orbit/module structure of row dependencies;
* whether the kernel admits a bounded-description recurrence;
* whether large nullity forces many low-complexity even-sections;
* whether those even-sections generate a polynomial-size quotient algebra.
```

Every proposed statement must be tested first against E12/RXC3 and then against
non-gadget connected controls such as E64-E69.

## 10. Replay

Companion checker:

```text
experiments/r5_e69_nullity_structure_torus_firewall.py
```

It verifies on `r=2,3,4,5`, i.e. `m=3,7,15,31`:

```text
* square/cubic/linear incidence;
* Levi connectivity;
* contraction to C_m square C_m;
* exact binary nullity m-1;
* cubic even-section structure for every computed kernel-basis word;
* explicit Exact-One cover for 3|m;
* divisibility obstruction for 3 not dividing m;
* E58 top-shell witness when SAT;
* frozen E17 q=6 source nullity control.
```

Scientific status remains:

```text
P_VS_NP = OPEN.
```
