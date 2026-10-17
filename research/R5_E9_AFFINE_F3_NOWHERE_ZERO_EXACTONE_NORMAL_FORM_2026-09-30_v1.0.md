# R5 E9 — Affine F3 Nowhere-Zero Exact-One Normal Form

Date: 2026-09-30

Status:
`JANUS_EXACT_FINITE_FIELD_NORMAL_FORM__AFFINE_NOWHERE_ZERO_AND_AUGMENTED_FULL_SUPPORT_CODE__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS NOTE REMOVES UNBOUNDED INTEGER MAGNITUDES FROM THE DECISION FORMULATION.
IT DOES NOT SUPPLY A POLYNOMIAL ALGORITHM FOR THE REMAINING FULL-SUPPORT SEARCH.
GENERAL TERNARY FULL-SUPPORT / HYPERPLANE-AVOIDANCE IS NOT A FREE POLYNOMIAL DONOR.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Source setting

Let

```text
A in {0,1}^{m x n}
```

have exactly three ones in every row.  No column-regularity, squareness, or linear-hypergraph assumption is needed for the equivalence below.

Because every row has weight three,

\[
A\mathbf 1 = 3\mathbf 1 \equiv 0 \pmod 3.
\]

Work over `F3={0,1,2}`, with `2=-1`.

## 2. Main equivalence

### Theorem AF3-1 — Exact-One = affine nowhere-zero F3 solution

The following are equivalent:

1. there exists `x in {0,1}^n` with

```text
A x = 1
```

over the integers;

2. there exists

```text
r in (F3^*)^n = {1,2}^n
```

such that

```text
A r = 1   over F3.
```

### Proof: Exact-One => nowhere-zero affine solution

Let `x` be an Exact-One witness and define

\[
r=\mathbf1+x\pmod3.
\]

Then every coordinate of `r` is `1` or `2`, hence nonzero.  Also

\[
Ar=A\mathbf1+Ax\equiv0+\mathbf1=\mathbf1\pmod3.
\]

### Proof: nowhere-zero affine solution => Exact-One

Let `r in {1,2}^n` satisfy `Ar=1` over `F3`.  In one source row let `k` be the number of entries equal to `2`.  The row sum is

\[
(3-k)\cdot1+k\cdot2=3+k\equiv k\pmod3.
\]

The affine equation requires this to equal `1`, so

\[
k\equiv1\pmod3.
\]

Since `k in {0,1,2,3}`, necessarily `k=1`.

Therefore the Boolean vector

\[
x_i=\mathbf1[r_i=2]
\]

contains exactly one selected coordinate in every source row, so `Ax=1` over the integers. QED.

Thus

\[
\boxed{
\text{Exact-One}(A)\text{ SAT}
\iff
\exists r\in\mathbb F_3^n:\ Ar=\mathbf1,\ r_i\ne0\ \forall i.
}
\]

## 3. Missing-residue terminal

Because `A1=0` over `F3`, every affine solution has its two global translates

```text
r,
r+1,
r+2
```

in the same solution set.

Hence if **any** affine solution omits one of the three field symbols, a global translation moves the omitted symbol to `0` and produces a nowhere-zero affine solution.  AF3-1 then reconstructs an Exact-One witness.

Equivalently:

```text
IF Ar=1 over F3 has a solution using at most two residue values,
THEN A is Exact-One SAT and a witness is recovered in linear time.
```

For a source that is Exact-One UNSAT, every affine solution (if any exists) must therefore use all three residues `0,1,2`.

This is a polynomial terminal after one Gaussian-elimination solution is supplied, but it is not complete because another vector in the same affine space may omit a residue even when the first one does not.

## 4. Augmented full-support kernel code

Form the augmented ternary matrix

\[
\widetilde A=[A\mid-\mathbf1]
\]

and the linear code

\[
C_A=\ker_{\mathbb F_3}(\widetilde A)\subseteq\mathbb F_3^{n+1}.
\]

### Theorem AF3-2 — augmented full-support equivalence

\[
\boxed{
A\text{ Exact-One SAT}
\iff
C_A\text{ contains a full-support codeword.}
}
\]

### Proof

If `r` is the AF3-1 nowhere-zero affine solution, then

```text
(r,1) in ker_F3([A|-1])
```

and every coordinate is nonzero.

Conversely, let `(u,t)` be a full-support kernel codeword.  Then `t` is nonzero, so scale the whole codeword by `t^{-1}`.  This preserves full support and gives `(r,1)` with `Ar=1`.  AF3-1 reconstructs the Boolean witness. QED.

The two nonzero scalars of `F3` pair every normalized full-support word `(r,1)` with its scalar multiple.  Therefore there is an exact counting identity:

\[
\boxed{
\#\operatorname{ExactOne}(A)
=\frac12\,#\{c\in C_A:\operatorname{supp}(c)=[n+1]\}.
}
\]

If `M(C_A)` denotes the matroid induced by a generator matrix of the code, the Crapo--Rota Critical Theorem gives

\[
#\{\text{full-support codewords in }C_A\}
=\chi_{M(C_A)}(3).
\]

Hence

\[
\boxed{
\#\operatorname{ExactOne}(A)=\frac12\chi_{M(C_A)}(3),
\qquad
A\text{ SAT}\iff\chi_{M(C_A)}(3)>0.
}
\]

This identity is exact; it is not an efficient characteristic-polynomial evaluation claim.

## 5. Affine hyperplane-avoidance form

Run Gaussian elimination over `F3`.

If

```text
A r = 1
```

is inconsistent, return Exact-One `UNSAT` immediately.

Otherwise write all affine solutions as

\[
r=r^{(0)}+B\alpha,
\qquad
\alpha\in\mathbb F_3^d,
\]

where the columns of `B` form `ker_F3(A)`.  Write `b_i` for row `i` of `B`.

AF3-1 becomes

\[
\boxed{
\exists\alpha\in\mathbb F_3^d
\quad\forall i:\quad
r_i^{(0)}+b_i\alpha\ne0.
}
\]

Equivalently the `n` affine hyperplanes

\[
H_i=\{\alpha:b_i\alpha=-r_i^{(0)}\}
\]

fail to cover the parameter space `F3^d`.

So the universal source problem is exactly a highly structured affine-hyperplane-avoidance problem over the fixed field `F3`.

This finite-field representation eliminates:

```text
unbounded integer coordinates,
exponentially large primitive integer coefficients,
integer sign-crossing magnitudes,
Graver step lengths
```

from the **decision representation**.  Those objects remain valid in the lattice formulation, but they are not logically necessary for deciding Exact-One.

## 6. Relation to the integer sign-crossing gate

The current integer-lattice stack proves

```text
Exact-One SAT
iff
min { ||y||_1 : Ay=-1, y odd } = n.
```

AF3-1 gives an exact bounded-alphabet formulation of the same decision problem.

Therefore future universal work has two equivalent attack surfaces:

```text
INTEGER:
  construct a globally improving sign-crossing source trade,

