# R5 E9 — Ternary Full-Support Matroid and Common Cubic Sinkless Orientation Normal Form

**Date:** 2026-09-23  
**Status:** exact JANUS-derived equivalence + source-bound prior-art firewall.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.  
**Novelty boundary:** the finite-field/characteristic-polynomial and general full-weight-code facts are classical; no novelty claim is made for them. The JANUS contribution here is the exact binding of the pair-defect hard core to the structured systematic ternary matrix [I;A2;A3] and to a simultaneous orientation problem.

## 1. Start from the exact pair-glue normal form

Let D1 partition the original variables into pairs. Orient each pair as

[
(a_i,b_i),qquad i=1,ldots,m.
]

Impose the activated zero-syndrome condition

[
x_{a_i}+x_{b_i}=1.
]

Set

[
t_i=x_{a_i},qquad x_{b_i}=1-t_i,
]

and introduce a spin

[
q_i:=2t_i-1in{-1,+1}.
]

Over (mathbb F_3),

[
{-1,+1}=mathbb F_3^*.
]

For a D2/D3 ternary clause r define a signed row

[
a_rin{0,pm1}^m
]

by:
- +1 in coordinate i if the row contains a_i;
- -1 if it contains b_i;
- 0 otherwise.

Linearity of the three partitions guarantees that a row contains at most one endpoint of any D1 pair.

## 2. NAE is nonvanishing over F3

For one ternary row r, after pair substitution,

[
sum_{vin r}x_v
=
rac{3+a_rq}{2}
]

over the integers.

Since q_i in {+-1}, the signed sum a_r q can only be

[
-3,-1,+1,+3.
]

The positive NAE constraint is satisfied exactly when the original triple sum is 1 or 2, equivalently

[
a_rq=pm1.
]

Therefore:

[
oxed{
NAE(r)
iff
a_rq
e0pmod3.
}
]

Let A2 and A3 be the signed-row matrices of D2 and D3.

The activated hard fiber is therefore exactly

[
qin(mathbb F_3^*)^m,
qquad
A_2qin(mathbb F_3^*)^{|D2|},
qquad
A_3qin(mathbb F_3^*)^{|D3|}.
]

## 3. Systematic ternary code

Stack

[
H=
egin{pmatrix}
I_m\
A_2\
A_3
end{pmatrix}.
]

Because of the identity block, H has column rank m.

Define the ternary linear code

[
C={Hq:qinmathbb F_3^m}.
]

Then the map q -> Hq is injective.

The activated SAT instance has a witness iff C contains a codeword with no zero coordinate.

Thus:

[
oxed{
PAIR_DEFECT_ZERO
iff
C	ext{ has a full-support codeword}.
}
]

## 4. Characteristic polynomial exact zero-test

Let M_C be the vector matroid associated with a generator matrix of C, equivalently with

[
G=H^T.
]

The Crapo-Rota Critical Theorem, in coding-theoretic form, states that for an [N,m]_q code C the number of ordered one-tuples of codewords whose support is the full coordinate set is

[
chi_{M_C}(q).
]

At q=3:

[
#{cin C:operatorname{supp}(c)=[N]}
=
chi_{M_C}(3).
]

Therefore:

[
oxed{
PAIR_DEFECT_ZERO
iff
chi_{M_C}(3)>0.
}
]

This is an existence/zero-test identity, not an efficient evaluation claim.

## 5. Relation to the older JANUS binary characteristic-polynomial line

The old q=2 full-support route had a special binary collapse: full-support binary codewords and (chi_M(2)) reduce to a rigid affine/bipartite/no-odd-circuit condition in the corresponding binary setting.

The present q=3 object does not inherit that collapse.

S. Barg (1994) proves that deciding whether a general ternary linear code contains a codeword of weight equal to the code length is NP-complete.

Hence:

GENERAL TERNARY FULL-SUPPORT CODEWORD
=
NP-COMPLETE.

This is a prior-art firewall against treating the code reformulation itself as the missing polynomial algorithm.

The only viable opportunity is the much more special JANUS matrix structure below.

## 6. Current prime-field source boundary

Jafari (2026), *Frobenius-Power Ideals and Hyperplane Avoidance for Representable Matroids*, proves positivity results for characteristic polynomials over extension fields (q=p^k) under a decomposition-cover condition.

That theorem is genuinely useful context but does not solve the present q=3 prime-field instance.

The paper explicitly separates the prime-field strengthening as a different problem/conjectural direction.

Therefore no current source theorem found in this audit collapses the JANUS (chi_M(3)>0) zero-test.

## 7. Each A_k is a cubic graph incidence matrix

Fix k in {2,3}.

Create graph G_k:

- one graph vertex for every ternary clause in D_k;
- one graph edge e_i for every D1 pair (a_i,b_i).

