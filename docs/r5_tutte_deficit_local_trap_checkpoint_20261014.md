# R5: Tutte-deficit descent — exact 4-flip counterexample (2026-10-14)

## Provenance and scope
- Base repository: `Hawkar-usls/Janus-Fundamentum`, default `main` at `744a210c632aa756cd51c140a7910b2450b641c1` when the research branch was created.
- Branch: `research/r5-tutte-deficit-local-trap-20261014`.
- Executable finite verifier: `experiments/r5_tutte_deficit_local_trap_20261014.py`.
- Status: **finite exact counterexample to a specified local-descent rule**. Not a universal lower bound. Not a polynomial SAT solver. `SolveLinearCubicXSAT`: NOT CONSTRUCTED; `P vs NP`: OPEN.
- Do not mislabel the unrelated R5 issue #517 (cross-colour sixpole monodromy) as this result.

## Exact equivalence underlying the test
Let `G` be a simple cubic graph. For a binary vertex labeling `s`, define
`M_s = {uv in E(G) : s(u)=s(v)}`.
Call `s` admissible if `M_s` is a matching. Put
`U_s = V(G) \\ V(M_s)` and `R_s = G[U_s]` (equivalently all remaining cross-label edges).
Define `Delta(s)=|U_s|-2nu(R_s)`, where `nu` is maximum matching size.

**Lemma.** `G` is 3-edge-colourable iff there exists an admissible `s` with `Delta(s)=0`.

*Proof.* If `s` is admissible and `Delta=0`, choose a perfect matching `N` in `R_s`. The edge set `M=M_s union N` is a perfect matching of `G`. All edges of `G-M` cross between the two `s` classes; as `G-M` is a 2-factor, every cycle is even. Alternate two colours along those cycles; colour `M` with the third. Conversely, from a proper 3-edge-colouring take one colour class `M`, and 2-colour the even cycles of `G-M` on their vertices. All edges within a class are precisely the edges of `M` (or a subset, depending on cycle phase); thus `M_s` is a matching and the remaining vertices admit a matching in `R_s`. QED.

For fixed `s`, computing `Delta(s)` is polynomial (Edmonds matching). Quantifying over all `s` is the NP-complete part; this verifier **enumerates** the `2^n` labelings only for small, fixed test fixtures.

## Frozen finite counterexample
The graph has `V={0,...,11}`, and 18 edges:

```text
(0,2) (0,6) (0,7)
(1,5) (1,10) (1,11)
(2,4) (2,9)
(3,6) (3,8) (3,11)
(4,8) (4,11)
(5,7) (5,10)
(6,9) (7,8) (9,10)
```

The executable independently checks: simple, connected, cubic, bridgeless.

Labeling bitmask `1246` (vertex `v` has colour `(1246 >> v)&1`) gives:

```text
M_s = {(1,10),(2,4),(3,6)}
U_s = {0,5,7,8,9,11}
E(R_s) = {(0,7),(5,7),(7,8)}
nu(R_s)=1
Delta(s)=6-2=4
```

**Exact Tutte-Berge obstruction:** for `W={7}`, the graph `R_s-W` has five singleton odd components. Thus
`o(R_s-W)-|W|=5-1=4=Delta(s)`.

**SAT witness:** labeling `1295` has `Delta=0`. In fact its within-class edges already give the perfect matching
`{(0,2),(1,10),(3,8),(4,11),(5,7),(6,9)}`;
the complementary 2-factor is bipartite under `1295` and hence edge-2-colourable.

**Exhaustive finite result:** among all 4096 labelings, precisely 10 are admissible: eight have `Delta=0`, two (1246 and its complement 2849) have `Delta=4`. Every other admissible labeling has Hamming distance at least five from mask 1246. In particular *no* change of 1, 2, 3 or 4 vertex bits even stays admissible. Thus no strictly decreasing `Delta` path using at most four simultaneous flips is possible from this nonzero starting point despite SAT.

This is a counterexample to the **proposed 4-local strict-descent guarantee**. It does **not** preclude a polynomial global `Improve` operation, a change of representation, leaving the admissible region between steps, or moves that flip >= 5 bits.

## Exact reproducibility
From the repository root:

```bash
python3 experiments/r5_tutte_deficit_local_trap_20261014.py
```

No third-party packages. Uses exact, cached subset DP for maximum matching on small fixtures and enumerates binary labelings. It asserts every reported count and prints a deterministic JSON certificate. Tests also include K4 (six admissible labelings, all deficiency zero), K3,3 (two, all deficiency zero), and Petersen (ten, all deficiency four). Such finite checks are **not** a proof of all-n behaviour.

## Next legitimate universal gate
Investigate a globally acting certificate-preserving transformation that, for arbitrary cubic G and admissible s with positive deficiency:
1. either outputs another admissible s' with strictly smaller deficiency,
2. or certifies **UNSAT** by a sound and complete polynomially verifiable criterion;
3. runs in a single uniform n^C bound on every input.

Any proposed mechanism must handle the frozen SAT local trap, Petersen UNSAT, connected bridgeless high-girth hard instances, and unconstrained Holyer reductions. A finite benchmark is not a universal theorem.

## Gate ledger
| Gate | Status |
|---|---|
| Exact s + matching characterization | PROVED |
| Fixed-s Tutte-Berge obstruction | PROVED |
| 12-vertex finite 4-flip trap | FINITE CERTIFICATE (replay script) |
| Universal polynomial global descent | OPEN / NOT PROVED |
| Polynomial `NonzeroSqFreeDet` | NOT CONSTRUCTED |
| Universal `SolveLinearCubicXSAT` | NOT CONSTRUCTED |
| P vs NP | OPEN |
