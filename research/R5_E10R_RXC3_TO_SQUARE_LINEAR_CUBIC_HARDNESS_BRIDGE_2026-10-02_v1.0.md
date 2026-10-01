# R5 E10R — RX3C hardness bridge into square linear-cubic Exact-One

Date: 2026-10-02

Status: **EXACT REDUCTION / HARDNESS GATE CLOSED**

Claim ceiling:

```text
TARGET_CLASS_NP_HARD = ESTABLISHED_BY_REDUCTION_FROM_RX3C
TARGET_CLASS_IN_NP = TRIVIAL
TARGET_CLASS_NP_COMPLETE = ESTABLISHED
POLYNOMIAL_TARGET_SOLVER = NOT_ESTABLISHED
P_VS_NP = OPEN
```

Executable clean-room control:

```text
experiments/r5_e10r_single_overlap_rxc3_hardness_bridge.py
```

## 1. Source problem

Use RESTRICTED EXACT COVER BY 3-SETS (RX3C):

- universe `X` has `N=3q` elements;
- every candidate set has size 3;
- every element occurs in exactly three candidate sets;
- decide whether some candidate sets cover every element exactly once.

RX3C is NP-complete; a standard source is Gonzalez (1985), *Clustering to Minimize the Maximum Intercluster Distance*, Theoretical Computer Science 38, 293–306.

Double-counting incidences already gives `|C|=|X|=N` in every RX3C instance.

The target additionally requires **linearity**: any two candidate triples intersect in at most one element.  The constant gadget below enforces this without changing exact-cover existence.

## 2. Local gadget

For each source triple

\[
C_j=\{x_1,x_2,x_3\},
\]

introduce six local elements `z1,...,z6` and the five triples

\[
\begin{aligned}
L_1&=\{x_1,z_1,z_4\},\\
L_2&=\{x_2,z_2,z_5\},\\
L_3&=\{x_3,z_3,z_6\},\\
L_4&=\{z_1,z_2,z_3\},\\
L_5&=\{z_4,z_5,z_6\}.
\end{aligned}
\]

Create a primed duplicate of all old/source and local elements and all five `L` triples.  Finally introduce `t1,t2,t3` and

\[
\begin{aligned}
D_1&=\{z_2,z_6,t_1\},&
D_2&=\{z_3,z_4,t_2\},&
D_3&=\{z_1,z_5,t_3\},\\
D_4&=\{z'_2,z'_6,t_2\},&
D_5&=\{z'_3,z'_4,t_3\},&
D_6&=\{z'_1,z'_5,t_1\},\\
D_7&=\{t_1,t_2,t_3\}.
\end{aligned}
\]

This is a constant 17-triple gadget.

## 3. All-or-none lemma

Let the same symbol also denote the 0/1 variable indicating whether a gadget triple is selected in an exact cover.

The six unprimed local exact-cover equations are

\[
\begin{aligned}
z_1:&\quad L_1+L_4+D_3=1,\\
z_2:&\quad L_2+L_4+D_1=1,\\
z_3:&\quad L_3+L_4+D_2=1,\\
z_4:&\quad L_1+L_5+D_2=1,\\
z_5:&\quad L_2+L_5+D_3=1,\\
z_6:&\quad L_3+L_5+D_1=1.
\end{aligned}
\]

Subtract the second block of three equations from the first block and sum.  The `D` terms cancel, giving

\[
3(L_4-L_5)=0,
\]

hence

\[
L_4=L_5.
\]

Substituting back yields

\[
D_1=D_2=D_3,
\]

and then the first three equations yield

\[
\boxed{L_1=L_2=L_3.}
\]

The same calculation on the primed half gives

\[
\boxed{L'_1=L'_2=L'_3.}
\]

Thus every exact cover of the transformed instance treats each source triple as an **all-or-none 3-port block**.

The executable checker also exhausts all `2^17` local edge selections.  There are exactly eight ways to cover the 15 local internal elements, and every one satisfies the two all-or-none identities above.

## 4. SAT preservation

### Forward

Suppose `A` is an exact cover of the RX3C source.

For every `j in A`, choose

```text
L1,L2,L3,L1',L2',L3',D7.
```

For every `j not in A`, choose

```text
L4,L5,L4',L5',D7.
```

These choices cover every transformed element exactly once.

### Backward

Suppose the transformed instance has an exact cover.

By the all-or-none lemma, for every source triple `C_j`, either all of `L1,L2,L3` are selected or none are.  The only transformed triples containing an original unprimed element `x` are these port triples.  Since every original `x` must be covered exactly once, the indices `j` for which `L1,L2,L3` are selected form an exact cover of the original RX3C universe.

Therefore

\[
\boxed{I\in RX3C_{YES}\iff R(I)\in TARGET_{YES}.}
\]

The construction has constant blowup and is polynomial-time.

## 5. Exact target-class invariants

For an RX3C source with `N` elements and therefore `N` triples, the transformed instance has

\[
\boxed{17N\text{ elements and }17N\text{ triples}.}
\]

Every transformed triple has size three.

Every transformed element has degree exactly three:

- each old `x` occurs in three port triples because RX3C has occurrence exactly 3;
- every `z`/`z'` occurs in two `L` triples and one `D` triple;
- each `t_i` occurs in exactly three `D` triples.

Linearity holds:

1. inside one constant gadget, direct pairwise inspection gives intersection size at most one;
2. local elements of distinct gadgets are disjoint;
3. a port triple contains only one old source element, so even if two original RX3C triples overlap in multiple source elements, any **pair of transformed triples** shares at most one element;
4. the primed and unprimed source copies are distinct.

Hence the transformed incidence matrix `A` satisfies exactly

\[
\boxed{
A\in\{0,1\}^{n\times n},\qquad
\text{row weight}=3,\qquad
\text{column weight}=3,\qquad
\langle A_{*i},A_{*j}\rangle\le1\ (i\ne j).
}
\]

This is precisely the square linear-cubic Exact-One class used in the Gram/Hoffman research frontier.

## 6. Complexity consequence

Membership in NP is immediate: a proposed Boolean vector `x` is checked by computing `Ax` and testing `Ax=1`.

The reduction above proves NP-hardness from RX3C. Therefore

\[
\boxed{
\text{SQUARE LINEAR-CUBIC EXACT-ONE is NP-complete.}
}
\]

Consequently, if a deterministic polynomial-time algorithm is proved for **all** instances of this exact target class, then

\[
\boxed{P=NP.}
\]

No such universal polynomial algorithm is established by this reduction.  The live research gate is now purely algorithmic.

## 7. Relation to the Gram graph

For every target instance produced here,

\[
A^\top A=3I+\operatorname{Adj}(G_A),
\]

where `G_A` is 6-regular and has smallest eigenvalue at least `-3`.  Exact-One satisfiability is equivalent to

\[
\alpha(G_A)=n/3
\]

and also to

\[
\ker_{\mathbb Q}(A)\cap\{-1,2\}^n\ne\varnothing.
\]

Thus the remaining universal problem can be stated without any unresolved hardness bridge:

> Find a deterministic polynomial-time procedure that decides whether a square linear-cubic incidence matrix has a `{-1,2}` rational-kernel word, equivalently whether its Gram graph has a Hoffman-tight stable set of size `n/3`.

Until such a procedure is proved:

\[
\boxed{P\stackrel?=NP\text{ remains OPEN}.}
\]
