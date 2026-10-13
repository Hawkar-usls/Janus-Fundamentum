# R5 — Edge-dependent GL2 matchgate parity impossibility for ALL native SCL Holant networks
Date: 2026-10-12, Europe/Kyiv.
PR #516 (DRAFT). Main unchanged.
Parent general global-basis result:
`research/R5_ALL_SCL_HOLANT_UNIFORM_MATCHGATE_PARITY_NOGO_2026-10-12.md`.

## Ultimate scientific contract

Construct one deterministic uniform n^C bit-time
`SolveLinearCubicXSAT(F)` returning original SAT witness or
original-source-certified UNSAT for EVERY legal source.
Not constructed; P vs NP OPEN. THIS RESULT IS A REJECTION
of a PARTICULAR ALGEBRAIC ROUTE, not fulfillment of the goal.

## 1. Statement of stronger theorem

Let F be ANY square+cubic+linear positive Exact-One source
with exactly three ones in every row and column. Its original
Tanner network has row tensor
`W=|001>+|010>+|100>`, i.e. `ExactOne3`,
and variable tensor
`G=|000>+|111>`, i.e. `Equality3`.

Give EVERY original Tanner incidence wire e its own ARBITRARY
invertible complex 2x2 basis B_e, independently from all
other Tanner wires. Transform the clause side of that wire by
B_e and the variable side by B_e^{-T}, so that the
original Boolean pairing / Holant partition sum is preserved.

**THEOREM: It is impossible for all transformed original
row tensors and all transformed original column tensors
to be ordinary matchgate signatures.** More strongly,
one cannot even make all of them pure even/odd local
Hamming-weight parity, which is a NECESSARY matchgate property.

The result is independent of source size, topology,
symmetry, connectedness, treewidth and planarity.

## 2. Pure-algebra proof for every complex gauge

Let Z=diag(1,-1), and for each incidence wire e define
`K_e=B_e^{-1} Z B_e`. Since B_e is invertible,
K_e is invertible, tr(K_e)=0, det(K_e)=-1, K_e^2=I.

A tensor has pure even or odd parity iff it is an
eigenvector of `Z^{tensor3}` with eigenvalue +1 or -1.
Pulling this condition back through the edgewise gauge,
we get at every original ExactOne clause row r

```
 (K_{e1} tensor K_{e2} tensor K_{e3}) W = ± W
```

and at every original variable column v, because the
opposite side has B_e^{-T} rather than B_e,

```
 (K_{e1}^T tensor K_{e2}^T tensor K_{e3}^T) G = ± G.
```

**LEMMA 1 (GHZ local-product stabilizer).**
If invertible A,B,C satisfy
`(A tensor B tensor C)G = lambda G`, lambda!=0,
then A,B,C must be ALL diagonal or ALL antidiagonal.

Proof. Flatten the tensor into first leg vs last two legs.
The two-dimensional right support is exactly
S=span{|00>,|11>}. Since A is invertible and the target
tensor is the same nonzero GHZ, B tensor C preserves S.
The only nonzero decomposable (rank-one) vectors
inside S are multiples of |00> or |11>:
a product (alpha|0>+beta|1>) tensor
(gamma|0>+delta|1>) in S requires
alpha*delta=beta*gamma=0; if nonzero it has precisely
one allowed coordinate direction. Therefore B tensor C
sends |00> and |11> into two distinct directions in
{|00>,|11>}, making B and C diagonal or antidiagonal
together. Repeating across the other two flattenings
forces A to have the same type. QED.

Applying this lemma at every original SCL VARIABLE gives
that every K_e^T, hence every K_e, is monomial: it is
diagonal or antidiagonal (three around the same variable
share the same type).

**LEMMA 2 (odd-cardinality W support).**
At a row the product of three invertible monomial K_e
permutes the 3-bit coordinates by a common XOR
translation mask m∈{0,1}^3, accompanied by nonzero
component scalars. W has support
S={001,010,100}, of cardinality exactly THREE.
If m!=000, the translation t->t xor m is a
fixed-point-free involution and EVERY finite invariant
set must have even cardinality. Therefore S cannot
be invariant, so the row-parity eigenvalue condition
forces m=000. ALL K_e at every row are diagonal.
Since every wire is incident to a row, ALL K_e
throughout the native Tanner network are diagonal.

**LEMMA 3 (diagonal involution contradiction).**
Every diagonal traceless involution with det=-1
is K_e=+Z or K_e=-Z. At any variable (degree THREE),
`(K_e1^T tensor K_e2^T tensor K_e3^T)G`
equals a nonzero scalar multiple of
`|000>-|111>`, which is NOT proportional
to `G=|000>+|111>` over characteristic zero.
Contradiction to the required variable-parity
eigenvector equation. QED.

