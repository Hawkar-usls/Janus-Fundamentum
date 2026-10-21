# BABEL-19 diverse-source SCL covers: exact rank mechanisms and seed16 full certificate

**Research-only Draft PR #542.** All claims are restricted to explicitly frozen graph incidences; no generic SAT or P-vs-NP result.

### Nine new exact negative controls

Three distinct source matrices (SCL63, SCL126_flip16, SCL126_flip68), with signings seeds 6, 11, 19 each, yielded **nine legal connected UNSAT covers**. All GF(2) kernel states were enumerated exactly for each. [Independent CI #39592294651](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39592294651) success; incident SHA-256 digests preserved by its manifest. In additional sweeps of 64 signing seeds per source, rank-two kernel examples: 20, 13 and 10 respectively.

### Three new rank-two covers

| Base / signing | Independent Q rank of B(ker T) | Conclusion |
|---|---|---|
| SCL63, seed7 | 29,303 / 29,303 | full rational anti-sector rank |
| SCL126_flip16, seed5 | 55,667 / 55,667 | full rational anti-sector rank |
| SCL126_flip68, seed16 | 60,374 / 60,375 | exact one-dimensional ker(T) cokernel |

[Cross-source verifier #39593597827](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39593597827) independently replayed each selected source-zero Fourier column. The rank-one deficit seed16 was repeated for finite fields 65521, 100003 and 100019, then **confirmed over Q** using a two-coordinate exact rational left-kernel at Fourier indices 96978, 113350, each coefficient +1. Every one of 1,807,092 ker(T) column images pairs to zero. [Rational cokernel CI #39594162668](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39594162668).

### Why seed16 nevertheless has a degree4 certificate

The source defect-polynomial Koszul identity between base rows r=37 and s=58, shifted by t=8832, is exactly zero on the base and uses only legal degree-2 multipliers. Its lifted image pairs to +1 against the two-coordinate cokernel. It supplies the sole missing direction and raises the full correction rank to 60,375 over Q. [Independent Koszul verification #39594725489](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39594725489).

After adding that single syzygy as a final pivot, the exact rational DAG solver recovered an **explicit 224,467-term integer Fourier certificate**, positive 775-digit constant, with 58,987 nonzero integer correction values and independent verification of *all* Fourier frequencies. [Successful full replay #39595184757](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39595184757). Full gzip certificate SHA-256: `2cf6e9178323e08c73fd60eda31437311cb3f243d01450db4319f4e96b13f730`.

The strong *sufficient* criterion `B(ker T)=ker Pi` is therefore **not universal**, even among these new legal covers. The more complete criterion `B(ker T)+BS(ker A)` captures the source syzygy that repairs this specific hole.

### Scientific boundaries

All historical degrees refer to the JANUS Fourier/ideal multiplier system. These exact data do **not** establish standard PSD-SOS equivalence or uniform polynomial-time `SolveLinearCubicXSAT` for every legal instance; P vs NP remains OPEN. No main merges or global proof authority updates.
