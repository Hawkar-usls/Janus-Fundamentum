# BABEL-19 — explicit rational coefficient recovery

This research-only gate reconstructs an **explicit degree-2 Fourier multiplier identity** on SCL252 seed0/seed4 from the exact nonzero finite-field minors proved in BABEL-18B. The finite-field rank is used to SELECT an invertible set of legal columns, **not** to guess their rational coefficient values. A new affine-substitution DAG solves the selected sparse integer linear system exactly with Python fractions, and a separate independent Fourier expansion must verify the result before PASS is claimed.

Only a successful full all-frequency replay authorizes `EXPLICIT_RATIONAL_CERTIFICATE_PASS`; a modular-only result is still the earlier existential PASS. No claim about standard PSD SOS or universal polynomial-time SCL.
