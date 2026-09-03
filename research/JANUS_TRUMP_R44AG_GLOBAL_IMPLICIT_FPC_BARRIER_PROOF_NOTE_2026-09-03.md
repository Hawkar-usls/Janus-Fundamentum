# JANUS TRUMP R44AG — Global implicit FPC barrier

## Fixed model

The route under test is one fixed program in Fixed-Point Logic with Counting (FPC) over the standard **unordered** relational encoding of 3-CNF/CSP instances. The route is global: it may use fixed-point recursion and counting. It is not restricted to bounded-local clause propagation.

## Published inexpressibility basis

Atserias, Bulatov and Dawar (TCS 2009, DOI 10.1016/j.tcs.2008.12.049) prove strong counting-logic inexpressibility for affine CSPs, including systems of equations over finite Abelian groups, and develop the transfer to CSP templates through algebraic/reduction machinery. Dawar's 2015 survey explicitly records the resulting consequence that 3-SAT is not definable in FPC.

Hence there is no single FPC definition which, on all standard unordered relational encodings of 3-SAT instances, exactly separates SAT from UNSAT.

## TRUMP consequence

A TRUMP transition/decision architecture whose complete semantics remain inside this fixed unordered FPC model cannot discharge universal exact 3-SAT decision. Adding recursion and counting therefore escapes the bounded-local Datalog route but still does not reach universal exactness **inside this model**.

This is an architecture-specific, unconditional barrier. It does **not** show that arbitrary deterministic polynomial-time algorithms fail: FPC is a proper and natural symmetry-respecting model of computation on unordered structures, not all of PTIME.

## Ordered-input scope correction

A standard Turing/RAM algorithm receives an ordered string encoding. It may legitimately use the input's presented variable/clause order internally. Its internal trajectory may change under a permutation of the encoding as long as the final SAT/UNSAT answer remains correct.

Therefore:

- `INPUT_ORDER != CANONICAL_ORDER`;
- using the supplied input order does **not** require first computing a canonization;
- the unordered-FPC lower bound does not automatically transfer to an ordinary ordered-input algorithm.

Canonization becomes an obligation only if a future route specifically claims a canonical or permutation-invariant ordering, not merely because it reads the input sequence it was given.

## Required successor escape

The next legitimate target is therefore stricter and cleaner: give one deterministic exact transition law in the ordinary ordered-input model and prove its total charged work polynomial on arbitrary 3CNF, or fix one precise ordered global model and prove a barrier for it.

Firewalls:

- `FPC_INEXPRESSIBILITY != P_NE_NP`
- `FPC != ALL_POLYNOMIAL_TIME_ALGORITHMS`
- `UNORDERED_FPC != ORDERED_TURING_MODEL`
- `INPUT_ORDER != CANONICAL_ORDER`
- `USING_PRESENTED_INPUT_ORDER != SOLVING_CANONIZATION`
- `MODEL_INDISTINGUISHABILITY != SAT_EQUIVALENCE`

Scientific status: `P_VS_NP=OPEN`.
