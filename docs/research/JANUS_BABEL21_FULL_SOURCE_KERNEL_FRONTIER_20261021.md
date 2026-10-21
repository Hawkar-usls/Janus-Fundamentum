# BABEL-21: full source syzygy frontier

**Status: new modular dependencies, exact rational witnesses pending.** This is not an SOS4 positive or negative proof.

BABEL-20 left one unspanned source-syzygy response direction for SCL126_flip16 cover seed20 and five for seed37. We reconstructed the exact rational ker(T) cokernels and all previously tested Koszul and identical-column syzygies before trying the full source matrix.

The source has 128,013 distinct degree2 Fourier generator signatures (142,509 further repeated occurrences). Exact source-cokernel response support is only 18 original coefficient positions for seed20 and 90 for seed37. Modular sparse elimination modulo 65,521 identified a *new dependency with nonzero cokernel response* for both. Seed20: after 38,872 unique source generators, source row78, multiplier13427, response -1 mod65521. Seed37: after 21,551, source row71, multiplier1225, response (1,0,0,0,0). These are candidate dependencies only, not yet independently checked Q-syzygies.

Evidence: [initial CI #39653891041](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39653891041), [extended source scan #39654323598](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39654323598). Bounded exact-Q source-rowspace search [#39655303487](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39655303487) did not locate a sparse representation within 781 frequencies for seed20 or 900 for seed37; **this is not source-rowspace nonmembership**.

Exact rational recovery scripts and workflows are committed: [seed37 #39654709047](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39654709047), [seed20 #39655495155](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39655495155), and [modular-DAG reconstruction #39655878473](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39655878473). Only a direct rational A*z=0 identity with exact nonzero response can upgrade the scientific gate.

A genuine negative full-M2 witness must give rational H with H^T M2=0 for **all** legal degree2 Fourier generator columns and H(e0) nonzero. The current anti-sector cokernel h has h(e0)=0. Missing syzygies in the transfer method cannot be called a full degree4 lower bound.

Fourier/ideal certificate degree is **not** automatically standard PSD SOS/Gram degree. No general polynomial-time SolveLinearCubicXSAT, no P=NP. Main remains unchanged.