This is an exact symbolic proof, NOT a failed
sample search generalized to all B_e.

## 3. Independently executable checks

New executable:
`experiments/r5_universal_holant_all_local_gl2_matchgate_nogo.py`

New GitHub workflow:
`.github/workflows/r5-holant-edge-local-matchgate-nogo.yml`

Canonical original-source CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38297618298
SUCCESS at `5993c229d05a326cdcf25986a5719de6a9966f4a`.

- Independently evaluates heterogeneous B_1,B_2,B_3
  ternary parity for W and inverse-dual GHZ, for 512
  distinct triples from 8 rational GL2 matrices.
- Checks that any GHZ parity-pure triple implies
  monomial local K_e of common diagonal/antidiagonal type.
- Checks that any parity-pure W triple with monomial
  local K_e has every K_e diagonal.
- Enumerates all 8 XOR flip masks to confirm that
  the size-three support has no nonzero translation
  stabilizer.
- Tests all 8 sign triples of diagonal traceless
  involutions: W eigen, GHZ NOT eigen.
- Rebuilds and authenticates every original cubic SCL
  source in Fano7, K4/SCL18, K3,3/SCL27,
  Petersen/SCL45, and rejects uniform and several
  nonuniform sampled edge-basis proposals.
- The mathematical no-go is independent of the samples.

Unsuccessful initial workflow
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38297568020
remains immutable and visible: a test dictionary
used an undefined `e` instead of `(row_index,var_index)`
for a heterogeneous gauge key. This was a test-harness
NameError after the core 512 local checks, NOT a false
scientific conclusion. Corrected CI succeeded without
modifying the theorem.

Prior exact gauge-invariance and single global GL2:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38297126176
SUCCESS, 1488 exact inverse-dual local pairings.

## 4. Literature and authority

Necessary matchgate parity and matchgate identities are
standard; not claimed as a novel discovery:
- J.-Y. Cai, P. Lu, M. Xia, Holographic Algorithms with
  Matchgates Capture Precisely Tractable Planar #CSP,
  SIAM J. Comput. 46 (2017),
  https://doi.org/10.1137/16M1073984
- The Complexity of Planar Boolean #CSP with Complex
  Weights, JCSS (2019), matchgate parity section:
  https://doi.org/10.1016/j.jcss.2019.07.005

Independent published counting hardness:
J.-Y. Cai and A. Z. Fan (2023), Planar 3-way Edge
Perfect Matching Leads to A Holant Dichotomy,
https://arxiv.org/abs/2303.16705.
Cubic Planar X3C / cubic monotone positive 1-in-3
SAT COUNTING is #P-hard even planar. Counting
hardness is NOT itself a proof that the decision
problem needs superpolynomial time.

The combination of the edge-dependent parity-stabilizer
lemmas above is a specific, source-structural JANUS
no-go for this exact native tensor architecture.

## 5. Exact meaning of the new frontier

The following route is CLOSED:

```
original SCL Tanner network
    -> independently invertible 2x2 basis B_e
       on EACH existing incidence wire
    -> all original ExactOne3 and Equality3
       nodes become matchgate signatures
    -> invoke a single standard FKT/Pfaffian
       perfect-matching contraction
```

No scheme in this precisely defined family works,
even before checking Pfaffian planarity/genus or
the full matchgate identities.

The following alternatives are still OPEN:
- replacing original W/GHZ nodes by polynomially
  sized GADGETS or grouping many original nodes
  into new tensors before attempting Pfaffian;
- noninvertible or higher-domain wire algebra;
- nonmatchgate symbolic compression with polynomial
  identity/nonzero testing;
- generalized contraction circuits and
  source-preserving SAT witness extraction;
- completely different universal polynomial algorithms.

Proving the local no-go does NOT prove P != NP;
it merely prevents pursuing this specific dead end.

```
ALL_SCL_HOLANT_EXACT_REPRESENTATION=PROVED
UNIFORM_GL2_MATCHGATE_ANSATZ=REFUTED
ALL_EDGE_LOCAL_GL2_NATIVE_MATCHGATE_ANSATZ=REFUTED
ALL_EDGE_LOCAL_PARITY_STABILIZER_PROOF=PROVED
HIGHER_ARITY_GADGET_AND_NONMATCHGATE_COMPRESSION=OPEN
GLOBAL_UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED
P_VS_NP=OPEN
```
