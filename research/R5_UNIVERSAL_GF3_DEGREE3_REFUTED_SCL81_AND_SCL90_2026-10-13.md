# R5 DECISIVE VERDICT — universal GF3 Boolean degree-three SCL refutation theorem DISPROVED

Checkpoint date: 2026-10-13 (Europe/Kyiv). GitHub PR #516 research branch DRAFT. Main untouched.

## The formerly open all-source statement is FALSE

Proposed but unproved statement:

For every original square/cubic/linear positive 1-in-3 SAT SCL source F, if F is UNSAT then the constant 1 belongs to the multilinear GF3 span of all original clause polynomials E_i(x)=sum_(v in C_i)x_v-1 multiplied by squarefree monomials of degree at most 2, modulo Boolean relations x_j²=x_j.

This is the specific native polynomial-calculus/Nullstellensatz degree-three space V3(F).

**PROVED NEGATIVE:** There exist TWO different explicitly source-audited UNSAT legal SCL sources F81, F90 for which 1 NOT IN V3(F). Hence this proposed universal degree-three proof bound is MATHEMATICALLY FALSE, unconditionally and independently of P versus NP.

This does NOT prove P!=NP, does NOT refute higher-degree or non-polynomial-calculus algorithms, and does NOT give any universal polynomial-time SAT solver. P_VS_NP=OPEN.

## Counterexample 1 — smaller original SCL81, Petersen dot product

A deterministic edge-splicing of two native Petersen graphs gives a connected BRIDGELESS 18-vertex simple cubic graph G with 27 edges; make_scl(G) yields exactly 81 original positive Exact-One variables/clauses and independently validates every SCL cubicity/linearity promise.

Frozen 27-edge graph G:
((0,4),(0,5),(0,10),(1,2),(1,6),(1,14),
 (2,7),(2,12),(3,4),(3,8),(3,13),
 (4,9),(5,7),(5,8),(6,8),(6,9),(7,9),
 (10,11),(10,15),(11,12),(11,16),(12,17),
 (13,15),(13,16),(14,16),(14,17),(15,17)).

Independent ORIGINAL SCL UNSAT proof: exact-cover DFS produces an explicit DAG of 286 dead uncovered ORIGINAL clause masks; a separate checker walks every original clause branch and verifies the DAG is complete and terminal0 is NOT among its allowed states. Independent graph edge-colouring solver also certifies no valid 3-colouring.

Independent degree-three dual proof: exact GF3 rowspace completed after 502,034,568 elimination updates. Number of multilinear monomials of degree<=3 for n81 is 1+81+C(81,2)+C(81,3)=88,642. Exact source span rank is 88,512. A full dual pseudo-moment functional y with 41,587 nonzero GF3 coordinates satisfies y(1)=1 and annihilates ALL original E_i*x_M, |M|<=2; independent source-level checker replays all 81*(1+81+C(81,2)) = 269,082 source generators.

Thus UNSAT original native SCL81 exists without any degree-three GF3 Boolean refutation.

Authoritative complete CI: https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38331729938 (SUCCESS), source commit 86dae308807d39a30c7e60b283fd6a61a3ba87ea.
Code: experiments/r5_universal_petersen_dot_snark_gf3_degree3_dual.py.

Prior CI #38331583210 hit its initial 100M-operation safety guard (UNKNOWN_RESOURCE_LIMIT, rank88385) but source UNSAT was already proven by DAG286. Enlarged exact guard to650M yielded the complete dual success. UNKNOWN was NEVER treated as negative proof.

## Counterexample 2 — original flower snark J5 native SCL90, FROZEN standalone certificate

Direct native cubic graph 3-edge colouring reduction of Isaacs J5 (20 vertices, 30 edges) yields 90 original positive exact-one variables and rows.

Independent ORIGINAL SCL UNSAT certificate: authenticated 27-state flower transfer theorem, 8-state quotient obstruction and separate exact edge colouring DFS.

Full original GF3 V3 Gaussian:
- ambient monomial dimension 121,576;
- complete source rowspace rank 121,275;
- 368,640 original clause×multiplier generators;
- 54,735 nonzero dual moments y(1)=1, annihilating ALL source generators;
- 464,719,115 exact GF3 sparse cell updates.

CI https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38331387342 (SUCCESS).

