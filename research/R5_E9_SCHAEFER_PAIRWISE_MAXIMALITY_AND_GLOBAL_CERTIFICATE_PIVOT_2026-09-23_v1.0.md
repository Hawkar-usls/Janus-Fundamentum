# R5 E9 — Schaefer Pairwise Maximality Matrix and Global-Certificate Pivot

**Date:** 2026-09-23  
**Status:** derived source-bound closure of fixed-language pairwise mixing for the canonical Boolean carriers.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Why this audit exists

The previous gate found a positive pairwise bridge:

[
	ext{Krom} 	imes 	ext{2-affine boundary} 	o_P 	ext{Krom}.
]

The next question is whether this bridge can be enlarged by admitting more affine boundary relations, or whether further progress must come from **instance-specific global certificates** such as q-Horn rather than from a larger fixed mixed language.

Schaefer's Boolean dichotomy provides an exact maximality test once we freeze canonical bases that isolate the Horn and bijunctive/Krom classes.

## 2. Canonical bases

Use constants (U_0={0}), (U_1={1}) to remove the trivial 0-valid/1-valid cases.

### Krom-isolating base

Let
[
Gamma_K={operatorname{OR}_2,operatorname{NAND}_2,operatorname{IMP},U_0,U_1}.
]

Every relation in (Gamma_K) is bijunctive.

The language as a whole is:
- not Horn, because (operatorname{OR}_2) is not AND-closed;
- not dual-Horn, because (operatorname{NAND}_2) is not OR-closed;
- not affine, because (operatorname{OR}_2) is not affine;
- neither 0-valid nor 1-valid because both constants are present.

Hence the only Schaefer tractability reason available to (Gamma_K) is bijunctivity.

### Horn-isolating base

Let
[
H_3(x,y,z):=(
eg xee
eg yee z),
qquad
Gamma_H={H_3,U_0,U_1}.
]

The relation (H_3) is Horn.

The language as a whole is:
- not dual-Horn: (100,010in H_3) but (100ee010=110
otin H_3);
- not bijunctive: (100,010,111in H_3), but their coordinatewise majority is (110
otin H_3);
- not affine: (|H_3|=7), whereas every nonempty affine Boolean relation has cardinality a power of two;
- neither 0-valid nor 1-valid after adding both constants.

Hence the only Schaefer tractability reason available to (Gamma_H) is Horn closure.

## 3. Maximality theorem for Krom × affine

Let (R) be any Boolean affine relation.

### Theorem E9-KA2

[
operatorname{CSP}(Gamma_Kcup{R})in P
quadLongleftrightarrowquad
R	ext{ is bijunctive}.
]

Because (R) is affine, the right side is equivalent to (R) being **bijunctive affine**, i.e. definable by unary constraints, equalities and disequalities:
[
x_i=c,qquad x_i=x_j,qquad x_i
e x_j.
]

Equivalently, (R) is 2-affine.

#### Proof

If (R) is bijunctive, every relation in the enlarged language is bijunctive, so Schaefer gives polynomial-time tractability.

If (R) is not bijunctive, the enlarged language is:
- not Horn due to OR2;
- not dual-Horn due to NAND2;
- not affine due to OR2;
- not bijunctive due to (R);
- not 0-valid / 1-valid due to (U_1/U_0).

Schaefer's dichotomy therefore gives NP-completeness.

Thus the 2-affine bridge found in the preceding audit is maximal relative to the full canonical Krom carrier.

## 4. Exact form of affine ∩ Horn

A second maximality statement needs the structure of affine relations that are Horn.

### Lemma E9-HA0

A nonempty Boolean relation is both affine and Horn iff it is definable by:
- unary pinnings (x_i=0) or (x_i=1);
- equalities (x_i=x_j).

No unpinned disequality is allowed.

#### Proof

Horn relations are closed under coordinatewise AND.

Let (R) be affine and AND-closed. Remove all fixed coordinates. In the remaining relation every coordinate takes both values.

For every remaining coordinate (i), choose a tuple (r_iin R) with ((r_i)_i=0). Since (R) is AND-closed,
[
igwedge_i r_i = 0^nin R.
]

Therefore the reduced affine relation contains zero and is a linear subspace (Vle mathbb F_2^n). Identifying vectors with their supports, (V) is closed under:
- symmetric difference, because it is linear;
- intersection, because it is AND-closed;
- hence union, because (Acup B=(A	riangle B)	riangle(Acap B)).

