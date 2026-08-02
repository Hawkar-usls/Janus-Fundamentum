# H102 — refutation by direct d-DNNF transfer

## Terminal status

`DESTROYED` by attack `A331`.

The result concerns the exact H102 syntax. It does not rule out interface
circuits that allow support overlap, nondeterministic OR, hidden projection, or
another operation outside d-DNNF.

## H102 output syntax

H102 requires every compiled object to be an explicit Boolean circuit over
named original variables with:

1. complete original-variable support stored and charged at every interface;
2. AND children having disjoint support;
3. OR children having certified disjoint satisfying alternatives;
4. polynomial total circuit size;
5. exact equivalence to the input CNF and witness recovery.

No existential projection of fresh variables appears in the output semantics.

## Gate-by-gate translation

Put the circuit in negation normal form by keeping negation only at literal
leaves, as already required by its typed Boolean interface interpretation.

### AND gates

For an AND gate

\[
g=g_1\land\cdots\land g_t,
\]

H102 records pairwise disjoint original-variable supports. Therefore the gate
is decomposable in the standard DNNF sense.

### OR gates

For an OR gate

\[
g=g_1\lor\cdots\lor g_t,
\]

H102 requires certified deterministic alternatives: no assignment satisfies
two different children. Therefore the gate is deterministic in the standard
d-DNNF sense.

### Leaves and size

Leaves are literals or constants over named original variables. The
translation does not introduce gates. Thus an H102 output with `s` gates is a
d-DNNF with `s` gates up to a constant encoding factor.

## Contradiction

H102 asserts polynomial-size output for every CNF. The translation above would
therefore produce polynomial-size d-DNNFs for every CNF.

The explicit families already cited by JANUS for H016 and H061 have
unconditional exponential DNNF lower bounds. Since H102 has no auxiliary
projection loophole, those lower bounds apply directly.

Hence the universal polynomial compiler claimed by H102 cannot exist.

## Why this differs from H019

H019 survived direct compilation lower bounds only because its interface-node
language was undefined and could hide arbitrary denotations. H102 repaired that
problem by making supports and gate semantics explicit. That repair made the
model falsifiable—and placed it exactly inside d-DNNF.

## Salvage

A descendant must use and charge at least one resource outside this transfer:

- overlapping AND supports;
- nondeterministic OR alternatives;
- an explicit projection operation;
- or a different composition primitive.

Merely renaming H102 interface nodes does not escape the lower bound.

## Claim boundary

This refutation does not prove `P != NP`. It eliminates one universal compiler
architecture using an existing unconditional representation lower bound.