FINITE FIELD:
  construct a point of Ar=1 avoiding all coordinate-zero hyperplanes.
```

A theorem that solves either surface with deterministic polynomial total cost closes the source carrier.  No equivalence between the *augmentation dynamics* of the two representations is claimed.

## 7. Frozen finite controls

The checker uses the existing linear-cubic controls.

### PG15 SAT

For the frozen `PG15_SAT_R11` source:

```text
rank_F3(A)=11,
dim affine solution space=4,
```

so there are `3^4=81` affine solutions of `Ar=1`.

Exactly four are nowhere-zero.  They map bijectively to the four known Exact-One witnesses.

For the augmented code `C_A`, the kernel dimension is five and exactly eight codewords have full support, verifying

```text
8 = 2 * 4.
```

### Frozen singular rank-14 UNSAT control

For the connected `n=15` singular UNSAT source:

```text
rank_F3(A)=14,
dim affine solution space=1,
```

so there are three affine solutions of `Ar=1`.

None is nowhere-zero and the source has no Exact-One witness.  The augmented code has no full-support codeword.

These are exact exhaustive finite controls only; AF3-1/AF3-2 are proved symbolically above.

## 8. Prior-art / anti-loop firewall

Full-support codewords and the Critical Theorem are classical coding/matroid objects.  The repository already records generic hardness of ternary full-support codeword search in broader code classes.  Therefore the reformulation itself must not be promoted as a polynomial algorithm.

Likewise, generic affine hyperplane avoidance over `F3` is not a free donor: the missing point-selection problem can encode hard finite-domain CSPs.

The JANUS-specific value of AF3-1/AF3-2 is that they bind the **literal cubic Exact-One source** directly to:

```text
one affine F3 system
+ one coordinate-wise nowhere-zero condition
```

with an exact linear-time witness decoder and no integer-magnitude layer.

## 9. New source-level gate

Freeze

```text
R5_E9_SOURCE_AUGMENTED_TERNARY_FULL_SUPPORT_DECOMPOSITION_GATE_V1
```

Required universal PASS:

```text
INPUT:
  linear-cubic source A.

POLYNOMIAL PREPROCESS:
  solve Ar=1 over F3 or reject as UNSAT;
  construct the affine parameter representation / augmented kernel code.

OUTPUT:
  either
    a full-support affine solution r and Exact-One witness,
  or
    a polynomially constructible certificate that the affine coordinate
    hyperplanes cover the whole solution space.
```

The algorithm may use source-specific matroid/graph decomposition, but must not:

```text
enumerate 3^d affine points,
enumerate all hyperplane subfamilies,
evaluate a general Tutte/characteristic polynomial exponentially,
assume a generic full-support-code oracle,
or hide SAT inside certificate discovery.
```

Immediate stress controls remain:

```text
PG15 SAT,
prime / unique-model SAT towers,
prime UNSAT towers,
post-RKPR high-nullity families,
nonregular F7/F7* augmented carriers.
```

## 10. Ceiling

```text
EXACT-ONE
iff AFFINE NOWHERE-ZERO F3 SOLUTION
= PROVED

EXACT-ONE
iff FULL-SUPPORT WORD IN ker_F3([A|-1])
= PROVED

#EXACT-ONE
= chi_{M(C_A)}(3) / 2
= PROVED VIA CRITICAL THEOREM

MISSING-RESIDUE AFFINE SOLUTION
=> SAT + LINEAR-TIME WITNESS
= PROVED

INTEGER MAGNITUDES NEEDED FOR DECISION
= NO

POLYNOMIAL FULL-SUPPORT CONSTRUCTOR / COVER CERTIFICATE
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1
= EMPTY
P_VS_NP
= OPEN
```
