# BABEL-21: full source syzygy frontier

**Status: new modular dependencies, exact rational witnesses pending.** This is not an SOS4 positive or negative proof.

BABEL-20 left one unspanned source-syzygy response direction for SCL126_flip16 cover seed20 and five for seed37. We reconstructed the exact rational ker(T) cokernels and all previously tested Koszul and identical-column syzygies before trying the full source matrix.

The source has 128,013 distinct degree2 Fourier generator signatures (142,509 further repeated occurrences). Exact source-cokernel response support is only 18 original coefficient positions for seed20 and 90 for seed37. Modular sparse elimination modulo 65,521 identified a *new dependency with nonzero cokernel response* for both. Seed20: after 38,872 unique source generators, source row78, multiplier13427, response -1 mod65521. Seed37: after 21,551, source row71, multiplier1225, response (1,0,0,0,0). These are candidate dependencies only, not yet independently checked Q-syzygies.

Evidence: [initial CI #39653891041](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39653891041), [extended source scan #39654323598](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39654323598). Bounded exact-Q source-rowspace search [#39655303487](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39655303487) did not locate a sparse representation within 781 frequencies for seed20 or 900 for seed37; **this is not source-rowspace nonmembership**.

Exact rational recovery scripts and workflows are committed: [seed37 #39654709047](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39654709047), [seed20 #39655495155](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39655495155), and [modular-DAG reconstruction #39655878473](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39655878473). Only a direct rational A*z=0 identity with exact nonzero response can upgrade the scientific gate.

A genuine negative full-M2 witness must give rational H with H^T M2=0 for **all** legal degree2 Fourier generator columns and H(e0) nonzero. The current anti-sector cokernel h has h(e0)=0. Missing syzygies in the transfer method cannot be called a full degree4 lower bound.

Fourier/ideal certificate degree is **not** automatically standard PSD SOS/Gram degree. No general polynomial-time SolveLinearCubicXSAT, no P=NP. Main remains unchanged.

## Addendum: independently generated exact Q relations for seed37

The [full exact-Q elimination #39654709047](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39654709047) successfully reconstructed an **exact rational source Fourier syzygy with 2,502 nonzero coefficients**, for which the complete base Fourier frequency vector is zero and the cover anti-cokernel response is nonzero. Hence independent source-syzygy response rank rises **6 to 7 of 11**. Four response directions are not yet accounted for.

An algorithmically separate [modular DAG then bounded rational reconstruction #39655878473](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39655878473) constructed a **394-term** exact rational source syzygy for seed37; its source Fourier equality and nonzero new cover response were verified over Q. These do not increase rank beyond 7/11 because they lie in the same one-dimensional new response direction.

The same bounded reconstruction tested two seed20 modular dependencies but did **not** yield an exact Q source syzygy; seed20 status stays **OPEN**. A longer rational-elimination CI is separately running, and must pass before any mathematical promotion.

An independent all-term replay script `experiments/babel21/independent_source_verify.py` is now committed, with [GitHub Actions #39656991020](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39656991020) as the independent verification gate. Do not claim its result until its jobs finish.


## Independently verified BABEL-21 closure of seed 20 — full rational correction space

The longer exact Q elimination [#39655495155](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39655495155) completed successfully. It reconstructed a **2484-multiplier rational source syzygy** with identically zero Fourier coefficients in the original SCL126_flip16 system and nonzero response on the sole residual cover anti-sector direction.

The *separate* independent checker in [CI #39666021816](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39666021816) downloaded the completed proof artifact, rebuilt the exact ker(T) rational cokernel and known Koszul/equal-column responses, re-expanded all 2484 source Fourier terms, and independently recomputed its lifted cover-cokernel pairing. **PASS**. This raises the full source syzygy response rank for seed20 from 8 to 9 of 9; the complete rational correction map is onto. Together with an exact source certificate, this proves existence of a degree-2 multiplier identity on that frozen legal SCL252 cover. The expanded full cover coefficient list is not yet persisted.

Seed37's separate independent check passed for its 2502-term source syzygy, but its source response rank is only **7 of 11**, leaving four directions unresolved. A shorter 394-term exact relation was independently replayed in earlier [#39656991020](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39656991020); it spans the same new response direction. No full rank claim for seed37 is warranted.

A deeper seed37 source-elimination research CI tests a larger set of distinct source generator signatures and independently verifies only exact rational syzygies. A modular hit alone does not change scientific gates. No full rational dual of the entire M2 with nonzero target pairing has been demonstrated. No universal polynomial-time result or P=NP proof.
