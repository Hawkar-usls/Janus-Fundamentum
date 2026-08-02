# C013 — circularity and specification terminal audit

## Scope

This document rejects six exact registry formulations as research mechanisms.
`REJECTED` does not mean that the corresponding existential statement has been
proved false. It means that the statement, as written, fails to isolate a
noncircular or well-defined mechanism beyond the target theorem.

## H001 — unrestricted low-treewidth lift

Assume a polynomial-time SAT decider exists. Run it on `F`.

- On YES, output the one-clause formula `(z)` and store the recovered witness.
- On NO, output `(z) AND (not z)`.

The output has constant treewidth and size. Therefore H001 follows immediately
from `P = NP`; conversely H001 gives a SAT algorithm. The statement is a
re-encoding of the target equality, not an independently constrained route.
H100 retains the useful local-treewidth idea while adding an explicit
potential-decreasing grammar and forbidding a global answer channel.

## H002 — unrestricted submodular lift

After deciding SAT, output a one-bit submodular function whose minimum is zero
on YES and one on NO. No structural property of the original CNF is used. Thus
the formulation does not isolate a submodular mechanism.

## H003 — unrestricted totally-unimodular lift

After deciding SAT, output either `0 <= 0` or `0 <= -1`. Both matrices are
trivially totally unimodular. The transformer has already done all semantic
work, so extension-complexity or integrality arguments cannot attack the exact
statement.

## H004 — unrestricted constant-level moment lift

After deciding SAT, output a constant-size polynomial system whose fixed
moment relaxation is feasible on YES and infeasible on NO. The degree bound
does not constrain the transformer that chose the system.

## H019 — untyped interface symbols

H019 counts interface nodes and exposed boundary *symbols*, but it never fixes:

- the allowed gate basis;
- the representation size of a symbol's denotation;
- the original-variable support of a node;
- whether a boundary symbol may denote a globally hard Boolean function;
- the exact composition semantics used by hash-consing.

One symbol can therefore hide the complete residual SAT function while still
counting as a constant-size boundary. The resource bound is not mathematically
well-defined. H102 repairs this by using explicit typed circuits and charging
full original-variable support.

## H070 — unrestricted theta compiler

Assume a polynomial-time SAT decider. After computing the answer, emit one of
two fixed constant graphs:

- a YES graph with `alpha = M`;
- a NO graph with a rational dual theta certificate below `M`.

Hence H070 is again equivalent to `P = NP` through solve-and-encode. The exact
H098 collision additionally proves that the ordinary first-level conflict-graph
route is incomplete, but it does not refute an arbitrary answer-dependent
compiler. H103 salvages the route by restricting the compiler to one fixed,
nonadaptive, bounded-radius signed-incidence transduction.

## Terminal interpretation

The graveyard status for all six entries is `REJECTED`, not `DESTROYED` as a
mathematical proposition. Their attack records use `DESTROYED` because the
registry's decisive-attack invariant denotes destruction of the exact active
formulation.

## Claim boundary

No step in this document proves `P != NP`, `P = NP`, or impossibility of every
restricted lift of the same broad type.
