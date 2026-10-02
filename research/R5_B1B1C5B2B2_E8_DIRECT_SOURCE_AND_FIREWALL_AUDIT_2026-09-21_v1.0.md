# E8-DIRECT — source and firewall audit

Authority: SOURCE_AND_FIREWALL_AUDIT_ONLY. Date: 2026-09-21.
Base main: 82493a57d05cd186b0c119e5fcc3b416649e7860.
No algorithm result or theorem seal is asserted here.

## Recovered authority

The pinned main contains E7's declared universal E6 exact-carrier equivalence.
The preceding readback verified the contents of six E6/E7 blobs and the four
E7 seal bindings. The same main SHA was checked again for this draft.

The historical v3.23 bootstrap concerns a scoped connected-mixed source census.
It is not silently replaced by this E8 proposal. C5C stays locked, recursive
general R1/R2 stays forbidden, and the existing theorem seals are unchanged.

The four contribution documents were read: README.md, CURRENT_RESEARCH_STATUS.md,
A3_PUBLICATION_TRACK.md, and C023_FORMULA_CACHING_CALCULUS.md.

## Published and repository predecessors

| Source | What is reused | Novelty classification |
|---|---|---|
| [Huang, section 2](https://arxiv.org/html/1304.5808v2) | Arbitrary signed 3-SAT occurrences in the P7-free coloring construction | Published hardness framework |
| [Cook, printed p. 5](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf) | NP-completeness implication and search-to-decision | Standard facts |
| [Darwiche–Marquis](https://arxiv.org/pdf/1106.1819) | Distinction between representation size, queries and transformations | Existing compilation framework |
| [Eén–Biere, section 2](https://fmv.jku.at/papers/EenBiere-SAT05.pdf) | Variable elimination by pairwise resolution | Existing elimination rule |
| docs/C023_FORMULA_CACHING_CALCULUS.md, blob dc2478f85401b578c75ac99561f4fba349631f4e | Exact syntactic residual caching, charged local resolution, open general complexity | Existing repository mechanism |
| research/TRUMP_BICAMERAL_GUARDED_BOUNDED_OUTPUT_ELIMINATION_THEOREM_2026-09-15.md, blob 525ff3befdbd9fc03ee1da98fbe09b0b5f0f3fb2 | A pre-expansion guard that returns OPEN before overbudget work | Existing scoped repository theorem |

The primary Davis–Putnam article was identified at DOI 10.1145/321033.321034,
but its full text returned HTTP 403 in this check. The elimination rule below
is supported by the accessible primary Eén–Biere paper and an explicit proof;
no claim of having read the inaccessible article is made.

No exhaustive novelty search or literature priority claim is made.

## Exact convention and standard interface

3-CNF means clauses of size **at most three**.

For a graph with N vertices, M edges, and lists in {1,2,3,4}, use four color
bits and one auxiliary a per vertex. The at-least-one constraint is

    (b1 OR b2 OR a) AND (NOT a OR b3 OR b4).

Existentially eliminating a gives b1 OR b2 OR b3 OR b4. Add six binary
at-most-one clauses per vertex, four binary inequality clauses per edge,
and one unit for each forbidden vertex color.

This gives 5N variables and at most 12N+4M clauses. The explicit bit size is
O((N+M+1) log(N+2)). This is an encoding, not a SAT decision procedure.

Given a correct polynomial decider, an initial decision followed by at most
one restriction query per occurring variable recovers a witness in n+1 calls.
This standard wrapper does not supply the missing decider.

## No hidden equivalence or certificate constructor

Let bottom = (z) AND (NOT z), interpreted over the union variable set.
Then EQ(F,bottom) holds exactly when F is unsatisfiable. An unexplained exact
equivalence test on arbitrary residuals therefore hides a SAT decision problem.

A sound efficiently computed sufficient invariant can justify particular
merges. It need not recognize every valid merge. However, the full algorithm
must still terminate with the correct answer and a polynomial total cost when
the test declines.

A polynomial certificate **verifier** is not a polynomial certificate
**constructor**. Discovery, certificate length, failed attempts, verification
and all unmerged states remain charged.

A resource-bounded procedure returning OPEN is scientifically acceptable as
research software. It does not meet the universal SAT/UNSAT decider contract.

## Scope of the accompanying reference audit

The separate elimination note writes a concrete complete reference Decide
procedure and derives its failure of polynomial runtime for a specified order
and explicit flat-CNF state representation. This is a known-method admission
audit, not an E8-D1 candidate, execution result or new theorem seal.

It is not a lower bound for arbitrary SAT algorithms, arbitrary carriers,
alternate elimination orders, affine representations, or representations that
retain/add auxiliary variables. E8-D1 remains empty.
