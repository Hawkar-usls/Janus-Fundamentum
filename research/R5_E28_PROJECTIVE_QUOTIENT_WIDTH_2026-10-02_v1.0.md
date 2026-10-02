# R5 E28 — Projective-Quotient Width Terminal

Date: 2026-10-02

Status:
`EXACT_FPT_PROJECTIVE_QUOTIENT_ELIMINATION__E26_E27_UNIFIED__E16_WIDTH_TWO`

Scientific ceiling:

```text
THIS NOTE TURNS THE R5 E27 "BOUNDED ADHESION" IDEA INTO AN EXECUTABLE
EXACT ROUTER BRANCH.

AFTER R5 E18 KERNEL-PROJECTIVE PREPROCESSING, EVERY UNFORCED PROJECTIVE
CLASS CARRIES ONE BOOLEAN BIT.  THE ORIGINAL SOURCE THEREFORE COLLAPSES
TO A FINITE BOOLEAN CSP ON THE FREE PROJECTIVE CLASSES.

ANY EXPLICIT ELIMINATION ORDER OF WIDTH w SOLVES THIS QUOTIENT CSP IN
O(2^w poly(n)) TIME.

ON THE R5 E16 k-BLOCK RING,
  q = 2k+1 = Theta(n)
BUT THE PROJECTIVE QUOTIENT HAS ELIMINATION WIDTH EXACTLY 2.

SO E16 IS CLOSED BY A CONSTANT-WIDTH QUOTIENT EVEN THOUGH PROJECTIVE
DIVERSITY IS LINEAR.

THIS DOES NOT PROVE A UNIVERSAL POLYNOMIAL BOUND ON QUOTIENT WIDTH.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be a square+cubic+linear Exact-One source and let

```text
K = ker_Q(A).
```

Choose a basis matrix

```text
B in Q^{n x d},
col(B)=K,
```

and write `b_i` for its coordinate rows.

R5 E18 partitions nonzero rows into projective classes.  If

```text
b_j = lambda b_i,
```

then every centered Boolean witness obeys

```text
y_j = lambda y_i,
y_i,y_j in {-1,2}.
```

The only admissible ratios are

```text
1, -2, -1/2.
```

The latter two force the Boolean pair.  Therefore after exhaustive KPROJ forcing,
any projective class that remains genuinely free can contain only equal kernel
rows:

```text
b_i=b_j  for all i,j in the free class.
```

Hence every free projective class carries exactly one Boolean bit.

## 2. Exact projective quotient CSP

Let the free classes be

```text
C_1,...,C_q
```

and introduce one Boolean variable

```text
u_a in {0,1}
```

for each class.

Substitute all KPROJ-forced original variables and replace every unforced original
variable `x_i` by the bit `u_a` of its free class.

Each original Exact-One row

```text
x_i+x_j+x_k=1
```

becomes an exact Boolean relation involving at most three quotient bits, with
possible repeated occurrences or fixed constants.

Thus the original instance is exactly equivalent to a bounded-arity Boolean CSP

```text
Q(A)
```

on `q` projective variables.

No relaxation is introduced: every quotient assignment lifts uniquely to all
unforced original variables, and every original witness projects to a quotient
assignment.

Therefore

```text
boxed:
A is Exact-One SAT
iff
Q(A) is SAT.
```

## 3. Interaction graph and certified elimination width

Define the projective quotient interaction graph `H_A`:

```text
vertices = free projective classes,
edge ab  = some surviving quotient constraint contains both u_a and u_b.
```

Take any explicit elimination order

```text
pi=(v_1,...,v_q).
```

When eliminating `v_t`, connect all still-active neighbors of `v_t` into a clique.
Let

```text
w(pi)
```

be the maximum number of active neighbors seen at an elimination step.

This width is directly checkable in polynomial time from the displayed order.
There is no need to know whether the order is globally optimal.

## 4. Exact variable elimination theorem

Because every quotient variable is Boolean, a factor whose active scope has at most
`w+1` variables has at most

```text
2^(w+1)
```

entries.

Eliminate variables in the certified order.  At each step:

```text
1. collect all factors containing v_t;
2. join them on their common variables;
3. existentially eliminate v_t;
4. retain the resulting factor on the active neighbors.
```

If the certified width is `w`, all intermediate tables have size

```text
O(2^(w+1)).
```

Therefore:

### Theorem PQ-WIDTH

Given `A` and any explicit quotient elimination order `pi`, Exact-One is decidable
exactly in

```text
O(2^w poly(n)),
w=w(pi).
```

SAT reconstruction is obtained by storing backpointers.  UNSAT is witnessed by the
empty final factor together with the quotient construction and elimination trace.

Consequences:

```text
w=O(1)      -> polynomial,
w=O(log n)  -> polynomial,
w=q         -> recovers the crude R5 E26 O(2^q poly(n)) envelope.
```

A polynomial heuristic may be used to produce a candidate order.  Soundness does
not depend on heuristic quality: the width of the returned order is verified
exactly before the branch is used.

## 5. Symbolic quotient of the R5 E16 ring

Recall the E16 `k`-block ring.  In block `b`, label the nine local variables by

```text
(i,j) in Z_3 x Z_3.
```

Its exact kernel may be parametrized by one global value `h` and one local value
`a_b` per block:

```text
j-i == 0 mod 3 :  a_b,
j-i == 1 mod 3 :  h,
j-i == 2 mod 3 : -h-a_b.
```

The redirected E16 incidence is exactly what forces the residue-1 value `h` to be
common across all blocks, while the other degree of freedom remains block-local.
This gives the known

```text
nullity_Q(A_k)=k+1.
```

Hence the exact projective classes are:

```text
H   = all 3k variables with j-i == 1 mod 3,
A_b = the three variables in block b with j-i == 0 mod 3,
B_b = the three variables in block b with j-i == 2 mod 3.
```

For `k>=2` these functionals are pairwise nonproportional across distinct displayed
classes.  Therefore

```text
q=1+2k,
```

recovering R5 E27.

## 6. Every E16 source row becomes one quotient Exact-One triple

Every unchanged toroidal row contains one variable from each residue class.
The redirected special row also contains exactly

```text
A_b,
B_b,
H.
```

Therefore all nine source rows of block `b` collapse to the same quotient relation

```text
ExactOne(H,A_b,B_b).
```

The whole quotient CSP is exactly

```text
for b=0,...,k-1:
    H + A_b + B_b = 1.