Separate symmetry compressed source-correct implementation uses the TRUE TWISTED petal automorphism C10×C2 of order20, invertible in characteristic3; by averaging, a source dual exists iff an invariant dual exists. It has just 6656 monomial orbits, 10 clause orbits, rank6639. The independently produced dual has 46266 nonzero full moment coordinates, and independently annihilates all 368640 original generators.

CI https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38332355302 (SUCCESS).

An actual compressed witness vector is committed, not simply recomputed:
- file: research/certificates/R5_J5_SCL90_GF3_V3_ORBIT_DUAL_2026-10-13.b64z
- 1452 characters of base64+zlib, decompressed into 6656 native GF3 orbit bytes
- SHA256 of decompressed witness: f2944e1a4fb474ebaac3aa2fcc19689139d1bee256f3f01af1f4ecebfd7c1edd

A completely STANDALONE original-source verifier, with NO Gaussian algorithm, reads this frozen witness, reproduces native SCL90 and the authenticated 27-state UNSAT proof, checks SHA256, regenerates its exact source automorphism orbits, expands 121576 monomials and checks all 368640 original generator identities y(E_i*x_M)=0 and y(1)=1. Forged witness rejected.

Standalone CI https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38332775987 (SUCCESS).
Code: experiments/r5_j5_degree3_frozen_dual_standalone_source_verifier.py.

Scientific details and provenance for this independent J5 pair:
research/R5_J5_SCL90_UNSAT_GF3_DEGREE3_DUAL_COUNTEREXAMPLE_PROVED_2026-10-13.md.

## Exact elementary proof of failure

Both original sources are UNSAT and source SCL-legal. For either full degree-three dual y:

 y(1) = 1,
 y(multilinear(E_i*x_M)) = 0 for EVERY original clause i and |M|<=2.

Assume constant 1 were in V3, i.e. expressible as sum c_(i,M)*multilinear(E_i*x_M). Applying the linear functional y to both sides gives 1=0 in F3. Contradiction. Thus 1 NOT in V3 on both SCL81 and SCL90.

Therefore the exact earlier universal statement ALL_SCL_V3_COMPLETE is **REFUTED**, not merely UNKNOWN. Source minimal GF3 refutation degrees for F81 and F90 are each at least4. The exact minimum degree, and whether some OTHER global constant d works on all SCL, remain open.

## Implications for solver roadmap and non-overclaiming

The earlier conditional O(n^10) algorithm relying on universal V3 completeness has its required premise PROVED FALSE and must NOT be described as a universal solver.

A fixed degree d>3 would still imply a polynomial source solver IF universal completeness were proved; no such theorem currently exists. Existing known linear polynomial-calculus degree lower bounds for vertex colouring or Tseitin formula encodings cannot be imported without a rigorous degree-preserving legal native SCL reduction. A source reduction from graph cubic edge colouring is a decision equivalence, not automatically a source-verified algebraic degree-back-simulation.

The already proven constant G10/G11 original-SCL unary pin compiler, its polynomial source size n+21q and n+1 conditional source search-to-decision theorem are UNAFFECTED; they still depend on obtaining an actual universal exact unpinned zero test through a different proof.

Checkpoint gates:
- NATIVE_SCL81_PETERSEN_DOT_SOURCE_UNSAT = PROVED
- SCL81_GF3_V3_DUAL_41587 = INDEPENDENT_CI_SUCCESS
- NATIVE_SCL90_J5_SOURCE_UNSAT = PROVED
- SCL90_GF3_V3_FULL_DUAL_54735 = INDEPENDENT_CI_SUCCESS
- SCL90_GF3_V3_SYMMETRIC_DUAL_46266 = INDEPENDENT_CI_SUCCESS
- SCL90_FROZEN_BYTES_STANDALONE_PROOF = INDEPENDENT_CI_SUCCESS
- ALL_SCL_GF3_V3_UNSAT_COMPLETENESS = REFUTED
- MIN_DEGREE_FOR_BOTH_SOURCE_COUNTEREXAMPLES >= 4 = PROVED
- ALL_SCL_ANY_FIXED_DEGREE_SUFFICIENCY = OPEN
- ALL_SCL_UNIFORM_LOOPZERO_POLYNOMIAL = NOT_CONSTRUCTED
- SolveLinearCubicXSAT = NOT_CONSTRUCTED
- P_VS_NP = OPEN
