# JANUS Fundamentum: Exact-One acyclic incidence-graph solver

**Status:** research-only component, not a universal P=NP algorithm.

The existing `research/exactone_parity_preprocessor.py` reduces arbitrary signed linear/cubic Exactly-One SAT in polynomial time with checkable XOR and clause certificates, but can leave a residual instance. This additional solver `research/exactone_forest_dp.py` handles **every residual whose bipartite variable–clause incidence graph is a forest**, using a deterministic two-state tree dynamic program.

A factor node is a clause with exactly one of its literals true, including negative or repeated literals. A variable node is Boolean. Every clause has arity at most three, hence the factor-to-variable message can be checked by at most four choices for its other variables. Variable-to-factor messages are intersections of child feasibility masks. The bottom-up masks determine SAT or UNSAT; upward witness backpointers reconstruct a full satisfying assignment if possible. The independent polynomial verifier checks each recorded local message against the original residual constraints and independently checks any reconstructed SAT witness directly against the **original** Exact-One input. It also verifies the preprocessor's certificates. A tampered bit in a local message must be rejected, even if the output SHA is recomputed.

**Theorem:** For all linear/cubic Exact-One inputs with an *acyclic* incidence graph after sound polynomial preprocessing, the combined system decides satisfiability and constructs a satisfying assignment when one exists, within the existing conservative `O(L^5)` bit-operation preprocessor bound. The forest DP itself takes `O(L)` word operations for bounded arity 3 and returns a locally checkable table. If the residual incidence graph contains a cycle, the result is `OPEN_CYCLIC` — no general solution claim, no failure reinterpreted as UNSAT.

Input example: `{"n":5,"clauses":[[1,2,3],[3,4,5]]}`. This connected two-clause factor tree requires no unit clauses and is not completely solved by basic parity propagation, but forest DP returns a verifiable satisfying assignment. A cyclic example is `{"n":4,"clauses":[[1,2,3],[2,3,4]]}`: a cycle may remain and the algorithm honestly reports `OPEN_CYCLIC`.

## Tests and traceability

```bash
python research/exactone_forest_dp.py --self-test
python research/exactone_forest_dp.py --input /tmp/problem.json --output /tmp/forest-result.json
```

The deterministic suite includes signed tree factors, contradictory unary constraints, repeated factors, cyclic controls, a negative tampered-message control, and independent brute-force truth checks for small instances. The suite does not hide exponential enumeration inside the solver; the oracle runs only in tests.

The Lapis bridge carries the generated forest certificate **as annotated, inspectable JSON**, preserving its checksum and independently verifying the result in Fundamentum before accepting it. Lapis does not convert Rowan's pTM/avg_lDDT scientific predictions into SAT constraints, solutions or mathematical facts; these are kept in a separate evidence lane. The provider does not expose a documented generic SAT execution workflow.

Formal boundary: polynomial for forest incidence instances only. `P_VS_NP=OPEN`. No Rowan provider credits or production changes.
