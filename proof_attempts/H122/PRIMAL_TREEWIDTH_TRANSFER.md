# H122 — primal graph and treewidth transfer

## Status

`FORMALIZING`, reproducibility `R2`.

This artifact isolates the graph-theoretic step used by H121.

## Primal graph equals a line graph

Let `G` be the graph underlying a standard edge-variable Tseitin formula.
Every edge `e` of `G` becomes a Boolean variable `x_e`.

At a graph vertex `v`, the local parity equation is encoded by clauses whose
variable set is exactly

\[
\{x_e:e\ni v\}.
\]

For degree four, every local clause contains all four incident variables.
Therefore every two incident graph edges co-occur in a clause and are adjacent
in the CNF primal graph.

Conversely, every clause belongs to one vertex equation and contains only
variables for edges incident with that vertex. Nonincident graph edges never
co-occur.

Hence

\[
\operatorname{Primal}(\operatorname{Tseitin}(G,c))=L(G),
\]

independently of the charge vector `c`.

The executable artifact constructs both edge sets and requires exact equality.

## General line-graph lower bound

Harvey and Wood record the elementary relation

\[
\operatorname{tw}(L(G))
\ge
\frac{\operatorname{tw}(G)+1}{2}-1.
\]

It follows by taking a tree decomposition of `L(G)` and replacing every line
graph vertex—an edge of `G`—by its two endpoints, producing a decomposition of
`G` with bags at most twice as large.

## Toroidal substitution

For the square toroidal grid `T_m`, Gima, Morimoto, Okada, and Otachi prove

\[
\operatorname{tw}(T_m)=2m-1
\]

for every `m >= 5`.

Substitution yields

\[
\operatorname{tw}(L(T_m))
\ge
\frac{(2m-1)+1}{2}-1
=m-1.
\]

H121 uses two disjoint copies. Treewidth of a disjoint union is the maximum of
its component treewidth, so the lower bound remains `m-1`.

## Input-size relation

One torus has `m^2` graph vertices and `2m^2` edge variables. Two copies give

\[
N=4m^2
\]

formula variables. Thus

\[
m-1=\Omega(\sqrt N).
\]

This is asymptotically larger than every `O(log N)` output-width target in
H106.

## Reproduction

```bash
python experiments/direct/toroidal_tseitin_twins.py --self-test
```

The executable checks the finite primal-line-graph identity. The asymptotic
width inequality relies on the committed primary references R070 and R071.

## Claim boundary

A high-treewidth input does not stop a compiler from producing a different
low-treewidth equisatisfiable output. H122 only closes the identity-compiler
escape that invalidated H115.
