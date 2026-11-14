# Exact-One 2-variable cycle-cutset proof-carrying solver (bounded class)

This research component extends the previously verified polynomial Exact-One preprocessor and acyclic incidence forest DP. It **does not** provide a generic polynomial NP-complete solver or prove P=NP.

## Bounded class and theorem

Consider the bipartite incidence graph of a linear/cubic Exact-One SAT input. If deleting edges incident to **at most two variable vertices** makes this graph acyclic, the algorithm `research/exactone_bounded_cycle_cutset.py` decides SAT/UNSAT and, for SAT, reconstructs a witness. Its search for a cutset enumerates all variable subsets of size 0, 1 and 2, using an ordinary cycle detector. The search is therefore polynomial for the frozen constant bound 2. A valid selected cutset of size k has at most 2^k <=4 assignments. Each branch is encoded by genuine Exact-One unary clauses, processed by the certificate-producing polynomial parity preprocessor and solved by the independently checkable incidence forest DP. Branches with UNSAT must carry valid certificates. To claim UNSAT, all possible assignments to the cutset must have been rejected; to claim SAT, one full satisfying assignment is verified directly against the original clauses. When no cutset of size <=2 is found, the output is `OPEN_NO_SMALL_CUTSET`, not UNSAT.

For general L = 1+n+total literals, the combined algorithm has a conservative **O(L^7) bit-operation upper bound** for the fixed cutset limit 2 (tighter analysis is possible). The certification verifier runs in polynomial time for the fixed bound. This result applies only to the recognized graph class, not to arbitrary networks with unrestricted cycle structure.

## Reproducible usage

~~~bash
python research/exactone_bounded_cycle_cutset.py --self-test
python research/exactone_bounded_cycle_cutset.py --input /tmp/exactone.json --output /tmp/answer.json
~~~

A cyclic demonstration instance:

~~~json
{"n":4,"clauses":[[1,2,3],[2,3,4]]}
~~~

A single deleted variable breaks the factor cycle, and the result has a verifiable Boolean witness.

A regression suite uses small signed/repeated-literal random cases with an **independent complete truth-table enumerator**; a top-level-hash-recomputed forged witness is rejected. The enumeration is a test oracle, **not** the solver.

## Lapis and Rowan isolation

The real Rowan BBC1 archive is ingested through Lapis as an experimental observation candidate with independent provider-authentication status unchanged. In parallel, Lapis carries the purely mathematical certificate as an annotation-only IR. Numeric structure-confidence predictions never enter the SAT clauses or influence branch decisions. Provider credit spend, new Rowan API jobs, cross-repository writes and proof promotion are not enabled by this research proposal.

All artifacts remain in Draft PR #571. The universal polynomial `SolveLinearCubicXSAT` remains OPEN.
