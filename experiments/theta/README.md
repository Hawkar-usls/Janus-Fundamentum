# Theta inversion experiments

This directory starts the reproducible side of C008.

## Seed reduction

`conflict_graph.py` implements the standard clause-literal conflict graph for a DIMACS CNF:

- one vertex per literal occurrence;
- edges join vertices from the same clause;
- edges also join complementary literals;
- a formula with `m` clauses is satisfiable exactly when the graph has an independent set of size `m`.

For a small fixture:

```bash
python experiments/theta/conflict_graph.py example.cnf --exact-alpha
```

`--exact-alpha` uses exponential branch-and-bound and is only a correctness fixture. It is not a SAT algorithm and does not compute the Lovasz theta number.

## Planned theta profile

The next executable layer will record, with exact solver/version metadata:

- graph encoding hash;
- first-level Lovasz theta value;
- primal and dual residuals;
- rationalized certificate size;
- bounded theta-body or SoS level;
- moment-matrix dimension;
- result before and after certified affine elimination.

The first target families are small Tseitin, pigeonhole, random 3CNF, and mixed XOR/non-affine instances derived from H053, H062, and H072.

## Claim boundary

Numerical SDP output is not a mathematical certificate by itself. No finite theta profile proves an asymptotic complexity statement. H070-H074 remain open hypotheses under attack.
