# JANUS TRUMP R44AF — global Lasserre / Sum-of-Squares barrier

## Fixed global model

R44AF deliberately leaves the bounded-local world. The fixed route is:

`EXPLICIT_STANDARD_LASSERRE_SUM_OF_SQUARES_LEVEL_ESCALATION`.

The machine encodes the Boolean CSP in the standard explicit Lasserre/SoS hierarchy and increases the relaxation level until exact negative authority is obtained.

This is a genuinely global relaxation architecture: the state consists of global moment/consistency data, not just small-clause propagation.

## Published lower bound

Grant Schoenebeck, *Linear Level Lasserre Lower Bounds for Certain k-CSPs*, FOCS 2008, pp. 593–602, DOI `10.1109/FOCS.2008.74`.

For `k >= 3`, the paper proves that even `Omega(n)` levels of the Lasserre hierarchy cannot disprove random k-CSP instances for predicates implied by k-XOR, explicitly including k-SAT and k-XOR.

The paper also states an `n^{O(r)}` optimization upper bound for level `r`. **R44AF does not reverse that upper bound into a lower bound.**

Instead we use the explicit standard formulation itself. Schoenebeck describes level `r` by defining vectors for AND functions on up to `r` variables. Hence a materialized level-`r` state contains at least one indexed object for every variable subset of size at most `r`.

If the lower-bound instance survives `r = alpha n` levels for a fixed `alpha > 0`, then the explicit state contains at least

`binomial(n, min(floor(alpha n), floor(n/2))) = 2^{Omega(n)}`

subset-indexed objects, by the standard binomial/Stirling bound.

So the superpolynomial barrier comes from an explicit state-count lower bound for this fixed materialized hierarchy, not by reversing an algorithmic upper bound.

## TRUMP consequence

`GLOBAL_RELAXATION != GLOBAL_EXACT_DECISION`.

`RELAXATION_STILL_FEASIBLE != SAT`.

`LINEAR_LEVEL_EXPLICIT_STATE => EXPONENTIAL_MATERIALIZED_STATE`.

The architecture is global, but exactness debt appears as required hierarchy level and the corresponding explicit moment/vector state.

Thus this fixed explicit standard level-escalation route cannot discharge `L4` polynomial live state and therefore cannot serve as a polynomial-work `L3` route when the standard level is materialized and processed.

## Accounting firewall

`n^{O(r)}` is an upper bound, not a lower bound.

The actual barrier used here is:

`Omega(n) REQUIRED LEVEL + EXPLICIT SUBSET INDEXING => 2^{Omega(n)} MATERIALIZED STATE`.

It remains forbidden to hide the exponential materialized hierarchy inside one macrostep.

## Scope

R44AF is not a lower bound for implicit or nonstandard SoS algorithms, every SDP algorithm, every global algorithm, or every 3-CNF instance. It does not imply `P != NP`.

It blocks one precisely fixed, strong **explicit standard** global relaxation architecture as an easier universal path.

The next admissible transition model must therefore either use a proved polynomial-size implicit global invariant or be a different exact non-relaxation mechanism, with all update/work costs charged explicitly.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
