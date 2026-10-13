# R5 checkpoint — real cross-colour 5-loop holonomy and binary cycle-space constraint

Date: 2026-10-13. Research branch: `research/r5-kempe-coupled-involutions-20261013`.

## Status

A real finite graph witness shows that the **unconditional** identity "every liftable 5-step forced boundary loop acts trivially on the full edge-colouring" is FALSE. The witness is **not** a genuine Exact-One gadget: forbidden boundary bits also occur in its complete colour relation. The all-size exclusion of exact-one sixpoles is OPEN.

Executable: [physical 5-loop witness / flow audit](../experiments/r5_kempe_physical_fiveloop_gf4_flow_witness.py). Previous abstract control: [F22 monodromy](r5_kempe_monodromy_rank22_checkpoint_20261013.md).

## Exact finite physical witness

Use 8 labelled internal vertices 0,...,7, with one physical semiedge at each vertex 0,...,5, and ordered semiedge colours `s=(0,0,1,2,1,2)`. The unordered interior edges **in this fixed order** are:

```
e0=(2,4), e1=(3,6), e2=(5,7),
e3=(0,1), e4=(3,5), e5=(6,7),
e6=(0,2), e7=(1,6), e8=(4,7).
```

Before: `c=(0,0,0,1,1,1,2,2,2)`. It is a proper edge-3-colouring: each vertex has one incident edge/end of each colour; the graph is simple and connected.

The following five **real** alternating terminal-path flips (colour pair, ordered physical semiedge endpoints) are all possible on this one fixed graph, with intermediate physical tuples:

| Step | Colour pair | Terminal endpoints | Boundary after flip |
| --- | --- | --- | --- |
| 1 | (0,1) | (0,1) | 111212 |
| 2 | (0,1) | (2,4) | 110202 |
| 3 | (1,2) | (0,1) | 220202 |
| 4 | (0,1) | (2,4) | 221212 |
| 5 | (0,2) | (0,1) | 001212 |

The boundary tuple returns to its starting value, retaining bit 100, yet the final full interior colouring is

`c'=(0,1,1,1,0,0,2,2,2)`.

The changed edges are `e1,e2,e4,e5`; these form a genuine interior quadrilateral `3-6-7-5-3`. Their colours 0 and 1 are interchanged. This yields a physically realised **nontrivial** monodromy lift of the specified boundary five-cycle.

Independent DFS over all interior 3-edge-colour assignments with fixed boundary `001212` finds exactly TWO full proper colourings: `c,c'`. **Important:** starting from `c'`, the identical prescribed boundary five-cycle does *not* lift fully. This is a *partial lift* in a graph admitting forbidden states; it is NOT a two-sheeted regular cover over the forced 36-state GOOD-only base.

## Full small-n finite cross-check

Fix the same physical boundary `001212` with one semiedge at each of six distinct roots. Three colour-class matchings each cover six eligible vertices and have 15 possibilities; independently enumerate `15^3 = 3375` labelled reference configurations. Remove any with repeated ordinary edges or disconnected underlying graph.

Counts of the **1,472** surviving simple connected proper coloured eight-vertex sixpoles, using the exact five-step prescribed boundary path:

| Class | Count |
| --- | ---: |
| Cannot lift all five prescribed terminal-path flips | 1,280 |
| Can lift and return to exactly original full internal colouring | 160 |
| Can lift and return to same physical boundary but DIFFERENT full internal colouring | 32 |
| **Total** | **1,472** |

These counts describe labelled *starting reference colourings*, NOT 1,472 nonisomorphic graphs, and are finite observations. The explicit witness above belongs to the 32 nontrivial instances.

### Second physical witness: nontrivial holonomy without short cycles

Exactly 16 of the 32 nontrivial lifts differ on an alternating internal 4-cycle in a graph of girth 4. The other **16** change all nine internal ordinary edges of a graph whose ordinary-edge girth is **6**. In particular, forbidding triangles and quadrilaterals does not guarantee the boundary 5-loop acts trivially.

An explicit second witness has the following ordered ordinary edges (again indexed by colour classes 0,1,2 in three blocks):

```
(2,4), (3,6), (5,7),
(0,6), (1,7), (3,5),
(0,1), (2,6), (4,7).
```

With the SAME starting port tuple `001212` and starting internal colours `000111222`, the SAME five terminal-path flips listed above give

`c'=(2,1,1,2,2,0,1,0,0)`

with exactly the same physical boundary tuple. Every one of its nine ordinary edge colours differs, and the resulting `F2^2` displacement is a closed (Kirchhoff) circulation. Direct DFS again finds exactly two full colourings with those fixed six port colours. The difference support is the entire internal edge set, not a monochromatic or bichromatic short cycle.

**Caution:** Girth 6 is only the girth of the internal ordinary-edge graph. This does not make the witness a globally GOOD-only Exact-One sixpole; it is still a necessary negative control only.

## Theorem — all-size GF(2)^2 cycle-space confinement of colour-fibre holonomy

Represent the three edge colours by the three nonzero group elements `1,2,3` of `F2^2` (bitwise XOR). At every cubic vertex the three incident colours xor to zero: `1 XOR 2 XOR 3 = 0`. A full properly coloured cubic sixpole is equivalently a nowhere-zero Klein-four flow with six labelled semiedges.

Let two **full** proper 3-edge-colourings `c,c'` of the same graph have the same ordered physical six-port tuple. Define an `F2^2` label on each ordinary internal edge by

