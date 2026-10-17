# R5 E9 — AF3 / EQ3 Global APSQ Factorization and Source Return

Date: 2026-09-30

Status:
`JANUS_EXACT_GLOBAL_ANTI_LOOP_THEOREM__EQ3_REGULARIZER_APSQ_FACTORS_THROUGH_SOURCE_APSQ__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_SATURATION_QUOTIENT_2026-09-30_v1.0.md`
- `research/R5_E9_AF3_APSQ_EQ3_LOCAL_SOURCE_RETURN_BARRIER_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THIS STRENGTHENS THE GADGET-LOCAL SOURCE-RETURN RESULT TO THE FULL GLOBAL
AFFINE-F3 SOLUTION SPACE AND THE FULL ITERATED APSQ PREPROCESSOR.
IT DOES NOT PROVE THAT SOURCE APSQ IS UNIVERSALLY POWERLESS.
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SOLVER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Source and regularizer

Let `Phi` be any cubic Positive 1-in-3 source with source variables `x` and source incidence matrix `A`.  The frozen regularizer `R(Phi)` splits the three occurrences of every source variable and attaches one ten-variable EQ3 gadget.

For gadget `x`, use the frozen gadget coordinates `0,...,9` and write the three occurrence terminals as `x_0,x_1,x_2`.

Over `F3`, the nine gadget equations have the exact affine solution family

\[
\boxed{
\begin{aligned}
r_{x,0}=r_{x,1}=r_{x,2}=r_{x,9}&=q_x,\\
r_{x,3}=r_{x,4}=r_{x,5}&=1-p_x-q_x,\\
r_{x,6}=r_{x,7}=r_{x,8}&=p_x,
\end{aligned}}
\]

with free `p_x,q_x in F3`.

Every retained old source row becomes exactly

\[
q_x+q_y+q_z=1.
\]

Therefore the complete affine solution space of the regularized instance is the direct affine product

\[
\boxed{
\{r:R(\Phi)r=1\}
\cong
\{q:Aq=1\}
\times
F_3^{V(\Phi)},
}
\]

where the second factor consists of the independent private parameters `p_x`.

No additional affine relation couples different `p_x` variables.

## 2. Full-support constraints after exact duplicate removal

Inside one gadget the ten coordinate nonzero constraints collapse to exactly three distinct constraints:

\[
\boxed{
Q_x:q_x\ne0,
\qquad
P_x:p_x\ne0,
\qquad
T_x:1-p_x-q_x\ne0.
}
\]

The multiplicities are respectively `4,3,3`, but duplicate multiplicity has no effect on AF3 avoidance.

Choose any affine parameterization of the source solution space

\[
q=c+B\alpha,
\qquad \alpha\in F_3^d,
\]

and retain the private parameters `p=(p_x)` as independent affine coordinates.  The linear parts of the three classes are

\[
\begin{aligned}
\nabla Q_x&=(b_x,0),\\
\nabla P_x&=(0,e_x),\\
\nabla T_x&=(-b_x,-e_x),
\end{aligned}
\]

where `b_x` is row `x` of `B` and `e_x` is the private unit vector of gadget `x`.

## 3. Projective-parallel classification

Assume first that `b_x` and `b_y` are nonzero source normals.

### P classes

For `x != y`,

\[
(0,e_x)
\not\parallel
(0,e_y).
\]

Thus distinct private `P` classes never merge.

### T classes

For `x != y`, the private supports `e_x` and `e_y` differ, so

\[
(-b_x,-e_x)
\not\parallel
(-b_y,-e_y).
\]

Thus distinct `T` classes never merge.

### Q versus private classes

Every `Q_x` normal has zero private part.  Every `P_y` and `T_y` normal has a nonzero private coordinate. Therefore

\[
Q_x\not\parallel P_y,
\qquad
Q_x\not\parallel T_y
\]

for every unresolved source coordinate.

### P versus T

A `P_x` normal can be projectively parallel to `T_x` only after the source normal `b_x` has vanished, i.e. only after `q_x` has become a source-level constant.  It cannot happen while `q_x` is unresolved.

### Q versus Q

Finally,

\[
Q_x\parallel Q_y
\iff
b_x\parallel b_y.
\]

Moreover their forbidden offsets are exactly the source AF3 forbidden offsets. Hence every cross-gadget APSQ parallel class is precisely a source-coordinate APSQ class.

### Theorem GAF3-1 — no hidden cross-gadget APSQ channel

Before source coordinates become constant, the only APSQ interactions involving more than one regularizer gadget are the `Q_x/Q_y` interactions already present in the source AF3 system.

The private `P/T` coordinates cannot create an additional cross-gadget pin, duplicate, or three-offset certificate.

## 4. Iteration after source pins

APSQ may pin an affine source functional and thereby make some `q_x` constant.  The corresponding gadget then closes locally.

### q_x = 0

The constraint `Q_x:q_x != 0` is violated identically.  This is exactly the same source-level UNSAT terminal.

### q_x = 1

`Q_x` is safe and disappears.  The two remaining constraints are

\[
p_x\ne0,
\qquad
-p_x\ne0,
\]

so they are duplicates.  The local fiber has two allowed extensions `p_x in {1,2}` and produces no condition on another source coordinate.

### q_x = 2

`Q_x` is safe and disappears.  The remaining constraints are

\[
p_x\ne0,
\qquad
2-p_x\ne0.
\]

They are one two-offset parallel class and APSQ deterministically pins

\[
p_x=1.
\]

Again the effect is purely local.

Therefore every source-level APSQ substitution preserves the direct-product structure: further private simplifications occur inside individual gadgets and never create a new relation among distinct unresolved source coordinates.

### Theorem GAF3-2 — full iterative factorization

Run exact APSQ to saturation on `R(Phi)`.  Its sequence of nonlocal pins/UNSAT events on the `q` variables is exactly a valid APSQ sequence on the source affine system `Aq=1`.  All additional regularizer actions are independent local duplicate removals or local `p_x` pins determined by already fixed `q_x` values.

Thus global APSQ on the regularizer factors through source APSQ; it has no extra hidden cross-gadget propagation channel.

## 5. Exact witness projection and extension

After source APSQ reaches a nowhere-zero source solution `q`, every gadget can be extended independently:

```text
q_x = 1 -> choose p_x=1 or 2;
q_x = 2 -> choose p_x=1.
```

Then `Q_x,P_x,T_x` are all nonzero. Conversely any full-support regularizer word has every `q_x` nonzero and the old source rows give

\[
q_x+q_y+q_z=1,
\]

so the `q` projection is a full-support source AF3 word.

Hence

\[
\boxed{
R(\Phi)\text{ AF3-full-support}
\iff
\Phi\text{ AF3-full-support}.
}
\]

This is the finite-field form of the already proved Boolean Karp equivalence, now with the exact global APSQ factorization exposed.

## 6. RNCDP excess transfer at an APSQ-fixed source

Suppose source APSQ is already at a fixed point with

```text
u unresolved source coordinate constraints,
r = rank of their normal matrix,
epsilon_source = u-r.
```

Assume none of these source coordinates is constant.  In the regularized residual, each unresolved source variable contributes the three classes `Q_x,P_x,T_x`.

The `P_x` normals add `u` independent private directions, while

\[
T_x=-Q_x-P_x.
\]

Therefore

\[
\operatorname{rank}(N_R)=r+u,
\qquad
m_R=3u,
\]

and

\[
\boxed{
\epsilon_R
=3u-(r+u)
=2u-r
=u+\epsilon_{source}.
}
\]

Thus the regularizer can increase RNCDP excess linearly even though it adds no new source-level semantic difficulty.

This is an anti-loop warning: large RNCDP excess produced by private equality gadgets is not by itself a hard-core certificate.

## 7. PG15 finite control prediction

For the canonical PG15 source, source AF3/APSQ has

```text
u=11 distinct source classes,
rank=4,
epsilon_source=7,
```

with no source pin.  Regularizing PG15 therefore predicts

```text
source Q classes = 11,
private P classes = 15,
private T classes = 15,
total classes = 41,
normal rank = 19,
epsilon_regularized = 22.
```

The companion checker verifies these values symbolically from the exact affine parameterization.

## 8. Architectural consequence

The previous gadget-local theorem left open the possibility that assembling many gadgets could create a new global APSQ mechanism absent from the source.

GAF3-1/GAF3-2 close that specific loophole:

```text
GLOBAL REGULARIZER APSQ POWER
= SOURCE APSQ POWER
  + LOCAL PRIVATE-FIBER CLEANUP.
