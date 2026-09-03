# JANUS TRUMP R44AU — Fixed additive Davis-Putnam budget meta-barrier

Fix a constant `K>=0` once and for all. A variable with polarity counts `(p,q)` is eligible for exact Davis-Putnam elimination when

`p*q <= p+q+K`.

One elimination removes `p+q` pivot clauses and creates at most `p*q` non-tautological resolvents, so it increases the clause count by at most `K`. Since at most `n_0` variables can be eliminated, the clause count throughout the legal phase is at most `m_0+K n_0`. With clause length at most `n_0`, the live literal state is polynomial for every fixed `K`; the phase also has polynomial charged work.

This entire constant-budget ladder nevertheless fails universal progress. Darmann and Döcker (Discrete Applied Mathematics 292, 2021, DOI `10.1016/j.dam.2020.12.010`) prove that for every fixed `k>=2`, Monotone 3-Sat remains NP-complete when every variable occurs exactly `k` times positively and `k` times negatively.

For any fixed `K`, choose a fixed `k` with

`k^2 > 2k+K`.

Then every variable in Monotone 3-Sat-(k,k) violates the eligibility inequality. The reducer has no legal first move on the entire class.

Therefore increasing the allowed clause debt by another fixed constant can never be promoted as a new universal route.

Seals:

- `K=0` is R44AT.
- `FOR_EVERY_FIXED_K: POLY_DP_PHASE != UNIVERSAL_PROGRESS`.
- `INCREMENTING_FIXED_K != NEW_MACHINE`.
- `NP_COMPLETE_FIXED_POINT_CLASS != P_NE_NP`.
- `P_VS_NP=OPEN`.
