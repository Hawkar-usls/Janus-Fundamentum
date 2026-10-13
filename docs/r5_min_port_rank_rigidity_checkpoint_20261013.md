# R5 — All-size minimum-port-rank rigidity and constructive forbidden certificate

**Date:** 2026-10-13  
**Scientific scope:** cubic sixpoles with six distinct physical semiedge roots, correct 3-edge-colourings, three fixed ordered equality pairs.  
**Executable:** [r5_kempe_min_port_rank_fibre_obstruction.py](../experiments/r5_kempe_min_port_rank_fibre_obstruction.py).  
**Prior dependencies:** [Kempe saturation and fibre-uniformity](r5_kempe_sixpole_saturation_or_forbidden_proof_20261013.md); [fixed-boundary Klein-four circulation envelopes](r5_crosscolour_fiveloop_flow_checkpoint_20261013.md).

## Theorem 1 — uniform fibre bound from all 36 boundary ranks

Let `M` be any connected simple cubic sixpole with six **distinct ordered physical ports**, all incident to distinct interior vertices, and fix three ordered port pairs. Encode their colour-equality bits as `b(s)` for physical tuple `s`. Put `GOOD={100,010,001}`. The theorem assumes the **global** promise `Bits(M) subset GOOD`. Let `b in Bits(M)`.

The previously established forced Kempe-path bijections between the 36 even-parity physical tuples of this one truth bit show that all 36 corresponding internal-colouring fibres are nonempty and have the same cardinality `m_b`.

For every parity-legal physical tuple `s` of bit `b`, independently of existence of a colouring, form the vector space `Z_s` of ordinary-edge `F2^2` labels satisfying zero divergence at every vertex and the root constraints `D_e in {0,s_i}` (the difference on the two internal edges at root i is equal). `Z_s` has a polynomial-size binary matrix; `d_s = dim_F2 Z_s` is polynomial-time computable by Gaussian elimination from **only** the uncoloured graph and prescribed port values.

For any fixed full reference colouring `c_s` extending `s`, the map `c -> c XOR c_s` injects the full-colouring fibre at `s` into `Z_s`. Thus `m_b <= 2^d_s`. Taking the minimum yields the all-size necessary condition

```
r_b(M) = min{dim_F2 Z_s : s parity-legal and b(s)=b}
m_b(M) <= 2^{r_b(M)}.
```

The minimum has only 36 terms (no exponential boundary enumeration). In particular,

```
r_b(M)=0  ==> m_b(M)=1.
```

All actual forced-loop monodromy permutations on the bit-`b` full-colouring fibre are then the identity simply because each fibre has one element. This does **not** prove the global GOOD-only promise or that a given bit occurs.

## Theorem 2 — witness-relative polynomial forbidden-state construction

Assume the same cubic, port and colour conventions, but do **NOT** assume the global GOOD-only promise.

**Input:**
- two distinct full proper 3-edge-colourings `c`, `c'` of the **same** graph, inducing exactly the same ordered physical boundary tuple `t` with `b(t) in GOOD`;
- a parity-legal ordered physical tuple `s` of the same bit with `d_s=0`.

**Output:** an explicit full proper 3-edge-colouring of the same graph whose boundary equality bits are outside GOOD, in polynomial time.

**Proof.** In the finite 36-state unique-matching graph for bit `b(t)`, select a shortest forced-boundary path `t -> s` of length <=4. Attempt to lift that exact labelled path through real bicoloured Kempe paths, independently from `c` and `c'`.

At every step, the boundary relation has exactly one matching of endpoints for which every subset of simultaneous disjoint path flips stays inside GOOD. If the actual path matching differs, enumerate all its at most `2^3` switch-subsets: one yields a full proper forbidden colouring. If it never differs, the prescribed path is liftable and reversible from the full-colouring starting state. The two distinct inputs therefore lift to **distinct** full proper colourings above `s`. But `d_s=0` permits at most one such colouring (difference-space injection), contradiction.

Thus at least one of the two lifts must encounter the forbidden branch. It consists of at most 3 earlier forced flips and 3 actual same-pair disjoint-path flips, i.e. <=6 actual Kempe path flips per witness. Gaussian elimination (36 ranks) and a constant number of graph traversals give polynomial time in `|V|+|E|`.

**Important:** This construction *uses two input proper colourings*. Producing them from an arbitrary SCL instance is not solved, and the condition `r_b=0` does not hold universally.

## Finite n8 independent replay

For fixed ordered port tuple `001212` of bit `100`, enumerate all three perfect matching colour classes on the eight labelled internal vertices, one semiedge incident to each vertex 0..5. Filter to simple, connected graphs and retain all 1,472 reference-coloured constructions. Independently enumerate the fixed-boundary full-colouring fibre and compute `r_100(M)` from 36 binary matrices (without using any colour witnesses for rank).

| `|Fibre(001212)|` | `r_100(M)` | Labelled configurations |
| ---: | ---: | ---: |
| 1 | 0 | 1104 |
| 1 | 1 | 208 |
| 2 | 0 | **112** |
| 2 | 1 | **48** |
| **Total** | | **1472** |

Hence 112 out of the 160 `|Fibre|=2` configurations have a direct constructive rank-zero forbidden-state certificate. The remaining 48 are **not certified** by this rank-only condition and may still be rejected by other checks; they are not actual Exact-One gadgets.

For both earlier explicit physical five-loop witnesses (the 4-cycle and girth-six examples), `r_100(M)=0` and the same rank-minimizing port target `001221` is one forced boundary step from input `001212`. The constructive procedure finds a genuine forbidden `111` full colouring with physical boundary `002222` after a single (1,2)-Kempe path switch in each of those two controls. Note: `002222` has equality bits `111`, not `000`.

## Limits and next gate

- Rank-minimum bound: **proved** under global GOOD-only, for all graph sizes with six distinct physical roots.
- Rank-zero plus two explicit proper-colouring witnesses => forbidden witness: **constructive polynomial theorem** for all such graph sizes.
- 1472-case partition and two small actual graph examples: **finite regression**, not universal gadget exclusion.
- No proof that every nontrivial GOOD-only candidate has rank zero. Indeed finite n8 controls include 48 two-colouring configurations with `r_100=1`, which evade this specific test.
- These statements do **not** imply native Polynomial Calculus degree growth, an all-n forbidden-state theorem, or a polynomial `SolveLinearCubicXSAT`.
- `P` vs `NP` remains **OPEN**.

**Next decisive mathematical question:** under the full GOOD-only promise, can every rank-positive residual candidate be forced to yield a forbidden state by the common internal matching geometry, using the exact affine flow constraints rather than just their dimensions? The current proof does not resolve that universal quantifier.

**CI provenance:** executable committed on research branch and included in the branch workflow. Only mark CI SUCCESS after retrieving actual job conclusion and logs.
