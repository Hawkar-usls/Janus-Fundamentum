# H018 formulation failure — the registered statement is vacuous

## Claim attacked

H018 bounds the number of certified residual classes explored by an algorithm `Q` and requires witness recovery from every accepting quotient path.

## Missing obligation

The statement does not require that:

1. `Q` covers every assignment represented by the original formula;
2. `Q` has an accepting path whenever the formula is satisfiable;
3. `Q` rejects whenever the formula is unsatisfiable; or
4. `Q` returns any decision at all.

## Vacuous countermodel

Define `Q₀` to inspect only the root residual and halt without creating an accepting path.

- It has one residual class at depth zero and zero classes afterward.
- Its canonicalization cost is constant.
- The condition “a satisfying assignment is recoverable from any accepting path” is vacuously true because there are no accepting paths.

Thus `Q₀` satisfies the explicit width, time, and witness clauses as written, but does not decide SAT. Therefore the advertised consequence does not follow from the registered statement.

## Verdict

H018 is rejected as an incomplete formulation, not refuted as a fully specified mathematical conjecture. A valid descendant must include a coverage invariant and two-sided correctness:

- every represented assignment is covered by the quotient DAG;
- an accepting terminal exists iff the input is satisfiable;
- rejection is certified for unsatisfiable inputs;
- the complete construction and all certificates are polynomially bounded.
