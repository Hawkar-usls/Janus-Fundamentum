# BABEL-18 — exact geometry of the rank-2 extra-character covers

**Verified seed0/seed4 geometry and minimum-degree lower bound only.** No degree-4 certificate for either seed has yet been built.

### Independent cloud evidence

- [Rank-2 cover geometry CI #39512846507](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39512846507): exact restriction homomorphism, valid connected legal 252-row cover, source GF(2) nullity 15, cover nullity 17, two-dimensional extra-character kernel, and degree-2 lift-fiber census.
- [Degree1 exclusion and rank-2 orbit CI #39513075749](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39513075749): exact source left-kernel witness, 63,756 projected degree1 lifted generators for each seed, and all 7,659 distinct source degree1 generators, proving no degree1 multiplier identity for either cover.

| Quantity | Seed 0 | Seed 4 |
|---|---:|---:|
| Additional kernel generators | 259, 1552 | 784, 32808 |
| Kernel group size | 4 | 4 |
| Degree-2 legal lift characters | 8,604 | 8,557 |
| Degree-2 source characters with no lift | 0 | 0 |
| Source character fibers of size 1 / 2 / 3 / 4 | 6 / 460 / 90 / 1852 | 0 / 478 / 119 / 1811 |
| Degree-3 lifted unique characters | 81,313 | 81,342 |
| Degree-3 quotient orbits | 20,464 | 20,464 |
| Degree-3 orbit sizes 2 / 3 / 4 | 260 / 23 / 20,181 | 250 / 14 / 20,200 |
| Minimum historic JANUS polynomial degree | at least 4 | at least 4 |

The one-extra-character BABEL-17 strategy cannot be copied directly: the quotient has four-element character orbits and **three nontrivial anti-sectors**, not one. Incomplete degree-2 fibers must be handled without assuming missing multipliers exist.

### Next mathematical gate

Construct an exact 3-component anti-sector correction map on each four-element orbit, explicitly respecting which of its four degree-2 multipliers are legal. Seek a source-syzygy-compatible integer lift and verify *every* Fourier frequency independently. Until then, **minimum degree = 4 is not established** for seeds 0 and 4: only the lower bound is proven.

Neither a standard positive-semidefinite SOS/Gram theorem nor a universal polynomial `SolveLinearCubicXSAT` or P=NP statement follows. All earlier seed1–3 exact local positive gates and seed3 method-specific negative gates remain unchanged.
