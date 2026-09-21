# E8-D1 admission audit: exact elimination is a rejected reference

Date: 2026-09-21.
Authority: SOURCE_AND_SYMBOLIC_ADMISSION_AUDIT_ONLY.
Classification: REDISCOVERY_OF_EXISTING_MECHANISM.
No execution, candidate admission, novelty claim, or theorem seal.

The future E8-D1 candidate slot is **not** filled by this reference algorithm.

## A complete reference procedure

Clauses are finite sets of signed literals; formulas are finite sets of clauses.
Normalize removes tautological clauses and exact duplicate literals/clauses.
It does not consult satisfiability or semantic-equivalence oracles.

Use the increasing numeric order of variable identifiers. Intermediate clauses
may be longer than three: the input convention does not constrain intermediates.

    Decide_DP(Phi):
        C = Normalize(Phi)
        while true:
            if empty_clause belongs to C:
                return UNSAT
            if C is empty:
                return SAT

            x = smallest variable identifier occurring in C
            P = { clause minus {x}     : clause in C and x in clause }
            N = { clause minus {not x} : clause in C and not x in clause }
            Z = { clause in C : neither x nor not x is in clause }

            R = empty set
            for A in P:
                for B in N:
                    D = A union B
                    if D contains no complementary literal pair:
                        add D to R
            C = Normalize(Z union R)

This is variable elimination by resolution. The rule is described in
[Eén–Biere, section 2](https://fmv.jku.at/papers/EenBiere-SAT05.pdf).
Its cost includes every pair attempt, normalization, storage and output write.

## Soundness, completeness and termination

Write the formula before eliminating x as

    Z AND conjunction_i (x OR A_i) AND conjunction_j (not x OR B_j).

For every assignment to the remaining variables,

    exists x C  iff  Z AND conjunction_i,j (A_i OR B_j).

Forward: every original assignment satisfies each resolvent.

Reverse: if an A_i is false, all B_j must be true, so choose x=true.
If every A_i is true, choose x=false. This also covers empty P or N.
Deleting tautologies and duplicates preserves the relation.

Induction over eliminations preserves existential satisfiability. The two
terminals therefore answer correctly. Each round removes one occurring
variable, introduces none, and processes finite clause sets. There are at
most the original number of variables many rounds.

A witness can be recovered by storing the eliminated clauses and applying
the same reverse choice after the later variables have been assigned.
The potentially large receipt is part of the cost; it is not a free certificate.

These arguments establish the first three obligations for this reference.
A bound on the number of rounds is not a bound on the size of a round.

## A symbolic obstruction to its polynomial runtime

Fix k >= 2. Let x1,...,xk be visible variables and y2,...,yk auxiliaries.
Define y2 = x1 XOR x2 and, for j=3,...,k, yj = y(j-1) XOR xj.
Require yk=true.

Encode w = u XOR v by the four clauses

    ( u OR  v OR not w)
    ( u OR not v OR  w)
    (not u OR  v OR  w)
    (not u OR not v OR not w).

Together with the unit (yk), this is a 3-CNF with

    variables = 2k - 1
    clauses   = 4(k - 1) + 1
    input bit length L_k = O(k log(k+1)).

Assign numeric identifiers in the order

    yk, y(k-1), ..., y2, x1, ..., xk.

The fixed-order reference algorithm must therefore eliminate all auxiliaries
before any visible variable. At that point exact projection gives

    x1 XOR ... XOR xk = 1.

The formula is satisfiable, so no UNSAT terminal can occur. Before that point
the exact projection is not the constant true relation, so C cannot be empty.

### Lower bound for a CNF over only the visible variables

Any non-tautological clause implied by odd parity must mention every xi.
Otherwise, falsify the mentioned literals and toggle a missing variable:
one of the two extensions has odd parity while still falsifying the clause.

After duplicate removal, a clause mentioning all k variables forbids exactly
one assignment. There are 2^(k-1) even-parity assignments to exclude.
Consequently, **any equivalent flat CNF over x1,...,xk needs at least
2^(k-1) clauses and k*2^(k-1) literal occurrences**.

The lower bound applies at an actual intermediate state of the specified
reference algorithm. Its materialization cost alone exceeds every fixed
polynomial in L_k. Hence REF-POLY fails; it is not merely unproved.

The general parity/CNF succinctness separation is already discussed in
[Darwiche–Marquis, Appendix A, Table 10 discussion](https://arxiv.org/pdf/1106.1819).
The exact count above is justified by the elementary assignment argument here.
This note claims no novelty for the separation.

## Exact interpretation

| Obligation for this reference only | Outcome |
|---|---|
| REF-SOUND | Established by the elimination identity |
| REF-COMPLETE | Established by the elimination identity |
| REF-TERMINATES | At most one round per variable |
| REF-POLY | Rejected by the explicit intermediate output-size bound |

This does not run the forbidden exponential expansion. The argument is
symbolic for arbitrary k; no finite stress-family sweep was performed.

The obstruction depends on materializing an equivalent CNF **without
auxiliaries**, after the specified projection. A compact XOR representation,
an affine solver, a different order, or retained auxiliaries can avoid this
particular expansion. Parity itself is easy. No lower bound for arbitrary SAT
or for the unrestricted E6 carrier follows.

Under E6, these inputs are inside the arbitrary signed 3-CNF semantics; no
new graph gadget or hidden source restriction is needed to interpret them.
This does not turn the example into evidence that the full source class is
harder than already known.

A polynomial pre-expansion cap would keep resource use bounded but could
return OPEN. That is a valid partial method, not a complete decider. The
repository already contains a scoped guarded-elimination theorem, so such a
guard is not promoted here as a new mechanism.

## Admission decision

    REFERENCE_DP = REJECTED_AS_POLYNOMIAL_E8_CANDIDATE
    E8_D1_CANDIDATE = MISSING
    E8_D1_EXECUTION = NOT_RUN
    P_VS_NP = OPEN
    NEW_THEOREM_SEAL = NONE

The remaining task is an explicit algorithm whose total resource proof
covers every input. This reference audit supplies no such algorithm.
