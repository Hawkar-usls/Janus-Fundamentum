# R5 E26 — Kernel-Projective Diversity Terminal

Date: 2026-10-02

Status:
`EXACT_FPT_PROJECTIVE_CLASS_TERMINAL__TRADE_DESCRIPTION_COMPLEXITY_FORMALIZED__E25_TORUS_COMPRESSED`

Scientific ceiling:

```text
THIS NOTE FORMALIZES ONE EXACT NOTION OF THE "TRADE DESCRIPTION COMPLEXITY"
SUGGESTED BY R5 E25.

AFTER THE R5 E18 PROJECTIVE KERNEL RULES, EACH PROJECTIVE CLASS OF KERNEL ROWS
CARRIES AT MOST ONE FREE BOOLEAN BIT.  IF q FREE PROJECTIVE CLASSES REMAIN,
EXACT-ONE IS SOLVABLE IN O(2^q poly(n)).

THEREFORE q=O(log n) IS A NEW POLYNOMIAL TERMINAL.

THE R5 E25 TOROIDAL FAMILY HAS TRADES OF SUPPORT 2n/3 BUT ONLY THREE FREE
KERNEL-ROW TYPES, SO ITS GLOBAL TRADE HAS CONSTANT DESCRIPTION COMPLEXITY.

THIS DOES NOT PROVE q=O(log n) FOR EVERY HARD CORE.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be a square+cubic Exact-One source and let

```text
K = ker_Q(A).
```

Choose a full-column-rank basis matrix

```text
B in Q^{n x d},
col(B)=K,
```

and write `b_i` for row `i` of `B`.

Every centered Boolean witness has the form

```text
y = B t,
y_i in {-1,2}.
```

As in R5 E18, proportionality of kernel rows is basis-invariant.

## 2. Projective classes

Put coordinates `i,j` in the same projective class when

```text
b_j = lambda b_i
```

for some nonzero rational `lambda`.

For every kernel vector, hence for every centered Boolean witness,

```text
y_j = lambda y_i.
```

Since both values belong to `{-1,2}`, the only ratios that can occur in a
Boolean witness are

```text
1, -2, -1/2.
```

Thus the R5 E18 rules apply classwise.

## 3. One class carries at most one free Boolean bit

Fix a projective class and a representative row `b_r`.
For every member `i`, write

```text
b_i = lambda_i b_r.
```

If the representative centered value is `a in {-1,2}`, then every coordinate in
the class is forced to

```text
y_i = lambda_i a.
```

Hence the set of allowed representative values is a subset of

```text
{-1,2}.
```

There are only three possibilities:

```text
0 allowed values -> immediate UNSAT;
1 allowed value  -> the entire class is forced;
2 allowed values -> one free Boolean bit controls the whole class.
```

In the two-valued case all class ratios must in fact be `1`, because both
representative choices must remain inside `{-1,2}`.  Thus a genuinely free class
is an equality class.

Therefore every projective class contributes at most one unresolved bit.

## 4. Exact FPT algorithm

Let

```text
q = number of free projective classes
```

after zero-row, bad-ratio and forced-class propagation.

Enumerate the two centered choices

```text
-1 or 2
```

for every free class.  Forced classes are fixed.  Every coordinate value is then
reconstructed from its class ratio.

For each of the at most

```text
2^q
```

reconstructed centered vectors `y`, verify

```text
A y = 0
```

and equivalently

```text
x=(y+1)/3 in {0,1}^n,
A x = 1.
```

This is exact and uses only rational arithmetic plus final integer checks.
Therefore

```text
boxed:
T(A)=O(2^q poly(n)).
```

In particular,

```text
boxed:
q=O(log n) => Exact-One is polynomial-time decidable.
```

This parameter is different from raw rational nullity `d`: one may have a large
support trade, or repeated global coordinates, while the number of distinct
projective row functionals remains small.

## 5. Relation to R5 E25

R5 E25 proved that on the toroidal family with `3|k`, every nonzero integer kernel
trade has support at least

```text
2n/3.
```

So support size is a bad description-complexity parameter.

But the exact toroidal kernel is

```text
y_{i,j}=u_{i-j mod 3},
u_0+u_1+u_2=0.
```

Hence the rows of a kernel basis take only three distinct values, one for each
residue class `i-j mod 3`.

The companion checker verifies for `k=3,6,9`:

```text
nullity_Q(A_k)=2,
projective/free kernel-row classes=3,
```

and exact enumeration therefore needs only

```text
2^3=8
```

class states, independent of `n`.

Thus the E25 phenomenon is now expressed cleanly:

```text
trade support = Theta(n),
trade projective description complexity = O(1).
```

A huge move can still be algorithmically simple.

## 6. Router update

After computing the rational kernel, the algebraic router should use:

```text
K0  zero kernel-row test
K1  projective bad-ratio test
K2  propagate forced projective classes
K3  quotient equality classes
K4  compute free projective diversity q
K5  if q=O(log n), enumerate 2^q class states exactly
K6  otherwise continue to KLOC/circuit, separator, integer-saturation,
    lattice-energy and structural branches
```

The class enumeration is exact SAT/UNSAT, not a relaxation.

## 7. What this does not prove

The NP-complete carrier from R5 E12 can have

```text
q = Theta(n).
```

No theorem here bounds projective diversity universally, and doing so without an
additional branch would contradict the existing hardness bridge unless `P=NP`.

The correct next firewall is therefore a family that simultaneously has

```text
large free projective diversity,
large effective kernel,
no useful KLOC-3/4 propagation,
integer feasibility,
no bounded-interface quotient,
and no recognized compact global normal form.
```

Equivalently, after E25/E26 the useful notion of a genuinely hard trade core is
not large support but **high projective description complexity**.

The next theorem target is:

```text
PROJECTIVE-DIVERSITY / TRADE-COMPRESSION DICHOTOMY

For every projectively reduced integer-feasible square+cubic+linear source,
either
  (A) q=O(log n),
  (B) a polynomial source-aligned / KLOC / cokernel obstruction exists,
  (C) the instance decomposes through bounded interfaces,
  (D) a compact algebraic normal form describes the global trade space,
  or
  (E) expose an explicit high-q survivor family.
```

Branch (E) is the next firewall target.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e26_kernel_projective_diversity.py
```
