# R50G25BA3 — FROZEN-POSITIVE-BRIDGE IMPOSSIBILITY + MINIMAL TWO-POLARITY COMPLETION — PREREG v1.0

Status: FROZEN BEFORE IMPLEMENTATION/TESTING
Parent: sealed BA2-A PERSISTENT_ONE_POLARITY_CHANNEL_CERTIFIED
Parent source head: 8caebdf7e157de3b610242e285afff412aaceb7d

## Scope / nonclaims
BA3 asks only whether the exact one-Boolean-endpoint architecture can (i) prove FORCE_0 impossible through the unchanged positive bridge for every endpoint relation C, and then (ii) obtain a minimal exact persistent two-polarity Boolean channel by completing both the BA2 block carrier and bridge. It does NOT study arbitrary-CNF coverage, SAT in P, or P=NP. AZ, BA0, BA1, BA2 are immutable ancestors.

## Frozen variables / orientation
q := x2 (incoming endpoint of real frozen U)
p := x30 (outgoing endpoint of real frozen U)
r := x32 (next shifted x2)
Rows=input, columns=output, values ordered 0,1.
Expected frozen U endpoint relation to be independently reconstructed before promotion:
J(q,p)=[[1,1],[1,1]].
Frozen bridge clause is (p OR r), literals (30,32), expected relation:
B(p,r)=[[0,1],[1,1]].
BA2 carrier clause is (-q OR -p), literals (-2,-30), expected relation:
C_STAR=[[1,1],[1,0]].
F1 if actual frozen bridge/source semantics disagrees with these orientations.

## Boolean relation composition
(R o S)(x,z) := OR_y [R(x,y) AND S(y,z)]. This is Boolean relation composition, not arithmetic matrix multiplication.

## BA3-1 frozen-positive-bridge impossibility lemma
Before constructing the candidate, audit all 16 Boolean relations C(q,p). For T=C o B, test/prove that no source row of T can equal exactly {r=0}. The structural reason to prove is that row_0(B)={1}, row_1(B)={0,1}; hence any existential union over permitted p is EMPTY, {1}, or {0,1}, never {0}. If confirmed seal only the restricted theorem FROZEN_POSITIVE_BRIDGE_FORCE0_IMPOSSIBILITY for this exact one-Boolean-endpoint model. Consequence: changing only C(q,p) cannot yield exact persistent two-polarity transport while B remains unchanged.

## BA3-2 complete BA2 block carrier
Candidate BA3-only block clause: (q OR p), literals (2,30), added to existing BA2 clause (-2,-30). Expected combined block endpoint relation:
C_X=[[0,1],[1,0]] (q XOR p).
Independently reconstruct the real U endpoint counts. Expected ancestor counts: 00:8, 01:19, 10:12, 11:21. Verify actual U plus both endpoint clauses leaves real internal witnesses exactly for endpoint pairs 01 and 10. No matrix-only promotion.

## BA3-3 complete bridge
Candidate BA3-only bridge clause: (-p OR -r), literals (-30,-32), added to frozen bridge (30,32). Expected exact bridge relation:
B_X=[[0,1],[1,0]] (p XOR r). Independently verify by truth-table evaluation of the real CNF clauses.

## BA3-4 two flips make identity
Compute T_2P=C_X o B_X. Preregistered expectation:
I=[[1,0],[0,1]], so T_2P=I and T_2P^k=I for every integer k>=1. Required meaning: FORCE_0 -> FORCE_0 and FORCE_1 -> FORCE_1 at observable block boundaries. F4/F5 on mismatch or eventual merge.

## BA3-5 residual equivalence / information
Classify TOP, FORCE_0, FORCE_1, BOTTOM by allowed continuation SAT behaviour. For the directional carrier require FORCE_0 not~ FORCE_1 after arbitrary chain length. If exact values persist, record N_direction=2 and I_direction=log2(2)=1 full Boolean bit. Do not conflate with BA2 one-polarity persistence.

