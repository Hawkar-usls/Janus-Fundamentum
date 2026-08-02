# H096 — exact finite level-one theta collision

## Status

Constructive witness found in C013. The result is machine-checkable at R3 but is
not promoted to repository status `PROVED` until independent review.

## The UNSAT formula

Let

\[
U=\bigwedge_{a\in\{\pm1\}^3}
(a_1x_1\lor a_2x_2\lor a_3x_3),
\]

where a negative coefficient means a negated literal. These are all eight
possible width-three clauses on three variables. Every Boolean assignment
falsifies exactly one of them, hence `U` is unsatisfiable. Its conflict graph
has 24 literal-occurrence vertices, clause target 8, and exact independence
number 7.

## The SAT formula

Let

\[
S=\bigwedge_{a\in\{\pm1\}^3}
(x_4\lor a_1x_1\lor a_2x_2\lor a_3x_3).
\]

The assignment `x4 = true` satisfies all eight clauses. Its conflict graph has
32 vertices, clause target 8, and exact independence number 8.

## Exact primal certificate for U

The signed-coordinate automorphism group has 48 elements and 12 orbits on
unordered vertex pairs. In deterministic representative order

```text
(0,0), (0,1), (0,3), (0,4), (0,5), (0,9),
(0,10), (0,12), (0,15), (0,17), (0,21), (0,22)
```

the Gram entries are

```text
1/24, 0, 1/36, -1/144, 1/48, 1/72,
1/72, 0, 0, 1/36, 0, 1/48.
```

The resulting rational matrix `X_U` satisfies exactly:

- `Tr(X_U) = 1`;
- every graph-edge entry is zero;
- `<J, X_U> = 8`;
- `X_U` is positive semidefinite.

Its exact spectrum is

\[
\frac13^{\times1},\quad
\frac16^{\times3},\quad
\frac1{18}^{\times3},\quad
0^{\times17}.
\]

The executable artifact does not trust this displayed spectrum; it constructs
and verifies an exact rational permuted `LDL^T` certificate.

## Exact primal certificate for S

Choose the positive `x4` occurrence in each clause. Put `1/8` in every entry of
the resulting 8 by 8 selected principal block and zero elsewhere. This rank-one
matrix has trace 1, objective 8, and zero on every conflict edge.

## Common exact dual certificate

For either graph, assign multiplier 8 to every edge joining two occurrences in
the same clause and multiplier 0 to every complementary-literal edge between
clauses. With eight clause blocks, the dual slack is

\[
8\,\operatorname{blockdiag}(J_{|C_1|},\ldots,J_{|C_8|})-J.
\]

For any vector `z`, writing `s_i` for the coordinate sum in clause block `i`,

\[
z^TSz=8\sum_{i=1}^8s_i^2-\left(\sum_{i=1}^8s_i\right)^2\ge0
\]

by Cauchy-Schwarz. The code again verifies an exact rational `LDL^T`
certificate rather than relying on this prose argument.

Thus both graphs have exact Lovasz theta value 8, while their exact alpha labels
relative to target 8 are opposite.

## Reproduction

```bash
python experiments/theta/complete_3cnf_collision.py --self-test
```

Expected headline:

```text
JANUS_COMPLETE_3CNF_THETA_COLLISION = PASS
```

The existing collision verifier recomputes both independence numbers
exponentially and verifies both exact primal-dual theta bundles.

## Consequence

This constructively discharges the existential core of H096. Combined with a
formal proof of theta additivity under disjoint union, it yields an explicit
infinite SAT/UNSAT family invisible to the standard first Lovasz-theta level.

## Claim boundary

This is not a solution of P versus NP. It proves only a limitation of one
standard level-one SDP relaxation on one explicit pair and its disjoint-union
amplifications. Novelty has not been assessed.
