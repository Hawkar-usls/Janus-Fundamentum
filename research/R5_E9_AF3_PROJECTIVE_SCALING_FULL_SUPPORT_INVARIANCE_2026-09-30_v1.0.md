# R5 E9 — AF3 projective-scaling full-support invariance

Date: 2026-09-30

Status: `JANUS_EXACT_REPRESENTATION_CHANGE_THEOREM__PROJECTIVE_COLUMN_SCALING_SAFE_FOR_AF3_FULL_SUPPORT__NO_D1_PROMOTION`

Parent:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`

## 1. Setting

For a row-weight-three Exact-One source `A`, form

\[
M=[A\mid-\mathbf1]
\]

over `F3`. The parent theorem proves

\[
A\text{ SAT}\iff \ker_{\mathbb F_3}(M)\text{ contains a full-support vector}.
\]

Unlike the original Boolean coordinates, full-support semantics are invariant under nonzero coordinate rescaling.

## 2. Projective invariance theorem

Let

\[
U\in GL_m(\mathbb F_3)
\]

and let

\[
D=\operatorname{diag}(d_1,\ldots,d_{n+1}),\qquad d_i\in\mathbb F_3^*=\{1,2\}.
\]

Put

\[
N=UMD.
\]

### Theorem AF3-PS-1

The map

\[
z\longmapsto c=Dz
\]

is a support-preserving linear bijection

\[
\ker N\xrightarrow{\cong}\ker M.
\]

Therefore

\[
\boxed{
\ker N\text{ contains a full-support word}
\iff
\ker M\text{ contains a full-support word}
\iff
A\text{ is Exact-One SAT}.
}
\]

### Proof

`Nz=0` iff `UMDz=0`. Since `U` is invertible, this is equivalent to `M(Dz)=0`. Thus `z -> Dz` is a bijection between the two kernels, with inverse `c -> D^{-1}c`.

Every diagonal entry of `D` is nonzero, so coordinate `i` is zero in `z` iff it is zero in `Dz`. Hence support is preserved exactly. QED.

## 3. Exact witness reconstruction after projective representation change

Suppose a solver on `N` returns a full-support `z`.

1. Undo the column scaling:
   \[
   c=Dz\in\ker M.
   \]
2. The syndrome coordinate `t=c_{n+1}` is nonzero. Scale the entire codeword by `t^{-1}`:
   \[
   (r,1)=t^{-1}c.
   \]
3. Then
   \[
   Ar=\mathbf1,
   \qquad r_i\in\{1,2\}.
   \]
4. Decode
   \[
   x_i=\mathbf1[r_i=2].
   \]
5. The AF3 theorem gives `Ax=1` over the integers; direct multiplication verifies the witness.

Every step is linear/exact and polynomial time.

## 4. Matroid consequence

Row operations and nonzero column scalings are precisely the standard projective changes of a matrix representation. Hence the AF3 full-support existence question depends only on the represented ternary matroid together with the identification of the ground elements, not on one fixed numeric representation.

This is a genuine enlargement of the legal representation toolbox. In the earlier rational/Boolean Exact-One routes, arbitrary coordinate rescaling was not semantics-preserving because the literal values `{-1,2}` or `{0,1}` mattered coordinatewise. In AF3 the target property is only `coordinate != 0`, so projective scaling is safe.

This permits exact use of projectively equivalent ternary representations, including candidate graphic/frame/gain representations, provided the solver preserves full-support semantics and witness reconstruction is carried out as above.

## 5. Scope firewall

Do not promote any of the following:

```text
projective equivalence preserves original Boolean coordinate values   FALSE
projective scaling is safe for the rational {-1,2} kernel route       FALSE
ternary matroid recognition alone solves full-support search           FALSE
every source augmented ternary matroid is frame/graphic                NOT PROVED
```

The exact promotion is only:

```text
FULL-SUPPORT EXISTENCE IN ker_F3([A|-1])
IS INVARIANT UNDER INVERTIBLE ROW OPERATIONS
AND NONZERO COLUMN SCALINGS.
```

## 6. New representation frontier

Because projective representation changes are now legal, polynomial routers may legitimately attempt:

```text
graphic / cographic representations,
frame / signed-graphic / gain-graph representations,
dyadic representations,
bounded-branch-width decompositions,
constant-interface matroid-sum composition,
```

but each admitted class still needs a polynomial full-support constructor or cover certificate. Recognition alone is not enough.

A particularly concrete sufficient subcase is a recovered signed cubic graph: published theory characterizes nowhere-zero 3-flow by antibalance plus perfect matching. The missing source theorem is polynomial recognition/coverage of that subcase from the augmented ternary matroid.

## 7. Ceiling

```text
AF3 PROJECTIVE COLUMN SCALING
= EXACTLY SAFE

KERNEL SUPPORT BIJECTION
= PROVED

BOOLEAN WITNESS RECONSTRUCTION
= PROVED POLYNOMIAL

PROJECTIVE TERNARY REPRESENTATION TOOLBOX
= LEGALLY OPEN

UNIVERSAL FRAME/SIGNED-GRAPH COVERAGE
= NOT PROVED

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
