# R5 E9 — AF3 model-count mod-3 linear-cubic barrier

Date: 2026-09-30

Status: `JANUS_EXACT_FINITE_COUNTERCONTROL__MOD3_COUNT_NONVANISHING_NOT_COMPLETE__NO_D1_PROMOTION`

## 1. Targeted shortcut

The affine-F3 normal form proves that Exact-One witnesses are in bijection with nowhere-zero solutions of

\[
Ar=\mathbf 1,\qquad r\in\mathbb F_3^n.
\]

For an affine parameterization `r=r0+B alpha`, the indicator that one coordinate is nonzero is its square over `F3`. Hence

\[
W(A):=\#\operatorname{ExactOne}(A)
=\sum_{\alpha\in\mathbb F_3^d}\prod_i(r_i^{(0)}+b_i\alpha)^2.
\]

Modulo three this sum can be extracted from the reduced polynomial as a top-coefficient functional. A tempting shortcut is therefore

```text
SAT iff W(A) != 0 mod 3.
```

This note falsifies that shortcut inside the literal connected square linear-cubic source class.

## 2. Connected linear-cubic 9_3 control

Use the following nine source rows, in zero-based indexing:

```text
(1,3,5)
(2,3,8)
(0,1,6)
(0,5,8)
(3,4,6)
(6,7,8)
(4,5,7)
(1,2,7)
(0,2,4)
```

Every row has size three. Every variable occurs in exactly three rows. Any two rows intersect in at most one variable, and the Levi graph is connected. Thus the source is square, cubic and linear.

## 3. Exactly three Exact-One witnesses

Exact enumeration gives precisely

```text
{0,3,7}
{1,4,8}
{2,5,6}
```

and no others. Therefore

\[
\boxed{W(A)=3\equiv0\pmod3}
\]

although the source is SAT.

So model-count nonvanishing modulo three is not a complete SAT criterion even on connected linear-cubic `9_3` sources.

## 4. Exact AF3 replay

Gaussian elimination gives

\[
\operatorname{rank}_{\mathbb F_3}(A)=6,
\qquad d=9-6=3.
\]

Hence `Ar=1` has exactly `3^3=27` affine solutions. Exactly three are nowhere-zero:

```text
(1,1,2,1,1,2,2,1,1)
(1,2,1,1,2,1,1,1,2)
(2,1,1,2,1,1,1,2,1)
```

They decode by `x_i=1[r_i=2]` to the three Boolean witnesses above.

For the augmented code

\[
C_A=\ker_{\mathbb F_3}[A\mid-\mathbf1],
\]

each normalized nowhere-zero affine word has two nonzero scalar multiples. Therefore the augmented code has exactly six full-support codewords. By the Critical Theorem,

\[
\chi_{M(C_A)}(3)=6\equiv0\pmod3.
\]

Thus even positivity of the full-support count cannot be inferred from its residue modulo three.

## 5. Consequence

The following routes are invalid as universal decision rules:

```text
W(A) mod 3 != 0;
chi_M(3) mod 3 != 0;
one reduced-polynomial top coefficient over F3 is nonzero.
```

They remain one-sided SAT certificates when nonzero, but zero residue cannot certify UNSAT.

This does not rule out richer exact counting, additional moduli, or source-specific algebraic decompositions. It only closes the single-mod-3 nonvanishing shortcut.

## 6. Ceiling

```text
CONNECTED SQUARE LINEAR-CUBIC 9_3 CONTROL = PASS
EXACT-ONE WITNESSES = 3
rank_F3(A) = 6
AFFINE F3 SOLUTIONS = 27
NOWHERE-ZERO AFFINE SOLUTIONS = 3
AUGMENTED FULL-SUPPORT CODEWORDS = 6
SAT => W(A) != 0 mod 3 = FALSE
UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
E8_D1 = EMPTY
P_VS_NP = OPEN
```
