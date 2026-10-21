# JANUS Fundamentum — BABEL-18B

## Exact rational existence proof for degree-2 Fourier multipliers on SCL252 seeds 0 and 4

**Scientific verdict: EXACT RATIONAL EXISTENCE PASS, with independently verified nonzero modular minors.** This is an exact existential proof, not an expanded list of rational coefficients, and not standard PSD SOS equivalence.

The frozen legal connected instances `SCL252_two_cover_seed0` and `seed4` have a GF(2) parity-kernel dimension of 17 and two additional characters relative to source `SCL126_flip68`. The BABEL-17 one-extra-character transfer cannot be applied directly.

### Algebraic identity and exact proof

Let (A) be the integer base Fourier multiplier matrix, (B) the corresponding 252-row cover matrix, (T) the surjective coefficient map that sums lifted degree-2 row-multiplier coefficients over the source rows/fibres, and (Pi) the character-frequency restriction that sums all cover frequencies over their 4-element kernel-group orbits.

The integral identity (Pi B = A T) holds for every permitted generator. Each source degree-2 character admits a lifted degree-2 representative, so (T) is surjective.

A rational source certificate (Ax=D e_0), (D>0), is independently confirmed by the earlier source Krylov exact integer replay. Choose (y) with (Ty=x). Then (r=De_0-By) satisfies (Pi r=0). Therefore an exact rational lifted certificate exists whenever
[
 B(ker T)=ker(Pi)cap mathbb Q^{D_3(	ext{cover})}.
]

The full (ker T) has an explicit generating set, consisting of all differences between lifted row-multiplier generators in each source coefficient fibre. Enumerate every generator exactly: `2*n*|Q_lift|-n*|Q_source|`. Each image has at most 8 signed integer Fourier terms. Representatives of the image live in an antisymmetric coordinate system of dimension `|D3(cover)|-|D3(source)|`.

### Independent verified numerical proof data

| Attribute | Seed 0 | Seed 4 |
|---|---:|---:|
| All legal ker(T) generator differences enumerated | 1,864,800 | 1,852,956 |
| Antisymmetric coordinates | 60,849 | 60,878 |
| Rank from exact nonzero modular minor mod 65,521 | **60,849** | **60,878** |
| Independent pivot generator witnesses | 60,849 | 60,878 |
| Initial short-column rank lower bound | 40,525 | 39,213 |
| Saturation passes to complete rank | 1 | 2 |
| Proven rational anti-sector cokernel dimension | **0** | **0** |
| Full explicit rational coefficient identity stored | no | no |

The proof uses **exact integer generators and finite-field Gaussian eliminations**, not floating-point optimization. A full-rank matrix modulo a prime has a nonzero integer minor and thus the same full row rank over (mathbb Q). The independent witness checker recomputes each selected integer column from the frozen legal source, verifies (Pi)-zero, and inserts each into a separate finite-field rank structure, refusing dependent pivots.

**[Independent GitHub CI #39520138897](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39520138897): PASS.** Proof archive `babel18b-independent-exact-rational-antisector-rank`, GitHub artifact ID `12311077255` and archive SHA-256 `f965a4f0fdcda21f4bc6db6c0b8d20f2449a122d31e938cd52f622f534444756` (available until 2026-10-28).

SHA-256 of pivot witness for seed 0: `005b8946333319bc78897e99aa499ac9eada418dcd0369dade11e17852cd7f14`.
SHA-256 of pivot witness for seed 4: `e6497da09cd97b050c7805bec978d120c667212a6fd9dfc176526ae7a3db2adb`.

### Scientific verdict and limitations

The source obstruction previously transferred to both seeds rules out degree-1 Fourier multipliers. Combined with the new exact degree-2 rational existence proof, the **minimum historical JANUS polynomial degree equals 4 for both seeds**.

Together with independently verified seeds 1, 2, 3, all *five frozen SCL252 covers* have historical minimum degree 4. This is a finite-family claim only.

This proof uses a stronger sufficient condition `B(ker T)=ker Pi`, so explicit construction of the full `ker A` syzygy basis is unnecessary **for this positive result**. The identity `ker(AT)/ker T ≅ ker A` remains valid, but no such basis was enumerated in this Gate. The complete rational coefficient vector for each full SOS4 identity also has not been printed; only rational existence is certified via invertible modular minors.

**Not proved:** equivalence to generic PSD SOS/Gram certificates; a universal SOS degree bound; polynomial-time `SolveLinearCubicXSAT` for all legal SCL; P=NP. The problem (P) versus (NP) remains OPEN.

Follow-up: derive explicit rational coefficient recovery from the 60k selected pivots and test whether the full-rank transfer condition holds for more general covers or can provably fail.