Thus (V) is a finite Boolean algebra of subsets of ([n]). Its atoms form a partition of the coordinates; every vector in (V) is exactly a union of atoms. Therefore coordinates in one atom are always equal, while distinct atoms vary independently. So (V) is defined exactly by equalities within the atoms.

Restoring removed fixed coordinates adds only unary pinnings.

The converse is immediate: pinnings and equalities are affine and Horn.

### Polynomial recognition from (Mx=b)

Let (x^0) be one solution and (W=operatorname{rowspan}(M)).

Let (G_H) contain:
- every weight-one vector in (W);
- every weight-two vector (win W) with (wcdot x^0=0).

Then
[
R	ext{ is affine-Horn}
iff
operatorname{span}(G_H)=W.
]

This is polynomial by Gaussian elimination over only (O(n^2)) candidate vectors.

## 5. Maximality theorem for Horn × affine

Let (R) be Boolean affine.

### Theorem E9-HA1

[
operatorname{CSP}(Gamma_Hcup{R})in P
quadLongleftrightarrowquad
R	ext{ is Horn}.
]

By Lemma E9-HA0, for affine (R) this means exactly pinnings plus equalities.

If (R) is Horn, the whole language remains Horn.

If (R) is not Horn, (Gamma_H) has already eliminated every Schaefer tractability class other than Horn, and constants eliminate 0/1-validity. Hence the enlarged language is NP-complete.

Thus the maximal affine bridge into a full Horn carrier is strictly smaller than the maximal affine bridge into Krom:

[
egin{array}{c|c}
	ext{pair} & 	ext{maximal affine slice}\
hline
	ext{Krom}	imes	ext{Affine} & 	ext{pins + equalities + disequalities}\
	ext{Horn}	imes	ext{Affine} & 	ext{pins + equalities}
end{array}
]

## 6. Krom × Horn fixed-language maximality

Let (R) be any bijunctive relation.

Relative to the full Horn-isolating base (Gamma_H):
[
operatorname{CSP}(Gamma_Hcup{R})in P
iff
R	ext{ is Horn}.
]

So a generic Krom relation that is not Horn cannot simply be added to a full Horn language without leaving every Schaefer tractable class.

This does **not** contradict q-Horn. q-Horn obtains tractability from an **instance-level global certificate**, not because the unrestricted union of all Horn and Krom relations forms one tractable fixed language.

## 7. 2026 knowledge-compilation control

Berkholz–Mengel–Wilhelm, arXiv:2311.10040v3 (4 Sep 2026), prove a complete DNNF-compilation dichotomy.

For Boolean languages their Theorem 35 says:

- if every relation is bijunctive affine—equivalently conjunctions of equality, disequality and unary constraints—then instances compile in polynomial time even to OBDD;
- otherwise there is a family of instances over that fixed language requiring DNNF size (2^{Omega(|arphi_n|)}).

Therefore a universal E9 construction cannot hope to turn arbitrary Horn, Krom, affine, q-Horn, or mixed islands into one generic polynomial DNNF currency. Native representations are essential.

A second control by de Colnet–Mengel shows something orthogonal: there are formulas with tiny final structured-DNNF representations for which **every bottom-up compilation** by repeated conjunction and structure modification must create exponential intermediate structured-DNNFs.

So even “the final summary is small” does not by itself certify a polynomial join pipeline.

## 8. Strategic conclusion

The fixed-language pairwise search has reached a sharp wall.

For the canonical Boolean carriers, maximal safe affine slices are already characterized by their shared Schaefer closure. Enlarging them gives NP-complete fixed languages.

Therefore the next universal mechanism, if it exists, must exploit **instance-specific global structure** that is invisible to fixed-language union.

q-Horn is the model positive control: the unrestricted Horn+Krom union is hard, yet a globally certified subset of mixed instances is tractable.

## 9. New gate

`R5_E9_GLOBAL_COMPATIBILITY_CERTIFICATE_LIFT_GATE_V1`

Seek a polynomially constructible certificate (C(F)) for an arbitrary instance such that:

1. (C(F)) assigns native carrier/bridge states globally, not independently edge-by-edge;
2. local joins are certified by the global state;
3. the certificate is preserved under join/project updates;
4. total state remains polynomial in original input length;
5. q-Horn is recovered as a strict positive control;
6. affine and E8 cube/few-subpowers islands can be represented without forcing them into DNNF or another single currency;
7. no unbounded assignment/backdoor enumeration is hidden in certificate construction.

No universal PASS is claimed.

