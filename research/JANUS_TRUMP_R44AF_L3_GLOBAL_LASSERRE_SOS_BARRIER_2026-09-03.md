# JANUS TRUMP R44AF — global Lasserre / Sum-of-Squares barrier

## Fixed global model

R44AF deliberately leaves the bounded-local world. The fixed route is:

`STANDARD_LASSERRE_SUM_OF_SQUARES_LEVEL_ESCALATION`.

The machine encodes the Boolean CSP in the standard Lasserre/SoS hierarchy and increases the relaxation level until exact negative authority is obtained.

This is a genuinely global relaxation architecture: the state consists of global moment/consistency data, not just small-clause propagation.

## Published lower bound

Grant Schoenebeck, *Linear Level Lasserre Lower Bounds for Certain k-CSPs*, FOCS 2008, pp. 593–602, DOI `10.1109/FOCS.2008.74`.

For `k >= 3`, the paper proves that even `Omega(n)` levels of the Lasserre hierarchy cannot disprove random k-CSP instances for predicates implied by k-XOR, explicitly including k-SAT and k-XOR.

The same paper states that level `r` of Lasserre for a k-CSP with polynomially many constraints can be optimized in time `n^{O(r)}`.

Therefore, on the covered unsatisfiable random 3-SAT family, an exact standard Lasserre route must cross a linear-order level threshold before it can refute satisfiability. At such a level the standard generic cost is `n^{Omega(n)}`, not polynomial.

## TRUMP consequence

`GLOBAL_RELAXATION != GLOBAL_EXACT_DECISION`.

`RELAXATION_STILL_FEASIBLE != SAT`.

The architecture is global, but exactness debt appears as required hierarchy degree/rank rather than as bounded-local blindness.

Thus the fixed standard level-escalation route cannot discharge the Legend polynomial-runtime requirement.

## Accounting firewall

It is forbidden to hide level escalation inside one macrostep:

`ONE_MACROSTEP_CONTAINING_LINEAR_LEVEL_SOS != POLYNOMIAL_WORK`.

L3 charges the full SDP/hierarchy work.

## Scope

R44AF is not a lower bound for every SDP algorithm, every global algorithm, or every 3-CNF instance. It does not imply `P != NP`.

It blocks one precisely fixed, strong global relaxation architecture as an easier universal path.

The next admissible transition model must therefore be global and exact in a sense not reducible to generic Cook–Reckhow proof search, bounded-local propagation, full-function compilation, or standard Lasserre/SoS feasibility escalation.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
