# JANUS Fundamentum - bounded primal width, unbounded incidence cycle count

Date: 28 October 2026. Research Draft PR #571. P_VS_NP=OPEN.

## Contract and theorem

The new implementation in research/exactone_bounded_width_dp.py handles conjunctions of signed Exact-One clauses of arity 1 or 3, including repeated literals and isolated variables. It converts each clause to the Boolean set of locally satisfying assignments, then eliminates variables by exact existential projection of all factors containing that variable.

Let L denote the instance input length. For a witnessed elimination order of width w (the largest number of currently adjacent primal variables), any local projection examines at most 2^(w+1) assignments. The overall running time is O(poly(L)*2^(w+1)); replayable certificate size is O(L*(w+1)*2^w) entries, with ordinary index-encoding overhead. At fixed w, both are polynomial. At w=O(log L), the bounds are polynomial provided a suitable ordering is supplied/produced in polynomial time.

This implementation uses a deterministic minimum-current-degree heuristic and an explicit research width cap 2..6. A successful ordering is sufficient and checkable, but heuristic failure does not certify a graph's optimal treewidth. The cap cannot be silently exceeded. On failure the output is OPEN_WIDTH_CAP, not a claimed UNSAT result.

## Independent certificate checking

Every elimination step stores (a) the selected variable, (b) the remaining scope, (c) every feasible projected tuple, and (d) a Boolean witness choice for reconstructing the eliminated variable. The independent verifier rebuilds each initial factor from original signed clause semantics, checks the elimination order and separately enumerates every bucket to reproduce its projected relation. A false relation remains rejected even if the caller recomputes the JSON checksum.

At completion, a SAT witness is reconstructed in reverse and checked directly against all original clauses. For UNSAT, the verifier establishes an empty exactly-projected relation. There is no dependence on Rowan, data-driven estimates, hash-only proof claims, a remote SAT oracle, or unreviewed extrapolation.

## Unbounded-cycle family

For n>=4 take the n-2 cubic Exact-One clauses (x_i,x_(i+1),x_(i+2)), i=1..n-2. Adjacent clauses share two variables: thus the incidence graph contains at least n-3 distinct four-cycles, tending to infinity with n. However the primal graph is a path of overlapping triangles admitting an elimination order of width 2. Consequently exact projection yields a complete solver and certificates for this entire infinite family, with polynomial work. A complementary triple gives an UNSAT control. A dense clique exceeding the current cap gives a strict OPEN control.

This is an application of established bounded-treewidth CSP variable elimination, not a new general solution of P vs NP. See MIT treewidth SAT lecture https://courses.csail.mit.edu/6.854/18/Scribe/s25-online/s25-online.html and D. Marx CSP treewidth lecture https://www.cs.bme.hu/~dmarx/papers/marx-weizmann-hypergraph.pdf .

## Test commands

    python research/exactone_bounded_width_dp.py --self-test
    python research/exactone_bounded_width_dp.py --input /tmp/instance.json --width-cap 2 --output /tmp/proof.json

Tests use an independent exhaustive oracle on small signed/repeated-literal inputs; a 83-variable cyclic chain with 80+ incidence cycles; SAT, UNSAT, width failure, and adversarial mutated/rehashed projection controls.

## Lapis transport and Rowan separation

The cross-repo CI pins the genuine Lapis universal converter and translates two independent sources: a real BBC1 8/8 Rowan API receipt previously collected via JANUS main, and a Fundamentum Exact-One mathematical certificate. The second is transported solely as annotation-only algorithm IR and verified by Fundamentum against the exact original SAT input. No Rowan protein-confidence estimate enters the SAT computation. The Rowan provider is not asked to run SAT. Credit spend by this CI: zero. Main branches untouched.