```

Therefore the EQ3 regularizer cannot be used to justify a universal AF3/APSQ solver by claiming emergent cross-gadget projective propagation.

A universal algorithm must still solve or contract the source APSQ residual itself, or route it into another exact polynomial representation class.

## 9. Updated frontier

The live universal target remains

```text
R5_E9_AF3_EXCESS_OR_REPRESENTATION_DICHOTOMY_GATE_V2
```

with the additional anti-loop rule:

```text
EQ3 regularization + global APSQ is not a new compression lane beyond source APSQ;
private-gadget RNCDP excess is bookkeeping, not semantic progress.
```

## 10. Ceiling

```text
GLOBAL AFFINE SOLUTION FACTORIZATION OF R(Phi)
= PROVED

CROSS-GADGET APSQ INTERACTIONS
= SOURCE Q-COORDINATES ONLY
= PROVED

FULL ITERATED APSQ ON REGULARIZER
= SOURCE APSQ + LOCAL PRIVATE CLEANUP
= PROVED

FULL-SUPPORT WITNESS PROJECTION / EXTENSION
= PROVED

REGULARIZED RNCDP EXCESS AT SOURCE FIXED POINT
= u + epsilon_source
= PROVED

UNIVERSAL SOURCE APSQ RESIDUAL SOLVER
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```