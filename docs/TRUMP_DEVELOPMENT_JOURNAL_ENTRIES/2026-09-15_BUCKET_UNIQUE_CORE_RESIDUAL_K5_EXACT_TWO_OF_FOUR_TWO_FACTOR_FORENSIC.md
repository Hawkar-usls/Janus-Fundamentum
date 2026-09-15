# 2026-09-15 — exact-two-of-four K5 cardinality / two-factor forensic

Authority: `DIAGNOSTIC_ONLY`. No scientific promotion.

The v3.16 raw-semantic forensic left a reproducibly generated nonuniversal K5 probe outside the sealed fixed-depth `1->2->2` portfolio. Each of its five K5 vertex relations contains exactly the six four-bit tuples of Hamming weight two. Captain Obvious required semantic classification before any size-4 separator mechanism.

The successor was preregistered before implementation at `729a72dd12e9ef5ac5cfaa2f4033f089cfa878a7`. The preregistered hypothesis was that interpreting each Boolean residual variable as selection of its corresponding K5 edge turns every local exact-two-of-four relation into the exact vertex constraint `selected_degree(v)=2`; globally the satisfying edge sets should therefore be spanning 2-factors. For K5 the finite specialization predicted exactly twelve solutions, every one a single five-cycle.

The immutable first execution, Actions `35019074281 / 104549852738`, failed before the independent checker with `EXPECTED_FIVE_TARGET_FACTORS:0`. This was an implementation-selection failure, not a scientific falsifier: the existing `_prepare()` path canonicalizes source `sticky_*` relation IDs into `orig:*`, while the first candidate implementation still filtered on the pre-prepare prefix. The frozen preregistration was not changed.

The candidate was repaired at `0bf1005c5ff73cc4c19cfa92a4d530a0fd21519c` to locate the unique five-factor K5 component from residual-overlap invariants: five arity-four exact-weight-two relations, all ten pair overlaps of size one, ten residual variables total, and every residual variable occurring in exactly two component factors. It does not hard-code the canonical `orig:19..23` IDs.

The independent checker was repaired separately at `2cadc96ec3020e90a8fcaf24ae1e34e288765d5f`. It independently rebuilds the ten K5 edge variables, then matches prepared residual scopes against the four incident variables for each abstract vertex. It does not import candidate discovery helpers. The candidate exhaustively checks all 1024 finite K5 edge assignments; the checker uses the degree handshake identity and independently checks the 252 five-edge subsets plus its own cycle traversal.

The repaired run `35019473824 / 104551283525` completed `SUCCESS`. Candidate, independent checker, all preregistered assertions, and regressions v3.16, v3.15 and v3.14 were all green.

The exact finite receipt is unambiguous: relation truth equals the selected-degree-two predicate on every one of the 1024 K5 edge assignments; there are zero semantic mismatches; there are exactly twelve satisfying edge sets; every satisfying set has five edges and degree vector `[2,2,2,2,2]`; and every one is a single five-cycle. The independent 252-subset method derives the identical solution family.

The broader semantic identity used here is representation-preserving, not a quotient: for an undirected graph with one Boolean variable per edge, the conjunction over vertices of `sum_{e incident to v} x_e = 2` is satisfied exactly by spanning 2-factors of the graph. This is the `f(v)=2` specialization of the classical f-factor object.

This diagnostic does **not** yet import or seal an f-factor algorithm. The fact that classical f-factor / matching theory is polynomial is only a candidate algorithmic door until TRUMP binds it to: exact recognition of the admitted raw relation family, an exact construction/reduction, proof-carrying witness reconstruction, exact original-relation verification, and one total polynomial resource envelope in the original explicit input size.

No size-4 separator assignment was enumerated. There were zero solver/carrier calls, zero separator>=3 Boolean branches, zero unbounded recursion, zero 3+ join chains, zero global residual Cartesian products, and no budget raise. `SIZE4_BRANCHING_LICENSED=false` remains frozen.

PR #473 merged the diagnostic lineage as `295b536e4a832c1adba8ce53362865df57e94aa0`.

Captain Obvious' next preferred successor is therefore not a size-4 separator theorem but `TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_EXACT_TWO_FACTOR_F_FACTOR_CARRIER_FALSIFIER_GATE`: a separately preregistered proof-carrying carrier attempt for the exact recognized 2-factor relation family.

Firewalls remain `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, `CONNECTED_MIXED_CORE_SOLVED=NO`, and `GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY=NOT_PROVED`. The global APMA frontier did not advance.
