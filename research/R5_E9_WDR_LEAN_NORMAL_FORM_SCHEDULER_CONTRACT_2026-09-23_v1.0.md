# R5 E9 — WDR-Lean Normal Form Scheduler Contract

Date: 2026-09-23

Authority: JANUS_DERIVED_GOVERNANCE_CONTRACT__NO_UNIQUENESS_OR_CONFLUENCE_CLAIM__NO_D1_PROMOTION

Parent: R5_E9_POLY_SYNTHESIZABLE_RANKED_WITNESS_TRANSFORMER_GATE_V1

## 1. Terminology correction

Do not yet claim a unique WDR-lean kernel. Known SAT preprocessing rules can be order-sensitive.
Until confluence is proved, the authoritative object is:

WDR_NORMAL_FORM UNDER A FROZEN DETERMINISTIC SCHEDULER.

Same input + implementation version + scheduler must be replayable; no theorem says all schedules yield the same residual CNF.

## 2. Two rule classes

Class R — reducing repair rules.
Each accepted step returns (F', reconstruction_record, certificate), preserves SAT exactly, has polynomial synthesis/verification/reconstruction, and strictly decreases the frozen reduction potential.

Examples/donors: forced assignments, pure/autarky deletion, matching/linear autarkies, blocked-clause elimination, no-growth variable elimination, exact equivalence substitution, and certified witness-dominance contractions that immediately fix at least one Boolean dimension.

Class S — strengthening repair rules.
These may add a satisfiability-preserving constraint using ranked repair, substitution redundancy, dominance, or another structural witness.

Class S is NOT allowed to saturate freely.
Every Class-S application must be paired with a polynomially bounded macro-step proving that it enables immediate Boolean-dimension elimination, strict decrease of a declared structural budget, or entry into an already proved polynomial carrier.

This prevents pseudo-progress by accumulating redundant constraints.

## 3. Potentials

For Class R use the lexicographic potential:

Phi_R(F) = (# live Boolean variables, # clauses, total literal occurrences).

After deterministic cleanup every accepted Class-R step must strictly decrease this tuple.

For a Class-S macro-step use:

Phi_S = (live Boolean dimensions, bounded structural budget declared by the macro-rule).

The macro-rule must prove strict decrease before admission. Number of discovered certificates is never a progress measure.

## 4. Reconstruction-log discipline

Every accepted transformation appends one typed inverse record to a stack. Reconstruction runs in reverse order.
Each record must be sufficient to lift any post-state model to a valid pre-state model in polynomial time.

This is mandatory for compositions such as BCE plus variable elimination: individual soundness is not enough if inverse repair steps are replayed in the wrong order.

## 5. Frozen scheduler v1

Priority rounds:
R0 forced assignments / tautology / duplicate cleanup
R1 exact equivalence substitution
R2 matching/linear autarky modules
R3 blocked-clause elimination
R4 no-growth variable elimination
R5 signed structural dominance contractions
R6 restricted ranked/SR macro-rules WITH immediate certified dimension drop
R7 tractable connected-component extraction

After any successful rule, restart at R0.
Tie-breaking is lexical over normalized variable/clause identifiers.
No confluence theorem is claimed.

## 6. Stress protocol

For each frozen family record input size, residual variables/clauses/literals, rule counts, certificate bytes, reconstruction-log bytes, runtime, terminal-carrier status, and survivor motif statistics.

Primary families: Tseitin expanders; pigeonhole principles; DDD linear 4-regular NAE-3SAT; Krom+XOR3 universalizing gadgets; random 3SAT near threshold; JANUS equality-channel controls.

The scientific output is the residual motif after the full polynomial repair closure, not merely percentage reduction.

## 7. Prior-art firewalls

BCE is satisfiability preserving and has model repair by flipping a blocking literal when needed.
Buss–Thapen formalize propagation/substitution redundancy as equisatisfiable structural-witness rules; with new variables the full systems reach Extended Resolution.
Kołodziejczyk–Thapen prove the linear dominance system equivalent to G1.
Szeider shows several natural CNF homomorphism proof systems polynomially equivalent to tree-like Resolution.

Therefore none of these rule families is promoted as a universal P=NP currency by itself.

## 8. Active gate

R5_E9_WDR_NORMAL_FORM_SURVIVOR_MOTIF_GATE_V1

Run the frozen scheduler to fixpoint on the stress ladder. Identify the first structural motif shared by surviving hard residuals but absent from solved positive controls. Only that motif may seed the next transformer/rank rule.

## 9. Ceiling

WDR UNIQUE KERNEL = NOT CLAIMED
DETERMINISTIC WDR NORMAL FORM = DEFINED
FREE STRENGTHENING SATURATION = FORBIDDEN
REVERSE RECONSTRUCTION LOG = MANDATORY
NEXT OBJECT = SURVIVOR MOTIF AFTER POLY REPAIR CLOSURE
D1 = EMPTY
P_VS_NP = OPEN
