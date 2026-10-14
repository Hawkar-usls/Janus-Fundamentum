# R5: Universal Hall/imbalance decomposition and a balanced SAT Hall obstruction
**Research checkpoint, 2026-10-14** · successor to PR #518 / issue #519

## Provenance and scientific boundary
- Baseline: `research/r5-tutte-deficit-local-trap-20261014` at `ab37154c0aa56268d1ba6f14d82897df75b70cb7` (the original 12-vertex local trap and universal flip-support lemma); initial `main` at `744a210c632aa756cd51c140a7910b2450b641c1`.
- Deterministic finite exact checker: `experiments/r5_tutte_hall_decomposition_20261014.py`.
- The identities below are analytically valid for **every** finite cubic graph and admissible binary vertex labelling; the counts/examples are finite computations only.
- Uniform polynomial `NonzeroSqFreeDet` and `SolveLinearCubicXSAT`: **NOT CONSTRUCTED**. `P vs NP`: **OPEN**.

## Theorem A: exact decomposition of Tutte deficit into imbalance and Hall obstruction

Let `G=(V,E)` be a simple cubic graph and `s:V->{0,1}` an admissible labelling: monochromatic edges `M_s` form a matching. Set `V_i=s^{-1}(i)`, `m_i=|M_s cap E(G[V_i])|`, `U_i=V_i\\V(M_s)`, and `R_s=G[U_0 cup U_1]`. Since no edge inside either `U_i` is monochromatic, `R_s` is bipartite with sides `U_0,U_1`.

Choose the smaller side `U_min`, and set
`h(s)=max_{X subseteq U_min} (|X|-|N_R(X)|)`,
which is nonnegative because the empty set is allowed. Define
`Delta(s)=|U_0|+|U_1|-2 nu(R_s)` where `nu` denotes maximum matching size.

**Universal identity:**
```text
Delta(s) = 2 * abs(|V_0|-|V_1|) + 2 * h(s).
```

*Proof.* Let `c` be the number of bichromatic edges. Cubicity gives
`3|V_i|=2m_i+c`, whence `|U_i|=|V_i|-2m_i=c-2|V_i|`, so
`abs(|U_0|-|U_1|)=2abs(|V_0|-|V_1|)`.
Hall's theorem (the matching deficiency equality in bipartite graphs)
gives `nu(R_s)=|U_min|-h(s)`. Combining the two identities gives the theorem. QED.

**Corollaries.** Any zero-deficit `s` is necessarily balanced:
`|V_0|=|V_1|`, and has `h(s)=0`.
Conversely a balanced, admissible `s` need **not** have `Delta=0`.
Computing `h(s)` and its witness at a fixed `s` is polynomial using
bipartite matching / Hall's theorem (the verifier enumerates subsets only
for small frozen controls).
This is a diagnostic decomposition, not a polynomial algorithm for
finding a good `s`.

## Frozen Type-A SAT obstacle: n=12 is **pure imbalance**
The existing [12-vertex checkpoint](r5_tutte_deficit_local_trap_checkpoint_20261014.md)
contains a connected bridgeless cubic SAT graph, valid mask `1246`
with `|V_0|=5`, `|V_1|=7`, `Delta=4`, and **`h=0`**.
The old Tutte witness `W={7}` is valid, but the entire deficiency is
accounted for by *side imbalance*. Calling it a nontrivial balanced
Hall obstruction would be incorrect.

The smallest distance in vertex bits from `1246` to any lower-deficit
admissible mask is five (finite exhaustive certificate). Mask `1295`
is an independent SAT witness.

## Frozen Type-B SAT obstacle: n=10 is **pure Hall**, even when balanced
New connected, bridgeless, simple cubic graph with vertices `0,...,9`:
```text
(0,3) (0,5) (0,7) (1,2) (1,4)
(1,6) (2,3) (2,8) (3,5) (4,6)
(4,9) (5,8) (6,9) (7,8) (7,9)
```
For mask `551` (bit v is `(551>>v)&1`), the monochromatic matching is
```text
M_s={(0,5),(1,2),(4,6),(7,8)}.
|V_0|=|V_1|=5.
U_0={3}, U_1={9}; there is no edge 3--9.
```
Hence `nu(R_s)=0`, `Delta=2`, `h=1`.
The **Hall certificate** is `X={3}` with `N_R(X)=empty`, despite
exact balance of the original labelling.