## BA3-6 source-preimage / DP hardening
Require separate statuses ALGEBRA_PASS, CNF_REALIZATION_PASS, SOURCE_PREIMAGE_PASS, DP_INTERACTION_PASS, PERSISTENCE_PASS for C_X and B_X. Provide actual U internal witnesses for 01 and 10. Independently eliminate/project the materialized U+carrier CNF back to the (q,p) endpoint relation and require exactly C_X. Independently recover B_X from the two real bridge clauses. Matrices/hashes are not substitutes for replayable source content.

## BA3-7 constructive return
For every SAT generalized carrier instance used by the theorem: solver/model -> reverse reconstruction -> model of original generalized CNF -> independent VERIFY=PASS. Reconstruction must preserve the input polarity: FORCE_0 returns boundary value 0, FORCE_1 returns boundary value 1 wherever the carrier theorem states it persists. Neither may silently become TOP.

## BA3-8 uniform generic chain
Two-polarity mode for block j uses exactly:
(-q_j OR -p_j) [BA2]
( q_j OR  p_j) [BA3-only]
with q_j=2+30j, p_j=30+30j.
For bridge j use exactly:
( p_j OR  q_{j+1}) [frozen]
(-p_j OR -q_{j+1}) [BA3-only].
No g-specific/hindsight choices. Prove effective q_j-to-q_{j+1} relation is identity and by induction q_0=q_1=...=q_{g-1} in two-polarity carrier semantics.

## BA3-9 hierarchy compatibility
NEUTRAL mode must be exactly sealed F_g.
ONE_POLARITY mode must be exactly sealed BA2 carrier.
TWO_POLARITY mode adds only the preregistered BA3-only clauses.
Removing BA3-only clauses must recover BA2 exactly; removing all carrier clauses must recover AZ F_g exactly. No ancestor theorem is rewritten.

## BA3-10 complexity quantities
Independently derive C_g,L_g,V_g, certificate records/bits, construction time, verification time, reconstruction time, and separator/primal width. Sanity candidate relative to frozen F_g: two-polarity mode adds 2g block-correlation binary clauses plus g-1 complementary bridge clauses = 3g-1 binary clauses. The second q-p clause reuses the BA2 primal edge; bridge complement reuses the frozen bridge primal edge. This does NOT authorize inheriting w<=13; independently replay/verify width and derive a generic bound.

## BA3-11 minimality beyond BA2
Under the declared clause grammar, perform finite exact relation/clause-cost audit. Require: (1) changing only C is impossible if BA3-1 holds; (2) at least one additional bridge restriction is necessary; (3) triangular BA2 C_STAR needs at least one additional endpoint restriction for both rows to become singleton; (4) compare all cheaper/equal-cost candidates. Proposed added pair is (q OR p) and (-p OR -r). If a cheaper construction exists, F11 and freeze the cheaper result instead of preferring XOR/XOR post hoc.

## Falsifiers
F1 frozen bridge/source matrix orientation differs.
F2 C_X not realizable in actual U.
F3 B_X not exact XOR.
F4 C_X o B_X != I.
F5 FORCE_0/FORCE_1 merge after finite chain length.
F6 source-preimage or DP semantics differ from relation algebra.
F7 reconstruction loses either polarity.
F8 neutral/BA2 hierarchy recovery fails.
F9 generic construction requires hindsight or g-specific choice.
F10 size/time/width becomes super-polynomial.
F11 a cheaper declared-grammar construction exists, invalidating minimality.

## Allowed outcome
Strongest permitted success label:
BA3-A PERSISTENT_TWO_POLARITY_BOOLEAN_CHANNEL_CERTIFIED
meaning only one full Boolean boundary state is transported through arbitrary length of this exact generalized chain with proof-carrying reconstruction and polynomial accounting.
On BA3-A STOP. Do not start arbitrary-CNF coverage or k-bit scaling automatically.

Firewalls: P_VS_NP=OPEN; SAT_IN_P=NOT_PROVED; TRUMP_finished=false.
