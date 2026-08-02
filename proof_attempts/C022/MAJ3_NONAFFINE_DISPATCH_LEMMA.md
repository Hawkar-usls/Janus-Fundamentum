# C022 lemma — MAJ3 lift disables the visible affine dispatcher

## Statement

Let a base Tseitin vertex have degree `d >= 1` and charge `c`. Replace every
incident edge variable by an independent `MAJ3` gadget. The resulting local
relation is

```text
R_{d,c} = {
  z in {0,1}^{3d} :
  XOR_{i=1}^d MAJ3(z_{i,1},z_{i,2},z_{i,3}) = c
}.
```

Then `R_{d,c}` is not an affine subset of `F_2^{3d}` for either charge.
Consequently the exact-scope detector used by Policy-0T returns `None` on every
complete MAJ3-lifted Tseitin CNF whose clauses are grouped by these local vertex
scopes.

## Lemma 1 — both MAJ3 fibres are non-affine

The fibres are

```text
MAJ3^{-1}(0) = {000,001,010,100},
MAJ3^{-1}(1) = {111,110,101,011}.
```

An affine subset of a vector space is closed under the ternary operation

```text
x xor y xor z.
```

For the zero fibre:

```text
001 xor 010 xor 100 = 111,
```

which is outside the fibre.

For the one fibre:

```text
110 xor 101 xor 011 = 000,
```

which is outside the fibre.

Thus both fibres are non-affine.

## Lemma 2 — every parity-of-MAJ3 relation is non-affine

Fix arbitrary assignments to gadget blocks `2,...,d`. Their MAJ3 outputs have
some parity `p`. Under this coordinate restriction, membership in `R_{d,c}`
requires the first block to satisfy

```text
MAJ3(block_1) = c xor p.
```

The restricted relation is therefore exactly one of the two non-affine MAJ3
fibres.

Every coordinate restriction of an affine relation is affine or empty. The
slice above is nonempty and non-affine. Hence `R_{d,c}` itself cannot be affine.

## Detector consequence

The Policy-0T detector groups a complete exact-relation CNF by its full variable
scope and reconstructs the allowed truth-table rows. It marks a group affine
only when the rows are exactly the solution set of all discovered linear
equations.

For a MAJ3-lifted Tseitin vertex, the reconstructed rows are `R_{d,c}`. By Lemma
2 the affine-equation routine returns `None`. Since every local vertex block is
non-affine, the detector does not cover all input clauses and returns

```text
affine_answer = None.
```

This holds uniformly for every graph with no isolated vertices, independently
of expansion or charge placement.

## Executable audit

```bash
python experiments/direct/janus_tear_maj3_nonaffine_family_audit.py
```

The audit exhausts both charges for degrees one through four. The general result
is supplied by the fibre-slice proof above.

## Claim boundary

This lemma concerns the exact current visible-affine detector and the complete
local truth-table encoding of the MAJ3 lift. A stronger semantic affine detector
or a different encoding with additional exposed parity variables would require
a separate analysis.
