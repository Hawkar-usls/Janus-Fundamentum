# H100 — formulation failure

## Terminal status

`REJECTED` by attack `A332`.

This rejects the exact research formulation, not the broad possibility that a
properly restricted local compiler could reduce treewidth.

## Intended repair

H100 attempted to repair two failures:

- H001 allowed an unrestricted solve-and-encode transformer;
- H009 allowed an iterated local system that might simulate a global
  polynomial-time computation.

It added a strictly decreasing locally computable potential and stated that no
rule could inspect or encode a global acceptance bit.

## Why the repair is not formal

The statement does not define:

- the representation on which the potential is local;
- the radius and syntax used to compute the potential;
- whether the potential is a sum of local terms or an arbitrary polynomial-bit
  annotation;
- what constitutes an encoded acceptance bit;
- how indirect global state, clocks, counters, or work-tape symbols are
  excluded.

A finite local rewrite system can simulate a Turing-machine space-time history.
A clock-like component can decrease at every step while the remaining local
state performs the computation. The final local rule need not contain a field
literally named `accept`; it can still emit one of two target structures after
the simulated computation halts.

Therefore strict decrease alone does not prevent solve-and-encode, and the
phrase forbidding a global answer channel has no machine-checkable criterion.

## Why terminal rejection is appropriate

A hypothesis must have stable falsification semantics. For H100, an alleged
counterexample can always be disputed by changing what counts as a legal
potential or encoded answer channel, while a proposed compiler can always hide
state in an unspecified annotation language.

This is a formulation failure rather than a theorem that all potential-based
rewrite systems are impossible.

## Salvage in H106

H106 removes the ambiguous concepts and fixes:

- exactly `q` synchronous passes for constant `q`;
- bounded rewrite radius `r`;
- radius-`qr` ancestry for every output symbol;
- no persistent adaptive scheduler or unbounded work tape.

Those restrictions are severe, but they define a falsifiable class and expose a
clear locality lower-bound target.
