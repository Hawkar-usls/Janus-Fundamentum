# BABEL-19 · explicit exact Fourier certificates for SCL252 seeds 0 and 4

**Scientific PASS is scoped to two frozen exact instances only.** No P=NP proof, no generic PSD SOS/Gram claim, and no universal polynomial-time SAT solver.

The BABEL-18B 65,521-modular full-rank witnesses implied rational coefficient existence for seeds 0 and 4 but did not supply coefficients. BABEL-19 recovers them by an affine-substitution DAG over actual rational numbers, rather than CRT-guessing, and checks the complete degree-2 Fourier multiplier identity over the integers. The independent replay loads the persisted gzip certificate and recomputes all frequencies from the original legal SCL252 row matrix.

| Metric | Seed 0 | Seed 4 |
| --- | ---: | ---: |
| Explicit nonzero integer coefficients | 224,350 | 231,873 |
| Nonzero sparse pivot corrections | 59,457 | 59,227 |
| Nonintegral corrections | 0 | 0 |
| Positive normalization digits | 775 | 775 |
| Full and independent integer Fourier replay | PASS | PASS |
| GitHub Actions run | [39591960890](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39591960890) | [39592389057](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39592389057) |

SHA256 expanded gzip seed0: `201853d4a5ffc055613b01aea42a1f4338ea259b68f53b393f9058fd9684c9db`; seed4: `39b5429c2a2511ab0813d56fc4db06e56a5d47fbb9abc1cb3218f01a17bdf353`.

Full certificates are preserved as GitHub Actions artifacts for seven days; the permanent PR stores the complete *source algorithm*, immutable checkpoint, expected digests and independent verifier. Artifacts expire October 28, 2026. Rebuild them from the frozen source and CI.

The lower-degree obstruction for both seeds was independently certified in BABEL-18. Therefore these frozen covers have **minimum historical JANUS Fourier polynomial degree 4**. This terminology does not establish a positive-semidefinite SOS hierarchy equivalence.

Additional experiments are tracked separately in [BABEL-19 diverse-cover Draft PR #542](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/542); do not promote claims about new covers until their independent tests complete.

**Governance:** No mutation to `main`, previous negative gates untouched, scientific authority frozen at individual-instance scope. Generic polynomial bound and `SolveLinearCubicXSAT` remain OPEN; P vs NP OPEN.
