# H104 — seeded arch-connected theta twins

## Status

`FORMALIZING`, reproducibility `R3`.

Seed `9379992` selects canonical bridge edges. Every mathematical condition is
then checked exactly; the seed is not probabilistic evidence.

## Base collision

Let `X_S` and `X_U` be the exact rational primal matrices from H098 for the SAT
and UNSAT graphs. Both have trace one and objective eight.

For `r` copies define

\[
X^{(r)}=\frac1r J_r\otimes X.
\]

Then

\[
\operatorname{Tr}(X^{(r)})=1,
\qquad
\langle J,X^{(r)}\rangle=8r,
\qquad
X^{(r)}\succeq0.
\]

The last property follows because both `J_r/r` and `X` are positive
semidefinite and the Kronecker product of PSD matrices is PSD.

## Seeded arch choice

For every ordered pair `(u,v)` with exact base entry `X[u,v]=0`, compute

```text
SHA256("9379992:<SIDE>:<u>:<v>")
```

and choose the lexicographically smallest digest.

On the SAT side, the eight vertices used by the independent-set witness are
excluded from the candidate set.

The frozen choices are:

```text
SAT    (31,22)
UNSAT  (22,13)
```

For consecutive copies `j` and `j+1`, add the edge joining local vertex `u` in
copy `j` to local vertex `v` in copy `j+1`.

Since the corresponding cross block of `X^(r)` is `X/r`, every new edge has
exact primal entry zero.

## Connectivity

Each base H098 graph is connected. One arch joins every consecutive pair of
copies, so the component graph is a path on `r` vertices. Therefore the full
arched graph is connected.

The executable artifact checks connectivity directly for the reproduced
fixtures.

## Dual upper bound

There are `8r` original clause cliques. Set the dual objective to `8r`, assign
multiplier `8r` to every intra-clause edge, and assign multiplier zero to every
complement edge and every new arch.

The slack is

\[
8r\,\operatorname{blockdiag}(J_{|C_1|},\ldots,J_{|C_{8r}|})-J.
\]

Writing `s_i` for the coordinate sum in clause block `i`, its quadratic form is

\[
8r\sum_{i=1}^{8r}s_i^2-\left(\sum_{i=1}^{8r}s_i\right)^2\ge0
\]

by Cauchy-Schwarz. Thus the dual gives `theta <= 8r`, while the primal gives
`theta >= 8r`.

Hence both connected arched graphs have exact theta value `8r`.

## Opposite alpha labels

### SAT side

In every copy choose the common positive `x4` occurrence from each of its eight
clauses. The seed selection excludes all these vertices, so no arch touches the
selected set. This gives an independent set of size `8r`.

Since `alpha <= theta = 8r`, equality follows.

### UNSAT side

Before arches, the disjoint union has independence number `7r`, because each
base component has exact alpha seven. Adding edges cannot increase independence
number. Therefore the arched UNSAT graph has

\[
\alpha\le7r<8r.
\]

## Reproduction

```bash
python experiments/theta/seeded_arches.py --self-test
```

Expected output includes:

```text
JANUS_SEEDED_ARCH_THETA_FAMILY = PASS
SEED = 9379992
SAT_ARCH = 31,22
UNSAT_ARCH = 22,13
CONNECTED_COPIES = 2
EXACT_THETA = 16
```

The test verifies exact rational primal and dual certificates for two connected
copies on both sides.

## Claim boundary

The added arches are graph edges. C014 does not yet prove that every arched
graph is the standard clause-literal conflict graph of a CNF obtained by a
local formula gadget. The result removes disconnectedness as a graph-level
explanation of the first-theta blind spot; it does not resolve higher theta
levels or P versus NP.
