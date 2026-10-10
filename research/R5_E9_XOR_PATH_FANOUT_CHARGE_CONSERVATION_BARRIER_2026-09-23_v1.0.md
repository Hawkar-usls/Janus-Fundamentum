# R5 E9 — XOR-Path / Fanout Charge Conservation Barrier

Date: 2026-09-23

Authority: DERIVED_EXACT_CONSERVATION_LAW__LOCAL_COHERENCE_SUBSTITUTION_ONLY__NO_D1_PROMOTION

Parent: R5_E9_THREE_CONNECTED_OVERLAY_PIVOT_GATE_V1

Checker: research/tools/r5_e9_xor_path_fanout_charge_checker.py

## 1. Exact local pivot

For one original variable with d literal occurrences, the two-path normal form places its occurrence copies on one XOR2 path. Every current coherence supernode carries at least one clause attachment.

Contract one path edge using v = u XOR delta, substitute v everywhere, remove that XOR edge, and reroute all clause attachments of v to u (with the induced sign change when delta=1). This is exact and reconstructive.

## 2. Joint charge

Let E_x be the number of remaining XOR path edges. Let F_x be the sum, over current supernodes s, of attachments(s)-1. Define Phi_x = E_x + F_x.

If the current path has k supernodes with positive attachment counts a_1,...,a_k, then E_x=k-1 and F_x=(a_1+...+a_k)-k. Their total attachment count is the invariant original occurrence number d. Hence Phi_x=(k-1)+(d-k)=d-1.

## 3. One-step conservation

Contract adjacent supernodes carrying p,q>=1 attachments. Then Delta E_x=-1. The fanout terms (p-1)+(q-1) are replaced by p+q-1, so Delta F_x=+1. Therefore Delta Phi_x=0.

This holds for every exact adjacent XOR-path substitution contraction.

## 4. Endpoints

Initially E_x=d-1, F_x=0, Phi_x=d-1. After fully collapsing the occurrence path to one representative bit, E_x=0, F_x=d-1, Phi_x=d-1.

Thus local coherence contraction does not destroy the cross-layer burden. It converts coherence length into nonlinear clause fanout. The fully collapsed endpoint is exactly the ordinary high-fanout original-variable representation.

## 5. Exhaustive sanity replay

Every reachable path state is a composition of d into positive attachment counts. The checker enumerates all such states for d<=10 and every adjacent contraction.

Result: all states PASS; adjacent contractions checked = 4097; Phi_x invariant.

The finite checker is only a replay. The arbitrary-d theorem is the algebraic identity above.

## 6. Consequence

The operation 'contract an XOR coherence edge by exact substitution and merely reroute its nonlinear attachments' cannot be the missing strict-progress pivot.

For the global sum Phi=sum_x Phi_x, ordinary path substitution is exactly invariant. Therefore it cannot provide a strictly decreasing joint potential.

## 7. Surviving operation class

This does not block a nonlocal contraction that simultaneously simplifies both layers, for example one that removes multiple independent clause attachments, identifies a semantic quotient of several clause gadgets, performs a nonlocal algebraic cancellation, or replaces a whole region by a strictly smaller exact boundary relation.

The surviving pivot must satisfy Delta(coherence burden)+Delta(nonlinear fanout burden)<0, not merely move one unit from one term to the other.

## 8. New micro-gate

R5_E9_NONLOCAL_OVERLAY_CHARGE_DISSIPATION_GATE_V1:

Find an exact polynomial contraction of a rigid torso region R such that SAT is preserved exactly, witnesses lift in polynomial time, total representation size stays polynomial, at least one unit of the conserved local charge is genuinely removed, the decrease is certified without a SAT oracle, and repeated application reaches a tractable normal form after polynomially many steps.

## 9. Ceiling

LOCAL XOR-PATH SUBSTITUTION = PASS EXACT
STRICT JOINT PROGRESS FROM THAT SUBSTITUTION = FALSIFIED BY CONSERVATION
NONLOCAL CHARGE-DISSIPATING QUOTIENT = OPEN <<< ACTIVE GAP
D1 = EMPTY
P_VS_NP = OPEN
