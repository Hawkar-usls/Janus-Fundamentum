# A3 Ternary DP — Publication Claim Ceiling

Frozen publication authority: `publication/A3_TERNARY_DP/PUBLICATION_MANIFEST.json`.

## Established in the stated project formal domain

- Endpoint compression preserves exact path-width for finite-field subspace arrangements consisting of `k` distinct geometric subspace classes with arbitrary positive multiplicities.
- With `s` singleton classes and `r` repeated classes, the endpoint-state DAG has exactly `2^s * 3^r` states.
- Its exact directed-transition count is `s*2^(s-1)*3^r + 2*r*2^s*3^(r-1)` with absent-type terms interpreted as zero.
- After the `2^k` subset-rank table is available, state width is obtained from `lambda(P,S)=rho(S)+rho(K\P)-rho(K)` and the combinatorial bottleneck-DP phase is `O(k*3^k)`.
- The result is exact, not heuristic.

## Evidence status

`ES5_GENERAL_ALGORITHMIC_THEOREM_ADMITTED`.

Novelty status: `N3_NOVELTY_CANDIDATE`.

External independent replication: `NOT_ESTABLISHED`.

World-novelty level N4: `NOT_ESTABLISHED`.

## Forbidden promotion

This publication package MUST NOT claim that:

- general matroid path-width is polynomial-time solvable;
- known NP-hardness for the unrestricted problem has been overturned;
- the algorithm is polynomial in unrestricted `k`;
- historical world priority has been proved;
- external independent verification or peer review has occurred;
- `P=NP`, `P!=NP`, or any other A0--A2 open problem has been resolved.

A literature search failing to find an equivalent prior result may strengthen the documented N3 search record, but cannot by itself establish universal absence or N4.
