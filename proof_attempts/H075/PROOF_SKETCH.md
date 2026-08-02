# H075 — proof sketch under attack

## Claim

Coordinate permutations and coordinate complementations `x_i -> 1-x_i` preserve theta rank for finite Boolean varieties and transport fixed-level theta certificates without changing degree.

## Sketch

Let `phi` be the polynomial-ring automorphism induced by a coordinate permutation and optional complementations. It has an inverse of the same form and maps Boolean relations `x_i^2-x_i` to Boolean relations.

Suppose a linear polynomial `f` is `k`-sos modulo an ideal `I`:

```text
f - sum_j h_j^2 belongs to I,
with deg(h_j) <= k.
```

Applying `phi` gives:

```text
phi(f) - sum_j phi(h_j)^2 belongs to phi(I).
```

Permutations and complementations do not increase total degree, so every `phi(h_j)` still has degree at most `k`. Applying `phi^{-1}` proves the converse. Thus the set of linear polynomials certified at level `k` is transported bijectively, and exactness occurs at the same first level.

The substitutions use only coefficients in `{0,1,-1}`. Expanding a complemented monomial can increase the number of terms, but for fixed degree the bit length and representation size remain polynomially related. A complete proof must state the representation convention and quantify this expansion.

## Boundaries

This sketch does **not** cover:

- XOR substitutions over `GF(2)`, which become higher-degree expressions in real `0/1` coordinates;
- existential projection or forgetting variables;
- nonfunctional auxiliary extensions;
- arbitrary affine maps that do not preserve the Boolean cube.

## Status

`FORMALIZING`, not `PROVED`. The next step is a complete quotient-ring statement and an independently checked coefficient-size proof.
