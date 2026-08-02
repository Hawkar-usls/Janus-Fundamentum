# C020 addendum — nonlinear masking of an affine Tear

## Status

`EXPLORATORY / REPRESENTATION-DEPENDENCE ATTACK`

A component-parity Tear solves explicit Tseitin systems because their affine
structure is visible. This addendum tests whether an affine-only Tear extractor
survives a satisfiability-preserving change of representation.

## Original relation

Start from the incompatible pair

```text
x XOR y = 0
x XOR y = 1
```

An explicit affine recognizer detects both equations immediately and Gaussian
elimination rejects their conjunction.

## Bijective nonlinear mask

Use three new variables and the triangular transformation

```text
x = a
y = b XOR (a AND c)
c = c
```

The map is bijective. Given `(x,y,c)`, recover

```text
a = x
b = y XOR (x AND c).
```

After substitution, the two incompatible relations become

```text
a XOR b XOR (a AND c) = 0
a XOR b XOR (a AND c) = 1.
```

Each relation has a four-clause exact 3-CNF encoding. Their conjunction contains
eight clauses and remains UNSAT.

## Exact audit

```bash
python experiments/direct/janus_tear_nonlinear_affine_masking.py
```

The script exhaustively verifies:

```text
triangular mapping is bijective:   true
zero-relation witnesses:           4
one-relation witnesses:            4
conjunction witnesses:             0
relation is affine over GF(2):      false
```

The non-affinity test enumerates every affine Boolean function on three inputs
and compares its complete truth table.

## Result

An extractor limited to explicit affine/XOR structure is not invariant under
polynomial-size bijective nonlinear re-encodings. The global contradiction is
still present, but the specific affine language in which the compact Tear was
obvious has disappeared.

This does not refute a policy that can discover arbitrary nonlinear bijections,
perform semantic circuit reconstruction, or use another proof system. It places
the cost exactly there: a universal Tear policy must either

1. normalize representations through a provably polynomial semantic procedure;
2. search across increasingly expressive invariant languages;
3. or prove that one fixed language survives every allowed encoding.

Any normalization that silently solves formula equivalence, circuit recovery,
or SAT has merely moved the original problem into Tear extraction.

## Lift to a concrete policy

The same local mask is applied independently to every edge variable of a cubic
Tseitin graph in:

```bash
python experiments/direct/janus_tear_policy0a_masked_tseitin.py --self-test
```

Because cubic degree is fixed, every masked vertex relation has nine inputs and
an exact 256-clause CNF. The encoding therefore has constant overhead per vertex.
Policy-0A rejects visible `K4` with zero branch states but visits 3,842 exact
residual states on the masked instance. The masked `K3,3` instance exceeds the
explicit quadratic state envelope.

This remains a finite policy falsification rather than an asymptotic lower bound.
