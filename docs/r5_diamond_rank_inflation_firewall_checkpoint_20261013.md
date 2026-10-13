# R5 — Diamond rank-inflation theorem and mandatory irreducible-core normalization

Date: 2026-10-13.  
Verification executable: [r5_kempe_diamond_unbounded_rank_inflation_firewall.py](../experiments/r5_kempe_diamond_unbounded_rank_inflation_firewall.py).

## All-size theorem: exact physical colour signature, unbounded algebraic rank

Let `G` be any connected simple cubic sixpole with six labelled semiedges attached to distinct roots, and let `e=(u,v)` be an ordinary internal edge. Replace `e` with a fresh connected four-vertex Diamond 2-pole `B=K4\{a,b}`, attaching its two dangling ends to old endpoints u and v. Call the result `G'`. The new graph is simple, connected and cubic.

### Physical boundary signature

The 2-pole `B` is properly three-edge-colourable, its two exposed semiedge colours must be equal by parity, and S3 colour relabellings give all three common values. Thus

```
Col6(G') = Col6(G)
```

as full sets of **ordered physical six-port colour tuples**; multiplicities of full interior colourings are not claimed equal.

### Difference-flow rank

Fix an *arbitrary* prescribed ordered external six-port colour tuple `s`, whether physically realizable or not. Let `Z_s(G)` be the `F2` vector space of `F2^2`-labelled zero-divergence flows on ordinary internal edges of `G`, with extra one-dimensional root constraints `D_e in span(s_i)` for the edge incident to each physical semiedge root i. This is the previously introduced *linear envelope*, not the set of proper 3-colourings.

There is a natural surjective `F2`-linear map `T:Z_s(G')->Z_s(G)`: for an expanded flow D, sum zero divergence over the four new Diamond vertices. The two attachment-edge flow labels are equal; collapse these to the single old label on e, keeping every other edge flow unchanged.

**Surjectivity.** For any original difference-flow, replace its value `D_e` on e by that same label on the path `u-a-c-b-v`, and assign zero to the other new internal Diamond edges. This gives an expanded zero-divergence flow. All old root line constraints remain identical.

**Kernel.** When the old collapsed flow vanishes, the attachment-edge labels vanish and the remaining flows are the unconstrained cycle-flow space on the five internal edges of the four-vertex connected graph `K4\{a,b}`. Its ordinary binary cyclomatic rank is `5-4+1=2`. Over the two-dimensional Klein-four vector space, the kernel therefore has dimension exactly `2*2=4`.

The rank-nullity theorem yields

```
dim_F2 Z_s(G') = dim_F2 Z_s(G) + 4
```

for every tuple s, without a proper-colouring witness. By k repeated Diamond inflations:

```
Col6(G_k) = Col6(G);
dim Z_s(G_k) = dim Z_s(G) + 4k;
|V(G_k)| = |V(G)| + 4k.
```

This is a universal **negative control**: large or unbounded raw `dim Z_s` by itself does not prove a hard, irreducible or unusually expressive sixpole. Any physical-signature no-go argument based on small flow-fibre envelopes must first contract all legitimately reducible 2/3-edge blocks, and then treat the remaining 4-edge blocks using the previously proved 11-class semantic atlas when applicable.

The theorem is compatible with the fact that `|Fibre(s)| <= 2^dimZ_s` is only an upper bound. The additional 4 dimensions in the *linear envelope* may be spurious relative to actual nowhere-zero edge colourings, and do not create new outer colour states.

## Regression

The new verifier constructs `C6` and inserts up to three successive 4-vertex Diamond 2-poles, giving graph orders 6,10,14,18. For **all 729** ordered three-colour port tuples (including tuples violating parity and not physically attainable) it asserts an exact +4 rank increase per inflation. Separately, it exhaustively enumerates all proper full-colouring physical six-port tuple sets and asserts complete equality with the 63-state original C6 relation at each size.

The fixed initial and constructed graph controls give, for the 36 parity-legal tuples of bit 100, rank minima:

| Internal vertices | Diamonds inserted | min(dim Z_s), bit100 | Physical tuple count |
| ---: | ---: | ---: | ---: |
| 6 | 0 | 0 | 63 |
| 10 | 1 | 4 | 63 |
| 14 | 2 | 8 | 63 |
| 18 | 3 | 12 | 63 |

The numerical checks validate the implementation; the all-size theorem rests on the explicit exact sequence of linear spaces, not on these four finite examples.

## Next universal target and open gates

A productive universal attack must characterize **reduction-invariant** physical constraints on the minimal irreducible core: in particular, how all 22 residual mixed-colour Kempe loops interact when their candidate flow displacements are constrained by actual shared cubic vertices, rather than allowing arbitrary abstract cover permutations.

No uniform upper bound on post-reduction rank has been established; high-rank, >4-edge-connected residual structures remain OPEN. Neither the complete Exact-One-gadget impossibility, nor a native PC lower bound, nor a polynomial general `SolveLinearCubicXSAT` follows. P vs NP is OPEN.

**CI:** script and the workflow entry are committed to a research branch; await actual status evidence before writing SUCCESS.
