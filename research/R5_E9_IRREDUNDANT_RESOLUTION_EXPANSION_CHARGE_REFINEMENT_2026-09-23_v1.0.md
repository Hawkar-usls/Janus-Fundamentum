# R5 E9 — Irredundant Resolution-Expansion Charge Refinement

Date: 2026-09-23

Status: exact derived refinement of the WDR expansion-charge metric.

Scientific boundary: D1=EMPTY; P_VS_NP=OPEN.

## 1. Motivation

The raw charge chi_F(x)=|R_x|-|P_x|-|N_x| counts all distinct non-tautological x-resolvents.
This can overestimate the real CNF projection cost when some resolvents are subsumed by existing clauses or by other resolvents.

Define C_x = F \ (P_x union N_x).
Let Min(H) be H after tautology deletion, duplicate deletion, and clause subsumption to a minimal antichain.

Define the exact normalized DP image

DPmin_x(F) = Min(C_x union R_x).

and the normalized clause charge

chi_min_F(x) = |DPmin_x(F)| - |Min(F)|.

Whenever the WDR state itself is maintained subsumption-minimal, this is exactly the clause-count change of Davis-Putnam elimination followed by the same deterministic cleanup.

## 2. Polynomial computability

For one variable x, at most |P_x||N_x| candidate resolvents are generated.
Tautology, duplicate and pairwise subsumption checks are polynomial in the current explicit CNF size.

Therefore chi_min_F(x) is deterministically polynomial-time computable.

If chi_min_F(x) <= 0, exact variable elimination plus cleanup is an admissible no-growth WDR contraction with standard polynomial witness reconstruction.

## 3. Linear positive NAE3 theorem survives unchanged

For a variable x of hypergraph degree d in a linear 3-uniform positive NAE encoding:

- there are d positive x-clauses and d negative x-clauses;
- same-edge resolution pairs are tautological;
- every cross-edge pair yields a distinct 4-clause;
- no two such 4-clauses subsume one another because all have equal size and are distinct;
- no original NAE clause subsumes such a 4-resolvent: an original positive clause would require three positive literals while every resolvent has exactly two positive and two negative literals, and symmetrically for negative clauses.

Hence cleanup removes none of the d(d-1) cross-edge resolvents.

Therefore

chi_min_F(x) = d(d-1)-2d = d(d-3).

So the exact threshold remains:

d=3 -> chi_min=0
d=4 -> chi_min=4.

## 4. Consequence for the active gate

The expansion-charge repair target should use chi_min, not raw chi, whenever the implementation can afford full polynomial subsumption cleanup.

This prevents false positives caused only by syntactic redundancy.

The NAE4 hard-family remains genuinely positive-charge even under this stronger normalization.

## 5. Scheduler update

Recommended R0 cleanup now includes polynomial subsumption deletion in addition to tautology/duplicate cleanup.

Then R4 admission becomes:

perform exact DP elimination on x iff the fully normalized post-state does not increase the frozen reduction potential.

## 6. Ceiling

RAW CHARGE = useful diagnostic
IRREDUNDANT CHARGE chi_min = preferred exact CNF-growth metric
LINEAR NAE3 chi_min(d)=d(d-3) = PROVED
WDR EXPANSION-CHARGE REPAIR GATE = OPEN
D1 = EMPTY
P_VS_NP = OPEN
