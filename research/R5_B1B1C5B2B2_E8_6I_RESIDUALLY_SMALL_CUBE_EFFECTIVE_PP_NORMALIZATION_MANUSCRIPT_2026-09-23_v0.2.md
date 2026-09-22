# R5 E8 6I — Effective Short pp-Definitions in the Residually-Small Cube-Term Regime

**Version:** v0.2 — bridge-lemma formalization after hostile standalone replay  
**Status:** CANDIDATE THEOREM; mathematical core survived first cold replay; THEOREM_SEAL remains HOLD pending a second independent cold replay and prior-art/novelty review.

## 1. Candidate theorem

Let \\(\\mathcal K\\) be a fixed finite family of finite similar algebras with a common \\(k\\)-cube term (equivalently, a common \\(k\\)-edge term), and assume \\(\\mathsf V(\\mathcal K)\\) is residually small.

For
\\[
R=\\operatorname{Sg}(a^1,\\ldots,a^m)\\le A_1\\times\\cdots\\times A_n,
\\qquad A_i\\in\\operatorname{HS}(\\mathcal K),
\\]
given by generators, the candidate algorithm constructs in deterministic time polynomial in the encoded generator-input length \\(L\\) a pp-definition \\(\\varphi_R\\) over one fixed finite relational basis \\(\\Gamma_{\\mathcal K}\\), with
\\[
\\varphi_R(\\bar x)\\iff \\bar x\\in R
\\]
and
\\[
|\\varphi_R|=O\\!\\left(n^{\\max(2,k-1)}\\right).
\\]

The proof uses BMS standardized compact representations operationally and Bulín–Kompatscher (BK) full signatures only as mathematical counting potentials. These two representation notions are not identified.

This manuscript does **not** claim THEOREM_SEAL.

---

## 2. Source backbone

### 2.1 Berman–Idziak–Marković–McKenzie–Valeriote–Willard

For a fixed integer \\(k\\ge2\\), a variety has a \\(k\\)-cube term iff it has a \\(k\\)-edge term. Thus one fixed parameter \\(k\\) can be used for the cube-term/BMS and edge-term/BK interfaces.

### 2.2 Bulatov–Mayr–Szendrei (BMS)

Use:
- Theorem 2.1: cube term implies congruence modularity.
- Theorem 2.2: term operations are affine/linear between blocks of abelian congruences.
- Theorem 2.3 and Corollary 2.4: residual-smallness in the finite congruence-modular setting yields a finite natural residual bound.
- polynomial reduction \\(\\operatorname{SMP}(\\mathcal K)\\leftrightarrow\\operatorname{SMP}(\\operatorname{HS}\\mathcal K)\\).
- Theorem 4.16: \\(\\operatorname{SMP}(\\mathcal K)\\leftrightarrow_P\\operatorname{CompactRep}(\\mathcal K)\\).
- polynomial construction of compact representations of intersections from compact representations.
- Theorem 5.3 / Remark 5.4 and Algorithm 7: canonical small-projection/coherence-block localization.
- Definition 6.2 and Algorithm 8: the d-coherent core.
- Claims 6.6–6.7: unary-polynomial contributions and target membership as subgroup membership.
- Theorem 6.5: SMP is in P in the residually-small cube-term regime.

### 2.3 Bulín–Kompatscher (BK), arXiv:2305.01984v3

