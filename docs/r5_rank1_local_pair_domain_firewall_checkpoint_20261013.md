# R5 — Rank-one Klein-four pair-domain firewall (all-n theorem, complete n8 control)

Date: 2026-10-13.  
Executable: [r5_kempe_rank1_pair_domain_firewall.py](../experiments/r5_kempe_rank1_pair_domain_firewall.py).  
Dependencies: [minimum port rank and two-colouring obstruction](r5_min_port_rank_rigidity_checkpoint_20261013.md), [saturation and fibre uniformity](r5_kempe_sixpole_saturation_or_forbidden_proof_20261013.md).

## Corrected scientific scope

The theorem below is for connected cubic sixpoles with six distinct ordered physical roots. It does NOT prove that every candidate has a low-dimensional `Z_s`, nor a universal absence of Exact-One sixpoles, an unbounded PC lower bound, or polynomial `SolveLinearCubicXSAT`.

## Theorem: polynomial local exclusion of a rank-one fibre pair

Choose any proper cubic sixpole M and ordered physical six-port tuple s. Let `Z_s` be the previously defined space of zero-divergence Klein-four edge-differences with boundary-colour root constraints, computed by a binary matrix.

If `dim Z_s=0`, there is at most one full proper internal 3-edge-colouring extending s.

Now suppose `dim Z_s=1`, and let `D != 0` be its uniquely determined nonzero member. If two distinct proper full colourings `c,c'` extend s, then `D_e=c_e XOR c'_e` on every ordinary edge. Use nonzero `F2^2` labels `1,2,3` for colours 0,1,2.

For each vertex v, enumerate the at most SIX local permutations of `(1,2,3)` assigning its three ordinary edges/semiedges the three distinct colours. At each external root its semiedge is fixed to s. Retain only assignments for which `c_e != D_e` on every ordinary edge incident to v. Because `partial D=0` and the original local colours have xor sum zero, this condition guarantees that the updated local triple `c_e XOR D_e` is also a proper three-colour triple.

For ordinary edge e=uv, form the set `L_v(e)` of its possible first-colouring labels among retained local assignments at v, and similarly `L_u(e)`. If

```
L_u(e) INTERSECT L_v(e) = EMPTY
```

for any e, no two distinct full proper 3-edge-colourings extending s can exist. This is a **sound sufficient polynomial certificate** independent of finding any actual full colouring; the local choices are bounded by six per vertex and the binary rank-one vector D is found by Gaussian elimination.

The absence of an edge-domain contradiction proves nothing: the global proper-colouring CSP may still be incompatible.

## Corollary: global GOOD-only forces singleton fibres when one such certificate exists

Assume additionally that `Bits(M) subset {100,010,001}`, and let b be a truth bit that actually occurs. The previously proved forced Kempe connectivity gives 36 full physical tuples of bit b with uniform positive fibre size `m_b`. If **any one** tuple s of bit b has either `dim Z_s=0` or `dim Z_s=1` plus the local empty-intersection conflict, then `m_b=1`, so the entire bit-b forced Kempe monodromy is trivial.

Without the global GOOD-only assumption, if TWO different actual full proper colourings of M share an allowed tuple t of bit b, then one can **construct** a forbidden full colouring in polynomial time by choosing a <=4-step forced Kempe path t->s and attempting to lift it from each input. If both lifts exist, invertibility produces two distinct full colourings of the capacity-one target s, contradiction. At the first wrong actual pair matching, switching a subset of at most three disjoint two-colour terminal paths yields the required full forbidden witness. The total number of path interchanges is at most six.

## Explicit n8 rank-one counterexample control

Take the following nine ordinary edges of a simple connected cubic sixpole, in this fixed order, with semiedges rooted at vertices 0..5:

```
e0=(2,3), e1=(4,6), e2=(5,7),
e3=(0,1), e4=(3,5), e5=(6,7),
e6=(0,6), e7=(1,7), e8=(2,4).
```

With physical port tuple `t=(0,0,1,2,1,2)` (bit `100`), it admits at least these two distinct full internal colourings:

```
c = (0,0,0,1,1,1,2,2,2),
c'=(0,0,0,2,1,2,1,1,2).
```

For the different allowed same-bit tuple `s=(0,0,0,2,0,2)`, the binary flow-difference matrix has rank deficiency exactly 1. Its nonzero difference on the nine ordered edges is

```
D=(0,0,0,1,0,1,1,1,0)
```

in Klein-four labels. At vertex 6 the incident D labels are `(0,1,1)`, forcing the unchanged edge `e1=(4,6)` to carry *first-colouring* label **1**. But at root vertex 4 the semiedge colour is 0 (=Klein-four label 1), so the internal edge `e1` can carry only labels **2 or 3**. Thus

```
L_6(e1)={1}, L_4(e1)={2,3}, intersection=empty.
```

This is a tiny, independently checkable graph- and boundary-relative **pair exclusion certificate**. Starting from the second full colouring `c'`, flipping its actual (0,1)-Kempe path ending at outer ports (1,2) yields a full proper colouring with boundary `(0,1,0,2,1,2)`, bits `000`, a directly checkable forbidden witness. Notice that this does not exclude all n, just the proposed global GOOD-only status of this particular graph.

## Exhaustive n8 finite profile

The n8 test enumerates `15^3=3375` triples of ordinary colour-class perfect matchings, retaining 1,472 labelled connected simple reference-coloured sixpoles with fixed physical tuple `001212`. It independently counts their full-colouring fibre over that tuple. For each graph it evaluates all 36 parity-legal same-bit tuples and tests the rank-zero or rank-one edge-domain capacity-one certificates.

| Number of full colourings over 001212 | Minimum boundary rank | Configurations | At least one pair-capacity-one certificate? |
| ---: | ---: | ---: | --- |
| 1 | 0 | 1,104 | YES |
| 1 | 1 | 208 | YES |
| 2 | 0 | 112 | YES — pure rank0 |
| 2 | 1 | 48 | YES — rank1 edge conflict |
| **Total** | | **1,472** | |

**Finite inference:** All 160 starting reference configurations with two distinct full colourings over `001212` have a polynomially checkable witness that their graph cannot satisfy the *global* GOOD-only boundary relation. This is **not** a universal all-n gadget no-go; no bound on all future dimensions `dim Z_s` was established.

## Next real barrier

Prove for an arbitrary hypothetical connected simple cubic sixpole with globally GOOD-only Exact-One boundary relation that some allowed boundary state has pair capacity ≤1, **and** independently prove that every exact-one gadget must have a physical boundary fibre of size ≥2; OR identify a stronger global physical cross-colour consistency condition that handles high-rank spaces and excludes all such sixpoles. Neither proposition is currently proved, and neither can be inferred from this finite result.

The bigger goal `SolveLinearCubicXSAT` remains NOT CONSTRUCTED and P vs NP OPEN. This work concerns a potential gadget obstruction, not an NP-complete solver.
