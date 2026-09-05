# JANUS TRUMP R50G9 — explicit wide-fixpoint ancestry witness

R50G8 reduced any same-pivot failure to a final nonterminal certified normalization fixpoint containing a wide clause with replayable DP/BVE ancestry and a complete nonblocking support graph.

R50G9 attacks that exact obstruction directly rather than enlarging a corpus.

Start from the sealed R47I normalization-fixed core `K` with hash `c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb`. Introduce a fresh pivot `x=1` and two W4 parents

- `P=(1,-2,-5,-9)`
- `N=(-1,24,-30)`.

Their unique non-taut cross-pivot resolvent is

`C=(-2,-5,-9,24,-30)`, width 5.

The source is `F = K ∪ {P,N}`. Because pivot 1 is fresh and least-numbered, exact frozen checks must establish that no earlier R33 rule applies and that the first BVE candidate is pivot 1. Exact DP then removes the two parents and inserts C, yielding `G = K ∪ {C}` up to canonical/subsumption normalization.

If certified R47J normalization leaves `G` nonterminal with width 5, then the broad local theorem

`NO_PRE_BVE_CLEAN_W4_SOURCE_CAN_GENERATE_A_WIDE_ANCESTRY_CERTIFICATE_ENDING_AT_A_NONTERMINAL_CERTIFIED_NORMALIZATION_FIXPOINT`

is false. This would not by itself refute the reachable-domain theorem, because reachability of F under the refined U_mu controller is a separate obligation.

For a surviving wide clause C in a certified R33/RUP fixed point, each literal l in C must have a distinct clause D_l containing -l such that the resolvent of C and D_l on l is non-tautological. In addition, D_l must contain at least one literal outside C\{l}; otherwise C\{l} is immediately RUP-strengthenable using C and D_l, contradicting RUP fixedness. R50G9 emits those witnesses explicitly.

The executable gate also exhaustively exposes all existing R49H and R47J_SAFE doors on F. Therefore the outcomes are separated cleanly:

1. same-pivot wide survivor + alternate certified door exists: local same-pivot safety is false, but the broader existing-door implication survives on this witness;
2. same-pivot wide survivor + no alternate certified door: explicit local guarded obstruction under current lanes, still not called reachable without a reachability proof;
3. no wide survivor: this candidate fails and R50G8 remains open.

No heuristic choice, learned selector, probabilistic authority, or new semantic inference rule is introduced.
