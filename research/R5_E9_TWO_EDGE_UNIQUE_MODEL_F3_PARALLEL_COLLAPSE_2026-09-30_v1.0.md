# R5 E9 — Two-Edge Unique-Model Tower: Exact F3 Parallel Collapse

Date: 2026-09-30

Status:
`JANUS_ARBITRARY_SIZE_POSITIVE_ROUTER_THEOREM__HOSTILE_SAT_TOWER_COLLAPSES_UNDER_F3_PARALLEL_SATURATION__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_TWO_EDGE_PRIME_UNIQUE_MODEL_LINEAR_NULLITY_TOWER_2026-09-29_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_SATURATION_QUOTIENT_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THE INFINITE UNIQUE-MODEL / SIGNED-TRADE-FREE / 3-CUT-PRIME SAT TOWER
IS SOLVED DETERMINISTICALLY BY THE NEW AFFINE-F3 PARALLEL QUOTIENT.
THIS REMOVES THAT TOWER AS A HOSTILE RESIDUAL FOR THE FINITE-FIELD ROUTE.
IT DOES NOT PROVE THAT EVERY LINEAR-CUBIC SOURCE COLLAPSES THIS WAY.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Tower notation

Let `A_0` be the frozen 18_3 unique-model source and let

```text
F_t={(i1,j1),(i2,j2)}
```

be the distinguished nonincident pair used by the parent two-edge tower.
Write `E_t` for its two-entry incidence matrix and

\[
A_{t+1}=\begin{pmatrix}
A_t-E_t&E_t\\
E_t&A_t-E_t
\end{pmatrix}.
\]

The next distinguished pair is the two upper-right crossed copies of the old pair.

The parent proves a unique Boolean witness `x_t`; write

\[
r_t^*=\mathbf1+x_t\in\{1,2\}^{n_t}\subset\mathbb F_3^{n_t}.
\]

By AF3-1, `r_t^*` is a nowhere-zero solution of

\[
A_t r=\mathbf1\quad(\mathbb F_3).
\]

The witness lifts fiber-constantly, so

\[
r_{t+1}^*=(r_t^*,r_t^*).
\]

## 2. Exact F3 kernel decomposition of one lift

Work over `F3`; here `2=-1` and the symmetric/antisymmetric change of variables is invertible.
For `(u,v)` representing symmetric and antisymmetric components, the lift splits as

\[
A_t\oplus(A_t-2E_t)
=A_t\oplus(A_t+E_t).
\]

Let

\[
K_t=\ker_{\mathbb F_3}(A_t).
\]

The parent supplies an integer left-kernel vector `ell_t` whose distinguished row values are

```text
ell_t[i1]=1,
ell_t[i2]=2.
```

Also column cubicity gives

\[
\mathbf1^T A_t=3\mathbf1^T=0\quad(\mathbb F_3).
\]

### Lemma F3L-1

\[
\boxed{
\ker(A_t+E_t)
=
W_t^0:=\{v\in K_t:v_{j_1}=v_{j_2}=0\}.
}
\]

### Proof

Take `(A_t+E_t)v=0`.  Left multiply by `1^T`:

\[
v_{j_1}+v_{j_2}=0.
\]

Left multiply by `ell_t^T`:

\[
v_{j_1}+2v_{j_2}=0.
\]

Subtracting gives `v_{j_2}=0`, hence `v_{j_1}=0`.  Therefore `E_tv=0` and then `A_tv=0`.
The reverse inclusion is immediate. QED.

Consequently

\[
\boxed{K_{t+1}\cong K_t\oplus W_t^0.}
\]

## 3. Distinguished evaluations have rank exactly one

At the seed, on the displayed rational/integer kernel basis,

```text
(ev_15(k1),ev_15(k2))=(0,1),
(ev_1 (k1),ev_1 (k2))=(0,-2).
```

Modulo three `-2=1`, so the two distinguished coordinate functionals are **equal** on all of `K_0` and are nonzero.

Assume they are equal on `K_t`.  In the lifted kernel decomposition, the next distinguished coordinates are the crossed bottom copies.  Their evaluations are

\[
f_{j_a}(u)-f_{j_a}(v|_{W_t^0}),\qquad a=1,2.
\]

Equality of the old functionals implies equality of their restrictions to `W_t^0`, hence equality of the two new distinguished evaluations on all of `K_{t+1}`.  Nonzeroness persists on the symmetric copy.

Therefore their joint evaluation rank is exactly one at every level, and

\[
\dim W_t^0=d_t-1,
\qquad d_t:=\dim K_t.
\]

Using F3L-1,

\[
\boxed{d_{t+1}=2d_t-1.}
\]

The seed has `d_0=2`, so

\[
\boxed{d_t=2^t+1.}
\]

This is an exact ternary-nullity theorem for the whole tower.

## 4. Projective polarity-completeness

For a nowhere-zero affine base point `r^*` and kernel `K`, let `f_j in K^*` be coordinate evaluation at variable `j`.

For one projective coordinate class `[f]`, normalize every nonzero `f_j=lambda_j f` to the same representative `f`.  The corresponding normalized affine constant is

\[
\lambda_j^{-1}r_j^*\in\{1,2\}.
\]

Call the pair `(K,r^*)` **polarity-complete** if every projective coordinate class contains both normalized constants `1` and `2`.

For such a class, the zero hyperplanes forbid both nonzero values of `f(alpha)`.  Since `alpha=0` gives the nowhere-zero point `r^*`, the only admissible value is

\[
\boxed{f(\alpha)=0.}
\]

Thus APSQ turns every projective class into a homogeneous pin.

### Seed verification

Reduce the explicit seed kernel basis `(k1,k2)` modulo three.  Its 18 coordinate functionals fall into exactly three projective classes:

```text
(1,0),
(0,1),
(1,1).
```

Using `r_0^*=1+x_0`, each of the three classes contains coordinates with both normalized constants `1` and `2`.  Hence `(K_0,r_0^*)` is polarity-complete.

## 5. Polarity-completeness is preserved by the lift

Assume `(K_t,r_t^*)` is polarity-complete.

Under

\[
K_{t+1}=K_t\oplus W_t^0,
\]

the top and bottom copies of coordinate `j` have functionals

\[
F_j^+=(f_j,f_j|_{W_t^0}),
\qquad
F_j^-=(f_j,-f_j|_{W_t^0}).
\]

If `f_k=lambda f_j` on `K_t`, then automatically

\[
f_k|_{W_t^0}=\lambda f_j|_{W_t^0},
\]

and hence

\[
F_k^+=\lambda F_j^+,
\qquad
F_k^-=\lambda F_j^-.
\]

The lifted affine constants are the same base constants because

\[
r_{t+1}^*=(r_t^*,r_t^*).
\]

Therefore every `+` and every `-` projective class inherits both normalized constants `1` and `2` from its parent class.  If two such classes merge projectively, the union still contains both values.

Hence `(K_{t+1},r_{t+1}^*)` is polarity-complete.

By induction the property holds for every `t`.

## 6. Complete saturation theorem

Coordinate evaluations span `K_t^*`: a nonzero kernel vector has some nonzero coordinate.  Since every projective coordinate class is polarity-complete, APSQ emits the homogeneous pin

\[
f(\alpha)=0
\]

for every projective class.  These pins therefore span the whole dual space and force

\[
\boxed{\alpha=0.}
\]

The unique remaining affine point is exactly `r_t^*`, which is nowhere-zero.  AF3-1 reconstructs the unique Exact-One witness `x_t=r_t^*-1`.

### Theorem F3L-2

For every level `t>=0` of the frozen two-edge prime unique-model SAT tower, the affine-F3 parallel-saturation quotient decides SAT and constructs the unique witness in deterministic polynomial time **without branching and without enumerating `3^{d_t}` affine points**.

The tower has

\[
n_t=18\cdot2^t,
\qquad
d_t=2^t+1=n_t/18+1,
\]

so this is an arbitrary-size high-nullity positive control for the new router.

## 7. Finite regression pattern

The exact checker replays the first five levels:

```text
t   n     d_F3   projective classes before saturation   final d
0   18      2                 3                           0
1   36      3                 5                           0
2   72      5                 9                           0
3  144      9                17                           0
4  288     17                33                           0
```

The observed class count is `2d_t-1`; the arbitrary-size theorem requires only polarity-completeness plus spanning, not this numerical class-count identity.

## 8. Consequence for the universal search

The previous hostile tower showed that the integer sign-crossing route cannot rely on:

```text
low rational nullity,
multiple models,
small signed trades,
small <=3 edge cuts,
balance.
```

F3L-2 now shows that all of those hostile properties can coexist while the **finite-field projective-offset structure remains completely deterministic**.

Therefore this tower is no longer an unresolved adversary for the AF3/APSQ route.
The correct next adversary must survive parallel saturation with positive residual dimension.

Immediate required controls:

```text
PG15 SAT              -> survives at d=4;
prime UNSAT towers     -> test saturation behavior;
post-RKPR Paley cores  -> reconcile with graphic/gradient terminals;
linear high-girth cores -> test positive residual dimension.
```

## 9. Ceiling

```text
TOWER F3 NULLITY
= d_t=2^t+1 EXACT

F3 KERNEL LIFT
= K_{t+1}=K_t direct-sum W_t^0 EXACT

PROJECTIVE POLARITY-COMPLETENESS
= PRESERVED FOR ALL t

APSQ ON UNIQUE-MODEL SAT TOWER
= COMPLETE / BRANCH-FREE / POLYNOMIAL

ARBITRARY LINEAR-CUBIC SOURCE
= NOT COVERED

PARALLEL-SIMPLE POSITIVE-DIMENSION RESIDUAL
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