```
D_e = code(c_e) XOR code(c'_e).
```

At any internal cubic vertex, xor of incident differences equals xor of the three colours of `c` plus xor of the three colours of `c'`, hence zero. Every physical semiedge has difference zero because the boundary tuples coincide. Therefore `D` is a **zero-boundary group-valued circulation** on the internal edge set:

```
partial(D) = 0 over F2^2.
```

For a connected sixpole with `n` internal cubic vertices and exactly six semiedges, the number of ordinary internal edges is `m=(3n-6)/2`. Their ordinary-edge graph remains connected by hypothesis and has binary cycle rank

```
beta = m-n+1 = (n-4)/2.
```

Thus all same-boundary colour differences lie in the vector space

```
H_1(G_interior; F2^2) ~= (F2)^(2 beta) = (F2)^(n-4).
```

Choosing one full colouring `c_0` in a fixed physical boundary fibre, mapping `c -> c XOR c_0` is injective into that common vector space, implying the **all-size bound**

```
|Fibre(s)| <= 2^(n-4).
```

Here `Fibre(s)` counts complete **proper** internal edge-colour assignments extending precisely the physical six-port tuple s. The bound is exponential in n, and does not solve colouring or native SCL. Crucially, it is NOT legitimate to assume a closed boundary Kempe loop acts as a fixed translation independent of its starting full colouring; its displacement vector can depend on the starting colouring.

The witness above realises a nonzero circulation `D` supported on the 4-cycle `3-6-7-5-3`. This is the **physical** source of its nontrivial five-loop displacement.

## Stronger polynomial linear envelope of a fixed physical boundary fibre

For six **distinct** semiedge roots and a fixed proper external colouring `s`, we have more than the generic cycle-space bound. At root `v_i` with external colour `a_i`, two internal edge colours must be the other two nonzero `F2^2` group elements. Between two full proper extensions of **the same** `s`, they either stay fixed or exchange; hence the difference labels on BOTH internal incident edges obey

```
D_e = D_f in span_F2(a_i) = {0, a_i}.
```

Let `Z_s` be the `F2`-linear subspace of ordinary-edge `F2^2` flows satisfying (i) Kirchhoff conservation at every vertex and (ii) one boundary-colour line constraint at each semiedge root. It is constructed directly from graph incidence and the six external colours **without** enumerating internal colourings; Gaussian elimination computes `d_s = dim(Z_s)` in polynomial time.

For any chosen full proper reference colouring extending `s` (when one exists), every other colouring in the fibre gives a UNIQUE `D in Z_s`. Thus

```
|Fibre(s)| <= 2^(d_s) <= 2^(n-4).
```

In particular, if `d_s=0` and a full reference colouring is already supplied, the fibre contains **exactly one** internal colouring. The bound alone gives no proof that the fibre is nonempty for arbitrary input.

New [independent fixed-port envelope verifier](../experiments/r5_kempe_fixed_port_gf4_linear_envelope.py) enumerates all 1,472 labelled valid n=8 reference colourings above port state `001212`. It independently DFS-enumerates all internal full colourings for each graph and checks the linear conditions on every difference:

| `dim(Z_s)` | Actual `|Fibre(s)|` | Configurations |
| ---: | ---: | ---: |
| 0 | 1 | 1,072 |
| 1 | 1 | 240 |
| 1 | 2 | 160 |

No general polynomial `SolveLinearCubicXSAT` follows because (a) a proper reference colouring need not be available, and (b) `d_s` can grow with graph size. The dimension `d_s` is a parameterized upper-envelope, **not** a complete solver.

## What remains to prove

The current abstract `F22` model allows arbitrary fibre permutations satisfying the 15 commutation squares. Physical realizations obey the stronger pointwise `F2^2` circulation constraint, and all their colour-specific matching/path updates share one fixed cubic incidence structure. However these conditions do not yet exclude all three nonempty bit fibres `100,010,001`.

Next test: select 22 basis loops for the forced boundary complex, lift them on actual coloured simple sixpoles when defined, and record their circulation displacement vectors in fixed cycle-space coordinates. Find a **universal cross-colour identity** that cannot be realised by any such physical flow and that is required by every globally GOOD-only exact-one sixpole, or exhibit a physical exact-one sixpole with complete 108-state relation. Do NOT confuse a single partial nontrivial lift with a full GOOD-only covering representation.

## Truth gates

- `PHYSICAL_N8_NONTRIVIAL_5LOOP`: finite explicit witness; CHECKED independently.
- `N8_1472_CENSUS_160_32`: finite enumerative result; independent local replay.
- `ALL_N_SAME_BOUNDARY_GF2xGF2_CIRCULATION`: proved elementary consequence of Kirchhoff parity.
- `UNIVERSAL_EXACTONE_6POLE_NO_GO`: OPEN.
- `UNBOUNDED_NATIVE_PC_DEGREE`: OPEN.
- `SolveLinearCubicXSAT`: NOT_CONSTRUCTED.
- `P_VS_NP`: OPEN.
- GitHub Actions test conclusion: **UNVERIFIED** until explicit successful job evidence is retrieved.

### Literature

Fiol & Vilaltella, *Some Results on the Structure of Multipoles in the Study of Snarks*, EJC 22(1), 2015: https://doi.org/10.37236/3629.

Related nowhere-zero Klein-four flow formulation and parity lemma: https://www.combinatorics.org/ojs/index.php/eljc/article/download/v31i2p6/pdf/.
