# JANUS Fundamentum — BABEL-17 final frozen-instance checkpoint

## Seed3: exact degree-4 linear Fourier ideal identity

**Scientific status: EXACT FROZEN INSTANCE PASS.** An independently replayed 185,122-term *integer* Fourier identity with positive 776-digit normalization exists for the legal connected unsatisfiable SCL-252 seed3 double cover of SCL126_flip68.

This is a proof in the historic JANUS *linear character-multiplier/ideal* formalism, not a positive-semidefinite sum-of-squares/Gram certificate by default. It has no universal P-vs-NP authority.

### Full independent CI evidence

- Full identity and independent all-frequency replay: [GitHub Actions #39511525819](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39511525819), complete **success** at commit `8b30c3f82ea97fba1407afcc01b3a300da7ed464`.
- Explicit compressed identity SHA-256: `296c8d3af247ffee779ea6e4d8f212b459da8c42c26163fe03f36ed5c9388554`.
- CI artifact `babel17-seed3-complete-integer-fourier-certificate`, ID `12305513016`, archived ZIP SHA-256 `00a83416f2332b247bd064b48d09abb61187db31f4f0f3fa2d4eb0d73fd05777`; retains until 2026-10-27.
- Exact integer correction scheme: **5609** off-graph frequencies, **483** forced zeros, **4029** singleton corrections, **7** initially invisible coordinates eliminated by **four** nonzero source-preserving syzygies, plus a **1090 × 1090** integer matrix of determinant **−1**.
- Signed graph repair: **14,851** spanning-forest edges and **4** sign-frustrating chords.
- All coefficient expansion, final equality, and independent coefficient replay passed; no floating-point or SDP relaxation was used.

### Exact instance minimum degree

[GitHub Actions #39512112508](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39512112508) checks the frozen exact BABEL-10 source degree-1 obstruction and the character-ring homomorphism from seed3 back to its 126-row source:

- **63,756** degree-1 lifted row products verified
- exactly **7,659** distinct source degree-1 products reached
- every lifted degree-1 identity would project to a forbidden degree-1 source identity

Thus minimum **character multiplier degree 2**, historically called polynomial degree **4** in JANUS, is exact for seed3.

### Governance and remaining scientific work

Three sampled SCL252 covers (seed1, seed2, seed3) now have frozen-instance minimum degree4 certificates. This proves neither a uniform degree bound over all legal SCL, a polynomial-time constructor for arbitrary instances, nor standard PSD SOS hierarchy equivalence. **P versus NP remains OPEN.**

BABEL-18 should test the rank-2 kernel covers seed0 and seed4; the one-extra-character paired transfer from seeds1–3 must not be assumed to apply. Preserve older negative results and frozen gates without modifying `main`.
