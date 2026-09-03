# JANUS TRUMP R44BC — logarithmic maximum-deficiency local terminal for CNF states

For a **CNF state** `F`, define maximum deficiency

`delta*(F) = max_{F' subseteq F} (c(F')-n(F'))`.

Stefan Szeider proved that SAT for CNF formulas of maximum deficiency `k` can be decided in time

`O(2^k n^3)`

and that the algorithm returns a satisfying assignment in the SAT case or a regular-resolution refutation in the UNSAT case. Maximum deficiency is polynomial-time computable by bipartite matching.

Let `S>=2` be the encoded size of the **current CNF state**. Apply the terminal only when

`delta*(F) <= floor(log_2 S)`.

Then

`2^delta*(F) <= S`

and `n<=S`, hence

`O(2^delta* n^3) <= O(S^4)`.

Thus R44BC is a deterministic exact uniform polynomial terminal relative to the current CNF state:

1. compute `delta*(F)`;
2. if `delta*(F)>floor(log_2 S)`, return `NO_PROGRESS`;
3. otherwise run Szeider's exact algorithm and return its certificate for this CNF state.

## Original-input accounting

R44BC does not silently identify current state size with original input size. If a larger TRUMP constructor has independently proved an L4 envelope

`S <= N^c`

for original input size `N`, then R44BC costs

`O(S^4) <= O(N^(4c))`.

Without such an inherited state envelope, R44BC proves only polynomiality in its current CNF input size.

## Representation boundary

`delta*` is a CNF clause-set parameter. R44BC does not directly apply to GF(2), circuit, DNNF, quantified, selector, or other non-CNF states. Such a state enters this gate only after a separately proved exact polynomial conversion to CNF, including its state/work and replay accounting.

Therefore:

`CNF_MAXDEF_TERMINAL != TERMINAL_FOR_EVERY_REPRESENTATION`.

## Certificate boundary

Szeider's SAT assignment or regular-resolution refutation certifies the **current CNF state**. If that state was produced by previous exact transformations, Legend L6 additionally requires predecessor metadata that reconstructs eliminated SAT variables or derives successor clauses back from the original CNF.

R44BC does not itself supply that whole history, so:

`LOCAL_CERTIFICATE != END_TO_END_REPLAY`.

## Other boundaries

The FPT theorem is not an ordinary polynomial algorithm when `delta*` is unbounded. The logarithmic gate works because the published exponential factor becomes polynomial in the current state size.

`FPT != P_FOR_UNBOUNDED_PARAMETER`

`k > log S != HARDNESS_CERTIFICATE`

`NO_PROGRESS != UNSAT`.

Global status remains:

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`.

Published basis: Stefan Szeider, *Minimal unsatisfiable formulas with bounded clause-variable difference are fixed-parameter tractable*, JCSS 69(4), 2004; ECCC TR03-002.
