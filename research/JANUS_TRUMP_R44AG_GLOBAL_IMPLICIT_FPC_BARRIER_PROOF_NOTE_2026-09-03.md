# JANUS TRUMP R44AG — Global implicit FPC barrier

## Fixed model

The route under test is one fixed program in Fixed-Point Logic with Counting (FPC) over the standard unordered relational encoding of 3-CNF/CSP instances. The route is global: it may use fixed-point recursion and counting. It is not restricted to bounded-local clause propagation.

## Published inexpressibility basis

Atserias, Bulatov and Dawar (TCS 2009, DOI 10.1016/j.tcs.2008.12.049) prove strong counting-logic inexpressibility for affine CSPs, including systems of equations over finite Abelian groups, and develop the transfer to CSP templates through algebraic/reduction machinery. Dawar's 2015 survey explicitly records the resulting consequence that 3-SAT is not definable in FPC.

Hence there is no single FPC definition which, on all standard unordered relational encodings of 3-SAT instances, exactly separates SAT from UNSAT.

## TRUMP consequence

A TRUMP transition/decision architecture whose complete semantics remain inside this fixed FPC model cannot discharge universal exact 3-SAT decision. Adding recursion and counting therefore escapes the bounded-local Datalog route but still does not reach universal exactness.

This is an architecture-specific, unconditional barrier. It does **not** show that arbitrary deterministic polynomial-time algorithms fail: FPC is a proper and natural subclass/model of PTIME computation on unordered structures, not all of PTIME.

## Required successor escape

A successor may claim novelty only if it names an operation/resource outside this model and charges it explicitly. Examples include a canonically constructed order/choice operation or another precisely specified algebraic/global primitive. Merely assuming an arbitrary order is not a mathematical escape: the construction and cost of that order must be proved.

Firewalls:

- `FPC_INEXPRESSIBILITY != P_NE_NP`
- `FPC != ALL_POLYNOMIAL_TIME_ALGORITHMS`
- `GLOBAL_FIXED_POINT_COUNTING != UNIVERSAL_3SAT_DECISION`
- `MODEL_INDISTINGUISHABILITY != SAT_EQUIVALENCE`
- `FREE_SYMMETRY_BREAKING != PROVED_POLYNOMIAL_CANONIZATION`

Scientific status: `P_VS_NP=OPEN`.
