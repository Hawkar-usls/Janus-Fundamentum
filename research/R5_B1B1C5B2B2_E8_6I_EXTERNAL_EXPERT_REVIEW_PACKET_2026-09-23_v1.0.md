# External Expert Review Packet — R5 E8 6I

## Purpose

This packet is for an independent researcher in universal algebra / algebraic CSPs. The candidate result is intentionally **not** presented as a proved theorem yet.

### Candidate claim

For a fixed finite family K of finite similar algebras with a common k-cube/k-edge term, assuming V(K) is residually small, there is a candidate deterministic polynomial-time procedure which, from arbitrary generators of an invariant relation R over factors in HS(K), constructs a polynomial-size pp-definition of R over one fixed finite basis. The candidate output bound is O(n^max(2,k-1)).

This is a scoped candidate related to Bulín–Kompatscher Question 30 (Section 6.3), not a claim about Question 30 (Section 6.3) in full generality.

## Files to review

1. `research/R5_B1B1C5B2B2_E8_6I_RESIDUALLY_SMALL_CUBE_EFFECTIVE_PP_NORMALIZATION_MANUSCRIPT_2026-09-23_v1.0-rc1.md`
2. `registry/JANUS_P_VS_NP_R5_E8_6I_FINAL_SOURCE_BINDING_CLOSURE_2026-09-23_v1.0-rc1.json`
3. `research/R5_B1B1C5B2B2_E8_6I_RESIDUALLY_SMALL_CUBE_EFFECTIVE_PP_NORMALIZATION_PRIOR_ART_NOVELTY_AUDIT_2026-09-23_v1.0.md`

## Primary sources

- Berman, Idziak, Marković, McKenzie, Valeriote, Willard — *Varieties with few subalgebras of powers*.
- Bulatov, Mayr, Szendrei — *The Subpower Membership Problem for Finite Algebras with Cube Terms*, LMCS 15(1:11), 2019.
- Bulín, Kompatscher — *Polynomial definability in constraint languages with few subpowers*, arXiv:2305.01984v3, 27 Jan 2026.
- Kalampakas — *Automatic constraints with few subpowers and graphoid recognition*, arXiv:2609.07891v1, for prior-art comparison only.

## Highest-risk novel points

### A. Cross-fibre affine avoidance

Please verify independently that BMS Theorem 2.2 plus Claims 6.6–6.7 justify the induced homomorphisms between old-skeleton source and target rho-fibre quotients, and that the constant coefficient family Lambda exactly characterizes unsafe one-generator extensions.

Questions:
- Does every relevant subgroup contribution after adjoining t reduce to one additive combination in Lambda?
- Is the liftable restriction invariant under the relevant unary polynomial maps?
- Is the coefficient modulus/exponent bound genuinely fixed by K?

### B. Strict existential old-block localization

Please verify independently the SAFEEXT reduction:
- post-extension coherence refines old coherence;
- Theorem 5.3 localizes a surviving target failure to U contained in an old block E;
- T_E=S[theta^E] is exactly the liftable full inverse image used as a strictness detector;
- if S<T_E, a tuple in T_E\S is immediately globally safe;
- if S=T_E, strictness of a global witness is visible on E;
- Algorithm 7 supplies exactly the d-coherent HSK input required by the local B/C solver;
- a strict liftable local witness completes to a strict global safe witness.

### C. Constructive critical decomposition

Please verify that repeated SAFEEXT maximalization plus the dummy-coordinate test constructs a critical separator and that the BK signature argument is used only as a mathematical polynomial potential/count, not as an algorithmically assumed representation conversion.

### D. Effective BK recursion

Please verify that mapping compact generators through the BK quotient homomorphism really supplies generators of R', and that BMS SMP/CompactRep over HS(K) is enough to recompact at every arity-reduction step.

## Requested reviewer verdict

Please return one of:

- **VALID AS STATED IN THE FROZEN SCOPE**
- **VALID AFTER EXPLICIT REPAIR** — identify exact statement/line
- **GAP / COUNTEREXAMPLE** — give smallest exact failure
- **PRIOR ART COLLISION** — identify exact theorem and scope

Please separately classify:
1. mathematical correctness,
2. runtime polynomiality in original generator-input length,
3. output-size bound,
4. novelty wording.

## Scientific firewall

This work does not imply a polynomial algorithm for arbitrary signed 3-SAT and does not resolve P vs NP.

D1 = EMPTY.  
P_VS_NP = OPEN.
