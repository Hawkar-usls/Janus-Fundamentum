# C025 — Akinator large-support ROBDD certificate lane

Canonical TOPA source:

`Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_AKINATOR_LARGE_SUPPORT_ROBDD_CERTIFICATE.md`

Claim ceiling: **P_VS_NP = OPEN**

## Positive local theorem

Under an explicit frozen root-variable order, a reduced ordered binary decision diagram (ROBDD) is used as a proof-carrying exact semantic certificate for a B2 macro.

- root literals have immediate canonical diagrams;
- `NOT` is constructed by terminal complementation plus deterministic reduction;
- `AND` is constructed by memoized pair-APPLY, visiting at most the Cartesian product of parent nodes before reduction;
- restriction by a partial root assignment is polynomial in explicit diagram bytes;
- a reduced residual diagram is nonconstant iff its root is nonterminal;
- explicit 0/1 witnesses are obtained by deterministic paths to the two terminals.

Thus construction, verification, restriction, and exact residual-survival discovery are polynomial in explicit parent/child ROBDD bytes. A polynomial-in-original-`N` claim additionally requires a universal polynomial bound on those bytes.

## Large support does not kill the lane

Parity on `n` roots has support `n` but only two semantic prefix states (even/odd), yielding an `O(n)` ROBDD under the natural order.

`LARGE_SUPPORT != LARGE_ROBDD_CERTIFICATE`.

## Exact residual-frontier parameter

For frozen order `x_1,...,x_n`, let `R_i(f)` be the number of distinct residual functions after assigning the first `i` variables. Distinct residual functions cannot merge into one reduced ordered state, so ROBDD size is at least the maximum residual frontier up to terminal-count convention.

## Explicit order-sensitivity counterfamily

`EQ_n(X,Y)=AND_j(x_j <-> y_j)` has an `O(n)` B2 DAG.

Under order `X_1,...,X_n,Y_1,...,Y_n`, fixing X leaves `2^n` distinct point-indicator residual functions on Y. Therefore the frozen-order ROBDD is exponential.

Under interleaved order `X_1,Y_1,...,X_n,Y_n`, it has constant width and linear size.

Hence:

`SMALL_B2_DAG != SMALL_ROBDD_UNDER_ARBITRARY_FIXED_ORDER`.

## External ordering boundary

Bollig and Wegener (IEEE Transactions on Computers 45(9), 1996, DOI 10.1109/12.537122) proved the general OBDD variable-order improvement problem NP-complete. This external result blocks treating generic adaptive order search as free. It does not prove hardness for the exact NW target macro class.

## Current gate

A viable Akinator route now needs either:

1. a deterministic input-derived order proved sufficient on the target states; or
2. a target-specific deterministic polynomial order/decomposition constructor.

An advertised small-order certificate is insufficient without cheap discovery.

`GOOD_ORDER_DISCOVERY = OPEN`  
`GLOBAL_PROGRESS = OPEN`  
`POLYNOMIAL_AKINATOR = OPEN`  
`P_VS_NP = OPEN`