The **same graph is SAT**: mask `779` has `Delta=0`;
mask `565` also has `Delta=0` and differs from `551`
in exactly two bits (vertices 1 and 4). This does not assert that
two-bit Hall repairs exist universally.

Exhaustive finite regression: all 1024 possible masks checked, exactly
16 admissible; `Delta=0` in 12 cases, `Delta=2` in 4 cases.
For the 12-vertex graph, all 4096 masks checked, exactly 10 admissible:
8 have `Delta=0`, 2 have `Delta=4`.
Controls include K4, K3,3 and Petersen.

This refutes the rule **"balance the labels, then Hall is automatic"**
even on connected bridgeless SAT cubic graphs.

## Theorem B: exact global flip (cut-space) law
Let `s'` be obtained from `s` by flipping a vertex set `F`. Then
```text
M_{s'} = M_s symmetric_difference delta_G(F).
```
This holds even if one or both masks are inadmissible. It follows
because equality of endpoint bits toggles iff exactly one endpoint is
flipped. Consequently, admissibility of `s'` is equivalent to
`M_s symmetric_difference delta_G(F)` being a matching.

For each vertex `v`, let
`d_s(v)=|M_s cap delta(v)|`, `b_F(v)` be the number of incident edges
crossing the cut `delta(F)`, and `a_F(v)` the number of those cut edges
which are already monochromatic in `s`. The new monochromatic degree is
```text
d_{s'}(v) = d_s(v) + b_F(v) - 2*a_F(v).
```
Hence `s'` is admissible iff this quantity is <=1 for every v.
These necessary-and-sufficient equations hold for **arbitrarily large,
simultaneous** flips; no locality assumption.

Corollary: `M_s symmetric_difference M_{s'}` has even intersection
with every cycle of G (because it is a cut). This is an exact GF(2)
cycle-space constraint on any global candidate update.

## Next universal gate
Design an **explicit deterministic polynomial-time** rule that, from
any admissible `s` on any connected cubic graph, either yields `s'`
with smaller `Delta` whenever G is SAT, or correctly decides UNSAT.
A candidate may use both the imbalance and Hall witnesses; it must
honour the cut-switch law, preserve admissibility, and be analyzed for
all-n runtime. Pass both different SAT obstacles above and Petersen
UNSAT. Merely producing witnesses to an individual Hall failure does
not settle the existential selection over all s.

Note that the admissible balanced partition (2-bisection) problem is
studied separately in the snark literature; an argument assuming all
bridgeless cubics admit such a partition cannot silently use a conjecture.

## Gate table
| Gate | Status |
|---|---|
| Hall/imbalance identity | PROVED (all n) |
| Global cut-switch identity | PROVED (all n) |
| Connected SAT n=10 balanced Hall obstruction | FINITE EXACT CERTIFICATE |
| Connected SAT n=12 imbalance-only trap | FINITE EXACT CERTIFICATE |
| Fixed-s Hall witness generation | POLYNOMIAL (bipartite matching) |
| Joint s selection + polynomial global improvement | OPEN |
| Polynomial NonzeroSqFreeDet / SolveLinearCubicXSAT | NOT CONSTRUCTED |
| P vs NP | OPEN |

## Replay
```bash
python3 experiments/r5_tutte_deficit_local_trap_20261014.py
python3 experiments/r5_tutte_hall_decomposition_20261014.py
```
No third-party dependencies. On every finite admissible label the
new verifier checks the exact identity against an independent
subset-matching computation, and separately exhausts the cut-switch
identity over all 2^n flip sets for the two frozen starts.