```

So the quotient interaction graph consists of `k` triangles sharing one common hub
`H`.

Equivalently it is a windmill graph with

```text
q=2k+1 vertices,
3k edges,
deg(H)=2k,
deg(A_b)=deg(B_b)=2.
```

## 7. Exact width and witness count

Eliminate, for each block, one wing and then the other, leaving the hub last.
At every wing elimination there are at most two active neighbors.
Therefore

```text
boxed:
w=2.
```

The companion checker independently runs a polynomial min-degree elimination rule
and obtains width exactly two for every tested `k=2,...,12`.

The quotient also immediately reproduces the E16 witness count:

```text
H=1:
  A_b=B_b=0 for every block
  -> 1 witness.

H=0:
  exactly one of A_b,B_b is 1 independently in every block
  -> 2^k witnesses.
```

Hence

```text
boxed:
#ExactOne(A_k)=2^k+1.
```

This recovers the E16 result through the new projective quotient language.

## 8. Why E28 is stronger than E26 and E27 separately

R5 E26 used only the number `q` of free projective classes.
R5 E27 showed `q` may be linear while small interfaces still make the instance
easy.

E28 unifies both facts:

```text
q measures the number of quotient variables;
w measures the interaction complexity among them.
```

The true exact cost is controlled by the latter whenever a narrow elimination order
is exposed.

Known controls now read:

```text
E25 torus:
  q=O(1), so already trivial under E26.

E16 ring:
  q=Theta(n), but quotient width w=2.

E17 hardness gadget:
  local gauge quotient must run first; then the effective quotient is analyzed.

E19 Paley quotient:
  q=55 with no pairwise collapse, but KLOC-3 rejects before width matters.
```

## 9. Row-space circuit duality

Let `c in Q^n`.  Since the columns of `B` span `ker_Q(A)`,

```text
c^T B=0
iff
c orthogonal to ker_Q(A)
iff
c in row_Q(A).
```

Therefore minimal dependencies among kernel coordinate rows are exactly minimal
support nonzero vectors of the rational row space of `A`.

This identifies the E20--E22 long-circuit realization problem with a carrier
row-space distance problem:

```text
long first kernel obstruction
=
large minimum support of a new rational row-space relation beyond the already
compatible source triples and propagated relations.
```

For square+cubic+linear `A`, this is a code-like invariant of the cubic bipartite
Levi carrier itself.

This reformulation is useful for the next firewall hunt because it lets searches
operate directly on `A` instead of repeatedly materializing every kernel
projection.

## 10. Updated hard core

A genuine post-E28 survivor must now have simultaneously:

```text
large free projective diversity q,
large certified quotient elimination width,
no bounded-interface decomposition,
large effective kernel after gauge quotient,
no KPROJ forcing/equality reduction,
no KLOC-3/4 obstruction,
integer feasibility,
no source-aligned/clique obstruction,
no commuting/near-commuting normal form,
and no known compact trade parametrization.
```

The immediate firewall target is therefore sharper than E27:

```text
HIGH-q / HIGH-PQ-WIDTH CARRIER HUNT.
```

The row-space duality above provides a second simultaneous target:

```text
seek high-width carriers whose rational row space has no short incompatible
relations beyond the native source triples.
```

If such a family exists, it becomes the first genuine high-description trade core.
If every candidate collapses under quotient width or a short row-space relation,
that pattern motivates the next structural theorem but is not itself a proof.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e28_projective_quotient_width.py
```
