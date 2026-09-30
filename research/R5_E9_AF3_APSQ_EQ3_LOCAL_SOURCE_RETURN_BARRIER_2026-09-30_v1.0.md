# R5 E9 — AF3 / APSQ on the EQ3 Regularizer: Local Source-Return Barrier

Date: 2026-09-30

Status:
`JANUS_EXACT_ANTI_LOOP_THEOREM__GADGET_LOCAL_AF3_APSQ_RETURNS_EQ3_SOURCE_SEMANTICS__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_SATURATION_QUOTIENT_2026-09-30_v1.0.md`
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`
- `research/R5_E9_EQ3_LOCAL_GAUGE_QUOTIENT_RETURNS_SOURCE_HARDNESS_2026-09-28_v1.0.md`

Scientific ceiling:

```text
THIS THEOREM RULES OUT ONLY A GADGET-BY-GADGET AF3/APSQ UNIVERSALIZATION.
IT DOES NOT RULE OUT GLOBAL APSQ INTERACTIONS ACROSS MANY GADGETS AND SOURCE ROWS.
IT DOES NOT PROVE P!=NP.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen EQ3 gadget

Use terminals `t0,t1,t2` and auxiliaries `a3,...,a9`, numbered `0,...,9`, with the nine Exact-One rows

```text
(2,5,6)
(1,4,7)
(5,7,9)
(0,3,7)
(4,6,9)
(2,4,8)
(3,8,9)
(0,5,8)
(1,3,6)
```

The parent theorem proves that the Boolean terminal projection is exactly

```text
EQ3 = {000,111}.
```

## 2. Exact affine-F3 solution family

Apply AF3 to the gadget incidence matrix `G`.  Exact elimination over `F3` gives rank eight and therefore affine dimension two for

\[
G r=\mathbf1.
\]

Choose parameters `p,q in F3`.  Every affine solution is exactly

\[
\boxed{
\begin{aligned}
r_0=r_1=r_2=r_9&=q,\\
r_3=r_4=r_5&=1-p-q,\\
r_6=r_7=r_8&=p.
\end{aligned}}
\]

Thus the ten coordinate nonzero constraints reduce, after duplicate removal, to only

\[
\boxed{
q\ne0,
\qquad p\ne0,
\qquad 1-p-q\ne0.
}
\]

These are three distinct affine hyperplanes with three distinct projective normals in the two-dimensional parameter space.

### Consequence for APSQ

Every parallel class has exactly one forbidden offset.  Therefore APSQ performs only duplicate removal:

```text
affine dimension before = 2
affine dimension after  = 2
projective classes       = 3
two-offset pins          = 0
three-offset UNSAT       = 0
```

So the local gadget does not collapse by parallel saturation.

## 3. Exact full-support solutions

The three pairs `(p,q)` satisfying all nonzero constraints are

```text
(p,q) = (1,1), (2,1), (1,2).
```

They give the three nowhere-zero affine words

```text
(1,1,1,1,1,1,2,2,2,1),
(1,1,1,2,2,2,1,1,1,1),
(2,2,2,1,1,1,1,1,1,2).
```

Therefore the terminal projection in the AF3 representation is exactly

\[
\boxed{
(r_0,r_1,r_2)\in\{(1,1,1),(2,2,2)\}.
}
\]

Under the AF3 Boolean decoder `x_i=1[r_i=2]`, this becomes exactly

```text
{000,111} = EQ3.
```

The two `q=1` words are the two internal extensions of Boolean terminal value `000`; the single `q=2` word is the unique extension of terminal value `111`, matching the parent regularizer theorem.

## 4. Gadget-local elimination returns the source variable

Now take the regularized instance `R(Phi)` of an arbitrary cubic Positive 1-in-3 source `Phi`.
Each source variable `x` has three occurrence terminals attached to one disjoint EQ3 gadget.

Apply AF3 and eliminate only the gadget-internal variables while preserving the terminal coordinates.
By Section 3, the exact projected relation is

\[
(r_{x,0},r_{x,1},r_{x,2})=(q_x,q_x,q_x),
\qquad q_x\in\mathbb F_3^*.
\]

So each gadget reduces to one shared nonzero ternary variable `q_x`.

For an old source row `(x,y,z)`, the retained AF3 row equation is

\[
q_x+q_y+q_z=1\pmod3,
\qquad q_x,q_y,q_z\in\{1,2\}.
\]

The only multiset of three nonzero F3 values summing to one is two `1`s and one `2`.  Hence, decoding `X=1[q_x=2]`, the old source row is exactly Positive 1-in-3 again.

Therefore local AF3 elimination of every regularizer gadget yields precisely the original source semantics:

\[
\boxed{
R(\Phi)_{\mathrm{AF3/local}}
\longrightarrow
\Phi
}
\]

with linear-time witness conversion.

## 5. What this theorem forbids

The following route is not universal progress:

```text
regularize arbitrary source into linear-cubic form
-> run AF3
-> apply APSQ independently inside each EQ3 gadget
-> eliminate gadget internal parameters
-> declare the residual simpler.
```

After exact local elimination the residual is just arbitrary cubic Positive 1-in-3 SAT again.

This is the F3 analogue of the earlier local-gauge source-return theorem.

## 6. What remains legitimately open

This theorem does **not** say that the full global APSQ preprocessing on `R(Phi)` is powerless.
When all gadget and old-source rows are assembled before saturation, projective coordinate classes can in principle involve information from multiple gadgets and source rows.  Such a global interaction is not captured by gadget-local elimination.

Therefore the live question is stricter:

```text
Can GLOBAL AF3/APSQ, or a stronger polynomial closure built on its saturated
parallel-simple geometry, always derive a witness/UNSAT certificate or a
strict semantic contraction that cannot be reproduced gadget-by-gadget?
```

Any claimed progress must be measured after quotienting out this exact local source-return behavior.

## 7. Ceiling

```text
EQ3 GADGET AF3 DIMENSION
= 2

LOCAL APSQ
= DUPLICATE REMOVAL ONLY / NO PIN

NOWHERE-ZERO TERMINAL PROJECTION
= {(1,1,1),(2,2,2)}

BOOLEAN TERMINAL PROJECTION
= EQ3

GADGET-LOCAL AF3/APSQ REGULARIZER ELIMINATION
= RETURNS ORIGINAL SOURCE SEMANTICS

GLOBAL CROSS-GADGET APSQ EFFECT
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
