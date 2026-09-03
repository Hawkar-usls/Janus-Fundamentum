# JANUS TRUMP R44BC — logarithmic maximum-deficiency exact terminal

For a CNF formula `F`, define maximum deficiency

`delta*(F) = max_{F' subseteq F} (c(F')-n(F'))`.

Stefan Szeider proved that SAT for formulas of maximum deficiency `k` can be decided in time

`O(2^k n^3)`

and that the algorithm outputs a certificate: a satisfying truth assignment in the SAT case or a regular-resolution refutation in the UNSAT case. Maximum deficiency itself is computable in polynomial time by bipartite matching.

Let `N>=2` be the encoded size of the current state measured against the original-input accounting envelope, and apply the algorithm only when

`delta*(F) <= floor(log_2 N)`.

Then

`2^delta*(F) <= N`

and `n<=N`, so

`O(2^delta* n^3) <= O(N^4)`.

Hence the following is one deterministic uniform polynomial-time exact terminal rule on arbitrary CNF:

1. compute `delta*(F)`;
2. if `delta*(F) > floor(log_2 N)`, return `NO_PROGRESS`;
3. otherwise run the exact maximum-deficiency SAT algorithm and return its SAT witness or UNSAT regular-resolution certificate.

This rule is not restricted to width 3 and can therefore terminate some wider CNF successors created by previous exact transitions.

## Boundary

The fixed-parameter theorem itself is not an ordinary polynomial algorithm when `delta*` is unbounded. R44BC only invokes it below the explicit logarithmic cutoff, where the published `2^k` factor becomes polynomial in `N`.

Therefore:

`FPT != P_FOR_UNBOUNDED_PARAMETER`

`k > log N != HARDNESS_CERTIFICATE`

`NO_PROGRESS != UNSAT`.

R44BC does not alter the global status:

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`.

Published basis: Stefan Szeider, *Minimal unsatisfiable formulas with bounded clause-variable difference are fixed-parameter tractable*, JCSS 69(4), 2004; ECCC TR03-002.
