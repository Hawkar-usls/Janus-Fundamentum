# BABEL-21 — full-source-kernel and full-M2 gate

This Draft PR extends the frozen BABEL-20 exact Q ker(T) cokernel proof. In SCL126_flip16 seed20, 8/9 independent directions are explained by Koszul and same-column syzygies; seed37 remains 6/11. The code analyzes the other source syzygies by using the full set of **128013 unique 4-term source Fourier generator signatures** (source coefficient duplicates are verified), checking for dependencies that have nonzero pairing with the remaining exact rational cokernel functionals.

The modular source search is only a diagnostic. A valid mathematical PASS requires exact rational reconstruction of the individual source syzygy with 4-term Fourier replay. A degree4 FAIL instead requires an exact rational left-kernel witness against **every legal column** of the full cover degree2 matrix M2; rank deficits in ker(T) alone are never enough.

No proof of a uniform degree bound, standard PSD SOS equivalence, or P=NP. Branch Draft only.