Use:
- Theorem 18 / Corollary 19: a BK compact representation generates the relation; full signature plus all \\(<k\\) projections determines comparable invariant relations.
- Theorem 20: critical relation of arity at least \\(k\\) has the parallelogram property.
- Lemma 21: at most \\(n|A|^2\\) nonredundant critical parallelogram conjuncts after the low-projection shell.
- Lemma 22: nonreduced critical parallelogram relations reduce through coordinate linkedness quotients and are full inverse images.
- Theorem 25: residual-finite reduced critical recursion through \\(A_{1,2},Q,R'\\), with linear definition per critical relation.
- Question 30: efficient construction of short pp-definitions from generators remains open in the source, even under residual finiteness.

---

## 3. Bridge Lemma 0 — Residual-small scope imports the BK residual-finite universe

**Lemma 0.** Under the hypotheses of the candidate theorem, \\(\\mathsf V(\\mathcal K)\\) satisfies the residual-finiteness hypothesis used by BK Theorem 25.

**Proof.** Let
\\[
\\mathbf A:=\\prod_{\\mathbf B\\in\\mathcal K}\\mathbf B.
\\]
Because \\(\\mathcal K\\) is finite, \\(\\mathbf A\\) is finite and
\\[
\\mathsf V(\\mathbf A)=\\mathsf V(\\mathcal K).
\\]
The common \\(k\\)-cube term is preserved by finite products; by BMS Theorem 2.1, \\(\\mathsf V(\\mathbf A)\\) is congruence modular. By assumption it is residually small. BMS Theorem 2.3 (the Freese–McKenzie residual-bound theorem in this setting) therefore gives a natural number \\(c\\) such that every subdirectly irreducible algebra in \\(\\mathsf V(\\mathbf A)\\) has cardinality \\(<c\\).

The language is fixed and finite. Hence, up to isomorphism, only finitely many finite algebras of cardinality \\(<c\\) exist in this language. Thus the subdirectly irreducible members of \\(\\mathsf V(\\mathcal K)\\) form, up to isomorphism, a finite family of finite algebras. This is precisely the residual-finiteness hypothesis used by BK Theorem 25. ∎

Consequently there is a fixed finite SI/factor universe and a fixed finite multisorted basis \\(\\Gamma_{\\mathcal K}\\).

---

## 4. Bridge Lemma 1 — Polynomial compact construction of the low-projection shell

Put
\\[
s:=\\max(k,3).
\\]
For every \\(I\\subseteq[n]\\) with \\(|I|<s\\), let
\\[
P_I:=\\operatorname{proj}_I(R)
\\]
and
\\[
C_I:=\\operatorname{proj}_I^{-1}(P_I).
\\]
Define
\\[
C_0:=\\bigcap_{|I|<s}C_I.
\\]

**Lemma 1.** From a BMS standardized compact representation of \\(R\\), a standardized compact representation of \\(C_0\\) is computable in polynomial time.

**Proof.**

1. **Materialize each fixed-arity table \\(P_I\\).**  
   Project the compact generators of \\(R\\) to \\(I\\). They generate \\(P_I\\). Since \\(|I|<s\\) and \\(s,\\mathcal K\\) are fixed, the ambient product on \\(I\\) has constant cardinality. Enumerate it and use SMP on the projected generators to recover the exact table \\(P_I\\) in constant-many polynomial membership tests.

2. **Construct a compact representation of each cylinder \\(C_I\\).**  
   Membership in \\(C_I\\) depends only on the constant-size coordinate set \\(I\\). The local witnesses and derived-fork witnesses required by a BMS standardized representation can therefore be constructed explicitly: for every required fixed-size local projection/fork pattern, enumerate the constant-size restriction on \\(I\\), choose a compatible tuple of \\(P_I\\), and fill coordinates outside the constrained set arbitrarily. The number of required witnesses is polynomial in \\(n\\).

3. **Intersect.**  
   BMS note that from compact representations of two subalgebras, Dalmau's algorithm constructs a compact representation of their intersection in polynomial time; together with Theorem 4.16 this is polynomial in the present scope. There are
   \\[
   \\sum_{i<s}\\binom ni=O(n^{s-1})
   \\]
   cylinders. Repeated intersection therefore yields compact \\(C_0\\) in polynomial time. ∎

The shell itself contributes
\\[
O(n^{s-1})=O(n^{\\max(2,k-1)})
\\]
fixed-arity pp-atoms.

For \\(k=2\\), the extra pair projections required by BMS localization raise the shell only to \\(O(n^2)\\), which is still the BK degree \\(\\max(2,k-1)=2\\).

---

## 5. Bridge Lemma 2 — Operational representation vs BK signature potential

BMS standardized representations and BK compact representations are **not** treated as identical.

- **Operational state:** BMS standardized compact representation, because BMS supplies the polynomial algorithms needed by the compiler.
- **Counting potential:** the abstract BK feature set
  \\[
  \\Phi(S):=\\operatorname{Sig}_{BK}(S)\\;\\cup\\;
  \\{(I,a):|I|<k,\\ a\\in\\operatorname{proj}_I(S)\\}.
  \\]

**Lemma 2.** Every strict invariant extension \\(S<T\\) changes \\(\\Phi\\).

**Proof.** If the BK signatures and all \\(<k\\) projections were equal, BK Corollary 19 would imply \\(S=T\\), contradiction. ∎

The number of possible features is
\\[
O(n|A|^2)+
\\sum_{i<k}\\binom ni O(|A|^i)
=
O(n^{\\max(2,k-1)})
\\]
for the fixed multisorted factor universe.

This is only a mathematical termination potential. The algorithm never needs to compute the full BK signature.

In the **outer** critical-decomposition chain, the \\(<k\\) projections have already been frozen by \\(C_0\\), so each nonredundant critical conjunct strictly decreases only the BK signature. BK Lemma 21 therefore gives the sharper \\(O(n)\\) bound.

---

## 6. Lemma A — SAFEEXT and pointed maximal separators

For invariant \\(S\\) and \\(y\\notin S\\), define
\\[
\\operatorname{SAFEEXT}(S,y)
\\]
to return a tuple \\(t\\notin S\\) satisfying
\\[
y\\notin\\operatorname{Sg}(S\\cup\\{t\\}),
\\]
or certify that none exists.

Repeated safe extensions produce
\\[
S_0<S_1<\\cdots<S_m
\\]
while excluding \\(y\\). By Lemma 2, \\(m=O(n^{\\max(2,k-1)})\\). Recompact after every extension using SMP \\(\\leftrightarrow\\) CompactRep.

When no safe extension exists, every strict invariant superrelation of \\(S_m\\) contains \\(y\\). Therefore
\\[
S_m^*:=\\operatorname{Sg}(S_m\\cup\\{y\\})
\\]
is the unique cover of \\(S_m\\); hence \\(S_m\\) is completely meet-irreducible.

---

## 7. Lemma B — Old-skeleton cross-fibre affine avoidance

Let \\(B\\) be a d-coherent old-skeleton subalgebra, with product abelian congruence \\(\\rho\\) as in BMS Algorithm 8. Let \\(q\\) be an old quotient-skeleton class and let \\(q_y\\) be the class of the target \\(y\\).

Choose transversal representatives \\(o_q,o_y\\in O\\) and put
\\[
G_q=o_q/\\rho,\\quad K_q=B\\cap G_q,\\quad M_q=G_q/K_q,
\\]
\\[
G_y=o_y/\\rho,\\quad K_y=B\\cap G_y,\\quad M_y=G_y/K_y.
\\]

If the computation is taking place inside the SI expansion with bundle-compatibility restrictions, let \\(L_q\\subseteq G_q\\) denote the liftable part containing \\(K_q\\), and put
\\[
N_q:=L_q/K_q\\le M_q.
\\]
The liftable image is a subalgebra; unary polynomial maps with parameters in \\(B\\) preserve it. Hence every relevant induced linear map below restricts to \\(N_q\\).

Let
\\[
p_1,\\ldots,p_m
\\]
be the Algorithm-8 unary polynomial types whose output class is \\(q_y\\). Here \\(m=O_{\\mathcal K}(1)\\). By BMS Theorem 2.2,
\\[
p_i(x)=p_i(o_q)+L_i(x-o_q)
\\]
between the corresponding abelian blocks. Since the parameters and \\(o_q\\) lie in \\(B\\),
\\[
p_i(o_q)\\in K_y,
\\qquad
L_i(K_q)\\subseteq K_y.
\\]
Thus each \\(L_i\\) induces
\\[
\\bar L_i:N_q\\to M_y.
\\]

Let \\(e\\) be the lcm of the exponents of all induced abelian groups arising from the fixed family \\(\\mathcal K\\). This is a constant. Define
\\[
\\Lambda_{q\\to q_y}
:=
\\left\\{
\\sum_{i=1}^{m}c_i\\bar L_i:
c_i\\in\\mathbb Z/e\\mathbb Z
\\right\\}.
\\]
Therefore
\\[
|\\Lambda_{q\\to q_y}|\\le e^m=O_{\\mathcal K}(1).
\\]

For a candidate \\(t\\in L_q\\), write
\\[
v=(t-o_q)+K_q\\in N_q,
\\qquad
\\bar y=(y-o_y)+K_y\\in M_y.
\\]

**Lemma B.**
\\[
y\\in\\operatorname{Sg}(B,t)
\\iff
\\exists L\\in\\Lambda_{q\\to q_y}:L(v)=\\bar y.
\\]

**Proof.** BMS Claims 6.6–6.7 say that target membership is membership in the subgroup generated by the unary-polynomial contributions of the generators. After quotienting by the old target subgroup \\(K_y\\), all old contributions vanish. The only new contributions from \\(t\\) are \\(\\bar L_1(v),\\ldots,\\bar L_m(v)\\). Since the target group has exponent dividing \\(e\\),
\\[
\\langle\\bar L_1(v),\\ldots,\\bar L_m(v)\\rangle
=
\\left\\{
\\sum_i c_i\\bar L_i(v):c_i\\in\\mathbb Z/e\\mathbb Z
\\right\\}.
\\]
The right-hand side is exactly
\\[
\\{L(v):L\\in\\Lambda_{q\\to q_y}\\}.
\\]
This proves both directions. ∎

Hence the unsafe set inside the liftable source module is
\\[
\\operatorname{BAD}_{q,y}
=
\\{0\\}
\\cup
\\bigcup_{L\\in\\Lambda_{q\\to q_y}}
\\{v\\in N_q:L(v)=\\bar y\\}.
\\]
Each nonempty fibre is one affine coset of \\(\\ker L\\). Since \\(\\Lambda\\) is constant, exact counting of the union uses constant-size inclusion-exclusion and finite-abelian-group linear algebra. Coordinate self-reduction returns an explicit safe \\(v\\neq0\\) whenever one exists.

Thus old-skeleton SAFEEXT, including cross-fibre \\(q\\neq q_y\\), is polynomial-time decidable with a polynomial-time witness.

---

## 8. Lemma C — Quotient-changing SAFEEXT and one-original-bundle normalization

Work in the BMS SI expansion. Let the current d-coherent core \\(B\\) have old coherence block \\(E\\), and let
\\[
C=\\operatorname{Sg}(B,t)
\\]
for a globally safe quotient-changing tuple \\(t\\):
\\[
y\\notin C.
\\]

All required small-projection tests that held for \\(B\\) still hold for \\(C\\) because \\(B\\subseteq C\\). By BMS Theorem 5.3, there is a large post-extension coherence block
\\[
U\\subseteq E
\\]
such that
\\[
\\hat y|_U\\notin\\hat C|_U.
\\]

### Claim C1 — post-extension refinement

For SI coordinates \\(v,w\\in E\\), let \\(D_B(v,w)\\) and \\(D_C(v,w)\\) be their quotient-pair images. Then
\\[
D_B(v,w)\\le D_C(v,w).
\\]
If \\(D_B(v,w)\\) is the graph of the old isomorphism \\(\\phi_{vw}\\), it remains a graph after adjoining \\(t\\) iff the new quotient pair lies on that graph. A non-graph pair cannot become a graph by enlargement. Therefore
\\[
\\sim_C\\subseteq\\sim_B.
\\]
Inside \\(E\\), the new blocks are fibres of the constant-alphabet defect label induced by \\(t/\\rho\\).

Since \\(t\\) is quotient-changing and the old d-coherent core is one old quotient skeleton, \\(U\\) is proper.

### Claim C2 — original-bundle slice integrity

Let
\\[
W_j=\\{j\\}\\times\\operatorname{Irr}(B_j)
\\]
be an original-coordinate bundle. If
\\[
v,w\\in E\\cap W_j,
\\]
then their old pair quotient image is a graph. Because \\(B\\to B_j\\) is surjective, every element of \\(B_j\\)—in particular the candidate value \\(t_j\\)—satisfies this graph relation. Therefore all points of \\(E\\cap W_j\\) receive the same defect label.

Hence every post-extension block \\(U\\subseteq E\\) contains either the whole slice \\(E\\cap W_j\\) or none of it.

### Claim C3 — one-bundle normalization

Choose an original bundle \\(W_j\\) meeting \\(E\\setminus U\\), and put
\\[
V:=E\\setminus W_j.
\\]
By Claim C2,
\\[
U\\subseteq V.
\\]

The original restricted witness \\(t|_U\\) proves that an old-skeleton safe direction exists on \\(U\\). Apply Lemma B on the **liftable** source submodule to construct a liftable safe displacement \\(u\\) on \\(U\\).

Extend \\(u\\) to \\(V\\) by zero displacement relative to an old transversal representative on \\(V\\setminus U\\). Claim C2 makes this extension bundle-wise compatible: no original bundle is split between a new displacement and the old displacement. Call the lifted witness \\(u_V\\).

If
\\[
y|_V\\in\\operatorname{Sg}(B|_V,u_V),
\\]
then projection to \\(U\\) would imply
\\[
y|_U\\in\\operatorname{Sg}(B|_U,u),
\\]
contradicting safety. Hence \\(u_V\\) is safe on \\(V\\).

Finally choose a value in the omitted original coordinate \\(A_j\\) whose SI quotient labels violate at least one old quotient graph against \\(V\\). Such a value exists for the original quotient-changing \\(t_j\\). Since \\(A_j\\) is fixed finite, the algorithm need not know that original witness: it enumerates all constant-many values of \\(A_j\\) for each of the \\(O(n)\\) possible bundles \\(j\\), tests the quotient defect, and combines it with the polynomial module witness on \\(V\\).

Let the resulting full original tuple be \\(t'\\). The broken quotient graph gives
\\[
t'\\notin B.
\\]
If
\\[
y\\in\\operatorname{Sg}(B,t'),
\\]
projection to \\(V\\) would put \\(y|_V\\) in \\(\\operatorname{Sg}(B|_V,t'|_V)\\), contradiction. Thus \\(t'\\) is globally safe.

Therefore any quotient-changing safe extension is found by polynomially many one-bundle cases plus Lemma B. ∎

Combining Lemmas B and C gives polynomial SAFEEXT in the frozen residual-small cube-term scope.

---

## 9. Lemma D — Constructive dummy deletion

Let \\(S\\) be a maximal invariant superrelation of \\(R\\) excluding \\(y\\).

For coordinate \\(i\\), test the constant-many neighbours
\\[
y^{i\\leftarrow a},\\qquad a\\in A_i.
\\]

**Lemma D.**
\\[
i\\text{ is essential in }S
\\iff
\\exists a\\in A_i:
y^{i\\leftarrow a}\\in S.
\\]

If no such neighbour lies in \\(S\\), the invariant cylinder
\\[
\\operatorname{proj}_{-i}(S)\\times A_i
\\]
still excludes \\(y\\). It is a superrelation of \\(S\\); maximality forces equality, so \\(i\\) is dummy. Conversely, if \\(i\\) is dummy, the existence of such a neighbour would imply \\(y\\in S\\). ∎

Membership tests are polynomial through SMP/compact calculus. Remove all dummy coordinates.

The resulting relation is meet-irreducible and has no dummy variables, hence is critical in the BK sense. Because \\(y\\in C_0\\), a separator of essential arity \\(<k\\) cannot exclude \\(y\\). Therefore essential arity is at least \\(k\\), and BK Theorem 20 gives the parallelogram property.

---

## 10. Constructive critical decomposition

Initialize \\(C:=C_0\\). While \\(C\\neq R\\):

1. obtain \\(y\\in C\\setminus R\\) by polynomial compact comparison;
2. maximalize \\(R\\) against \\(y\\) by repeated SAFEEXT;
3. remove dummy coordinates by Lemma D;
4. record the resulting critical parallelogram separator \\(S\\);
5. replace \\(C\\) by \\(C\\cap S\\) and recompact.

Every chain relation has the same \\(<k\\) projections as \\(R\\). Therefore every nonredundant step strictly drops the BK signature, and BK Lemma 21 bounds the number of recorded critical conjuncts by \\(O(n)\\) (single-sorted bound \\(n|A|^2\\), with a fixed multisorted constant).

---

## 11. Nonreduced and reduced critical recursion

After restricting every sort to its unary projection, the critical relation is subdirect.

For a nonreduced critical parallelogram relation, compute each coordinate linkedness congruence \\(\\theta_i\\), map compact generators through
\\[
R\\to R/(\\theta_1,\\ldots,\\theta_n),
\\]
and recompact the image over \\(\\operatorname{HS}(\\mathcal K)\\). BK Lemma 22 says the quotient is reduced, critical and parallelogram and that \\(R\\) is its full inverse image.

For reduced critical \\(R\\), BK Theorem 25 defines
\\[
A_{1,2}=\\operatorname{proj}_{1,2}(R)/\\theta_{1,2},
\\]
the fixed ternary quotient graph \\(Q\\), and
\\[
R'=h(R),
\\quad
h(x_1,x_2,x_3,\\ldots,x_n)
=
([(x_1,x_2)]_{\\theta_{1,2}},x_3,\\ldots,x_n).
\\]
If \\(F_R\\) generates \\(R\\), then
\\[
h(F_R)
\\]
generates \\(R'\\). Recompact using SMP(HS(K)) \\(\\leftrightarrow_P\\) CompactRep(HS(K)). The arity drops by one. Lemma 0 puts \\(A_{1,2}\\) in the fixed finite SI universe, so \\(Q\\) is a basis relation. Recurse to arity at most three.

The fixed multisorted basis is translated back to the fixed single-sort/power basis using the source projection-graph encodings; all such translations are constant-template syntax because \\(\\mathcal K\\) and the residual universe are fixed.

---

## 12. Input-length runtime ledger

Let \\(L\\) be the encoded length of the generator input. Since the domains and language are fixed,
\\[
n\\le L,
\\qquad
m\\le L
\\]
up to a fixed encoding constant.

Let \\(P_{SMP}(x)\\), \\(P_{CR}(x)\\), and \\(P_{INT}(x)\\) be fixed polynomials bounding SMP, CompactRep and compact-intersection operations in this fixed scope.

1. Initial CompactRep uses time \\(P_{CR}(L)\\).
2. The shell uses \\(O(n^{\\max(2,k-1)})\\) constant-arity cylinders and polynomially many compact intersections.
3. Outer critical decomposition performs \\(O(n)\\) separator constructions.
4. One maximal separator has at most \\(O(n^{\\max(2,k-1)})\\) strict safe extensions by Lemma 2.
5. One SAFEEXT call enumerates only polynomially many BMS blocks/original bundles and constant-many local quotient values; each old-skeleton affine-avoidance test solves only a constant family of finite-abelian linear systems on polynomial-size data.
6. Recompaction after each strict extension uses polynomial SMP/CompactRep.
7. Each of the \\(O(n)\\) critical pieces undergoes at most \\(O(n)\\) arity-reduction steps.
8. Every intermediate compact representation has size polynomial in its current arity and hence polynomial in \\(L\\).

Therefore there is one fixed polynomial \\(P_{\\mathcal K}\\) such that
\\[
T_{build}(L)\\le P_{\\mathcal K}(L).
\\]

The pp-output contains
\\[
O(n^{\\max(2,k-1)})
\\]
shell atoms plus \\(O(n)\\) critical pieces each with an \\(O(n)\\) source recursion, hence
\\[
|\\varphi_R|
=
O(n^{\\max(2,k-1)}+n^2)
=
O(n^{\\max(2,k-1)})
\\le
O(L^{\\max(2,k-1)}).
\\]

---

## 13. Candidate conclusion

Within the frozen scope, the manuscript now contains explicit bridges for:

1. residual-small \\(\\Rightarrow\\) BK residual-finite universe;
2. polynomial construction of the low-projection shell;
3. separation of BMS operational representations from the BK signature potential;
4. old-skeleton cross-fibre affine avoidance, including the coefficient modulus and liftable submodule;
5. quotient-changing one-original-bundle normalization;
6. runtime measured from original generator-input length \\(L\\).

No theorem-killing counterexample was found in the first hostile standalone replay.

**Candidate conclusion only:**
\\[
\\text{generators}
\\longrightarrow_P
\\text{compact representation}
\\longrightarrow_P
\\text{short pp-definition}.
\\]

If a second independent cold replay of v0.2 verifies every lemma and the prior-art review finds no earlier result, this would give a scoped positive result candidate for BK Question 30 in the fixed finite residually-small cube-term regime.

---

## 14. Scientific ceiling and seal conditions

- THEOREM_SEAL = HOLD.
- QUESTION_30_SOLVED = NOT CLAIMED.
- D1 = EMPTY.
- P_VS_NP = OPEN.

Seal requires:
1. second cold replay using only v0.2 and cited sources;
2. line-by-line verification of Lemmas B and C;
3. independent check of the low-shell compact construction;
4. independent check of the residual-small/residual-finite bridge;
5. prior-art/novelty review through the current literature;
6. one final dependency-ledger closure with no unproved NOVEL node.