Because D_k is a partition of all original variables:
- a_i lies in exactly one D_k clause;
- b_i lies in exactly one D_k clause.

Because the source geometry is linear, those two clauses are distinct: otherwise a D1 pair and one D_k triple would intersect in two variables.

Join those two clause-vertices by edge e_i.

Orient e_i from the D_k clause containing b_i to the D_k clause containing a_i.

Then:
- the incidence coefficient at the a_i endpoint is +1;
- the incidence coefficient at the b_i endpoint is -1.

Therefore A_k is exactly the oriented vertex-edge incidence matrix of G_k over (mathbb F_3).

Every D_k clause contains three variables, so every graph vertex has degree three.

Thus G_2 and G_3 are cubic graphs on the **same labeled edge set** E=D1.

## 8. Spins are common edge reversals

Take the reference orientations above.

For edge e:
- q_e=+1 keeps its reference orientation;
- q_e=-1 reverses it.

The same spin q_e is used in both G_2 and G_3, although the two reference orientations may differ.

At a cubic vertex v of G_k, the coordinate

[
(A_kq)_v
]

is the signed incidence sum/divergence.

Three incident signs are each +-1.

Modulo 3:

[
(A_kq)_v=0
]

iff all three incident edges point into v or all three point out of v.

Equivalently v is a sink or a source.

If the orientation is mixed 1-in/2-out or 2-in/1-out, the divergence is +-1 and therefore nonzero in F3.

Hence:

[
A_kqin(mathbb F_3^*)^{V(G_k)}
]

iff the q-induced orientation of G_k has no source and no sink.

## 9. Common cubic orientation theorem

Combining the two graph blocks:

### Theorem CCSO-1

The pair-defect zero-syndrome hard fiber is satisfiable iff there exists one edge-sign vector

[
qin{pm1}^E
]

such that applying q as a common set of edge reversals makes **both** cubic graphs G_2 and G_3 simultaneously source-free and sink-free.

In symbols:

[
oxed{
0in E(Mod(B))
iff
exists q:
G_2^q	ext{ and }G_3^q
	ext{ are both source/sink-free}.
}
]

Call this problem:

[
	exttt{COMMON_CUBIC_SINKLESS_ORIENTATION}.
]

The reduction in the previous JANUS artifacts proves NP-hardness for the structured instances generated from the DDD source family.

A focused web/prior-art search found literature on ordinary sink/source-free orientations and on other simultaneous-orientation notions, but no exact public match for this two-cubic-graphs/common-edge-sign formulation.

No novelty claim is made absent a dedicated exhaustive prior-art audit.

## 10. Why this is stronger than the generic syndrome-image view

The object is no longer:

> represent an arbitrary relation E(Mod(B)).

It is:

> choose one common sign on each edge so that two explicit cubic graphic incidence systems are simultaneously nowhere-zero over F3.

This exposes three pieces of additional structure:

1. both constraint systems are graphic incidence systems;
2. every local constraint has degree exactly three;
3. the two systems share the same edge-sign variables.

The generic ternary-code hardness result does not exploit this special pair-of-graphic structure.

## 11. Structured matroid form

The generator matrix is

[
G=
egin{pmatrix}
I_m & A_2^T & A_3^T
end{pmatrix}.
]

So M_C has:
- a distinguished basis indexed by common edges E;
- one nonbasis element for every vertex of G_2 and G_3;
- every nonbasis column has exactly three nonzero entries;
- each basis coordinate occurs in exactly two G_2 vertex columns and exactly two G_3 vertex columns.

This is the precise sparse systematic ternary matroid subclass to study.

The next matroid theorem, if one exists, must use this structure; general ternary full-support positivity is already NP-hard.

## 12. New active gate

### R5_E9_COMMON_CUBIC_SINKLESS_ORIENTATION_GATE_V1

Input:
two cubic graphs G_2,G_3 on one labeled edge set E, with fixed reference orientations.

Question:
is there a common reversal vector q in {+-1}^E making both orientations source-free and sink-free?

Required JANUS algorithmic object:
a polynomially synthesizable witness-preserving contraction/augmentation rule that exploits the **pair of graphic systems jointly**.

Forbidden:
- generic ternary-code search;
- explicit 2^|E| orientation enumeration;
- expansion back to degree-4 SAT;
- treating G_2 and G_3 independently and intersecting exponential solution sets;
- generic evaluation of the full characteristic polynomial.

Promising structural primitives to test:
- alternating/cycle reversal actions;
- cut/cycle decompositions in the two graphic systems;
- common decomposition blocks;
- graphic-matroid intersection-like certificates;
- contractions that reduce one common edge while preserving both no-source/no-sink conditions.

The signed-balanced pair-glue test remains a preprocessing YES rule before entering this gate.

D1 = EMPTY.
P_VS_NP = OPEN.
